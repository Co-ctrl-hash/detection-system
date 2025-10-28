"""
Flask backend for real-time number plate detection system.

Endpoints:
- POST /api/detect - Upload image/frame for detection
- POST /api/detect/video - Process video file
- GET /api/detections - Retrieve detection history
- GET /api/detections/<id> - Get specific detection
- DELETE /api/detections/<id> - Delete detection
- GET /api/stats - Get detection statistics
- WebSocket /ws/live - Real-time video stream processing
"""

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from datetime import datetime
from dotenv import load_dotenv
import os
import cv2
import numpy as np
import base64
from pathlib import Path
import sys

# Load environment variables from .env file
load_dotenv()

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.models import db, Detection
from backend.detector import PlateDetector

# Initialize Flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///plates.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max upload
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

# Initialize extensions
CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize detector
detector = PlateDetector(
    yolov7_weights=os.getenv("MODEL_WEIGHTS", "models/yolov7.pt"),
    device=os.getenv("DEVICE", "0"),
    conf_threshold=float(os.getenv("CONF_THRESHOLD", "0.25")),
)

# Create upload folder
upload_folder = Path(app.config["UPLOAD_FOLDER"])
upload_folder.mkdir(parents=True, exist_ok=True)

# Create database tables
with app.app_context():
    db.create_all()


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "model_loaded": getattr(detector, "model", None) is not None,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@app.route("/api/detect", methods=["POST"])
def detect_plate():
    """Detect plates in uploaded image.

    Request:
        - file: image file (multipart/form-data)
        - camera_id: optional camera identifier

    Response:
        - detections: list of detected plates with bbox, confidence, text
        - detection_id: database record ID
    """
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    camera_id = request.form.get("camera_id", "default")

    if not file or not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    # Read image
    img_bytes = file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return jsonify({"error": "Invalid image format"}), 400

    # Run detection (ensure list)
    results = detector.detect(img) or []

    # Save to database
    detection_records = []
    for result in results:
        # defensive access
        plate_crop = result.get("plate_crop")
        if plate_crop is None:
            continue

        # Save cropped plate image (base64)
        ok, buffer = cv2.imencode(".jpg", plate_crop)
        if not ok:
            continue
        plate_img_b64 = base64.b64encode(buffer).decode("utf-8")

        # Create Detection instance then set attributes (avoids keyword-arg mismatch)
        detection = Detection()
        # Use .get with defaults, cast to expected primitive types
        detection.plate_number = result.get("plate_text")
        detection.confidence = float(result.get("confidence", 0.0))
        detection.camera_id = camera_id
        bbox = result.get("bbox", [0, 0, 0, 0])
        try:
            detection.bbox_x1 = float(bbox[0])
            detection.bbox_y1 = float(bbox[1])
            detection.bbox_x2 = float(bbox[2])
            detection.bbox_y2 = float(bbox[3])
        except Exception:
            detection.bbox_x1 = detection.bbox_y1 = detection.bbox_x2 = detection.bbox_y2 = 0.0
        detection.plate_image = plate_img_b64

        db.session.add(detection)

        detection_records.append(
            {
                "plate_number": result.get("plate_text"),
                "confidence": float(result.get("confidence", 0.0)),
                "bbox": bbox,
                "ocr_confidence": float(result.get("ocr_confidence", 0.0)),
            }
        )

    db.session.commit()

    return jsonify(
        {
            "success": True,
            "detections": detection_records,
            "count": len(detection_records),
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@app.route("/api/detect/video", methods=["POST"])
def detect_video():
    """Process video file and detect plates in frames.

    Request:
        - file: video file
        - camera_id: optional camera identifier
        - sample_rate: frames to skip (default: 5)

    Response:
        - detections: list of all detections across frames
        - total_frames: number of frames processed
    """
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    camera_id = request.form.get("camera_id", "default")
    sample_rate = int(request.form.get("sample_rate", 5))

    if not file or not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    # Save video temporarily (use secure filename)
    filename = secure_filename(file.filename)
    video_path = upload_folder / filename
    file.save(str(video_path))

    # Process video
    cap = cv2.VideoCapture(str(video_path))
    frame_count = 0
    all_detections = []
    processed_frames = 0

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # guard in case frame is None
            if frame is None:
                frame_count += 1
                continue

            # Sample frames
            if frame_count % sample_rate == 0:
                results = detector.detect(frame) or []

                for result in results:
                    plate_crop = result.get("plate_crop")
                    if plate_crop is None:
                        continue

                    ok, buffer = cv2.imencode(".jpg", plate_crop)
                    if not ok:
                        continue
                    plate_img_b64 = base64.b64encode(buffer).decode("utf-8")

                    # Create Detection safely
                    detection = Detection()
                    detection.plate_number = result.get("plate_text")
                    detection.confidence = float(result.get("confidence", 0.0))
                    detection.camera_id = camera_id
                    bbox = result.get("bbox", [0, 0, 0, 0])
                    try:
                        detection.bbox_x1 = float(bbox[0])
                        detection.bbox_y1 = float(bbox[1])
                        detection.bbox_x2 = float(bbox[2])
                        detection.bbox_y2 = float(bbox[3])
                    except Exception:
                        detection.bbox_x1 = detection.bbox_y1 = detection.bbox_x2 = (
                            detection.bbox_y2
                        ) = 0.0
                    detection.plate_image = plate_img_b64

                    db.session.add(detection)
                    all_detections.append(result.get("plate_text"))

                processed_frames += 1

            frame_count += 1
    finally:
        cap.release()
        db.session.commit()
        # Clean up safely
        try:
            if video_path.exists():
                video_path.unlink()
        except Exception:
            pass

    return jsonify(
        {
            "success": True,
            "total_frames": frame_count,
            "processed_frames": processed_frames,
            "detections": all_detections,
            "unique_plates": len(set(all_detections)),
        }
    )


@app.route("/api/detections", methods=["GET"])
def get_detections():
    """Get detection history with pagination and filters.

    Query params:
        - page: page number (default: 1)
        - per_page: items per page (default: 50)
        - camera_id: filter by camera
        - date_from: filter by date (ISO format)
        - date_to: filter by date (ISO format)
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    camera_id = request.args.get("camera_id")

    query = Detection.query

    if camera_id:
        query = query.filter_by(camera_id=camera_id)

    # Date filters can be added here

    pagination = query.order_by(Detection.id.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify(
        {
            "detections": [d.to_dict() for d in pagination.items],
            "total": pagination.total,
            "page": page,
            "per_page": per_page,
            "pages": pagination.pages,
        }
    )


@app.route("/api/detections/<int:detection_id>", methods=["GET"])
def get_detection(detection_id):
    """Get specific detection by ID."""
    detection = Detection.query.get_or_404(detection_id)
    return jsonify(detection.to_dict())


@app.route("/api/detections/<int:detection_id>", methods=["DELETE"])
def delete_detection(detection_id):
    """Delete a detection record."""
    detection = Detection.query.get_or_404(detection_id)
    db.session.delete(detection)
    db.session.commit()
    return jsonify({"success": True, "message": "Detection deleted"})


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get detection statistics."""
    total = Detection.query.count()
    unique_plates = db.session.query(Detection.plate_number).distinct().count()
    cameras = db.session.query(Detection.camera_id).distinct().all()

    return jsonify(
        {
            "total_detections": total,
            "unique_plates": unique_plates,
            "cameras": [c[0] for c in cameras],
        }
    )


@socketio.on("connect")
def handle_connect():
    """Handle WebSocket connection."""
    print("Client connected")
    emit("connection_response", {"status": "connected"})


@socketio.on("video_frame")
def handle_video_frame(data):
    """Process video frame from WebSocket.

    Expected data:
        - frame: base64 encoded image
        - camera_id: camera identifier
    """
    try:
        # Validate payload
        frame_b64 = data.get("frame")
        if not frame_b64:
            emit("error", {"message": "No frame provided"})
            return

        # Decode frame
        img_data = base64.b64decode(frame_b64)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Guard: ensure decode succeeded
        if img is None:
            emit("error", {"message": "Invalid frame data"})
            return

        # Detect plates
        results = detector.detect(img) or []

        # Save to DB and emit results
        detections = []
        for result in results:
            plate_crop = result.get("plate_crop")
            if plate_crop is None:
                continue

            ok, buffer = cv2.imencode(".jpg", plate_crop)
            if not ok:
                continue
            plate_img_b64 = base64.b64encode(buffer).decode("utf-8")

            detection = Detection()
            detection.plate_number = result.get("plate_text")
            detection.confidence = float(result.get("confidence", 0.0))
            detection.camera_id = data.get("camera_id", "live")
            bbox = result.get("bbox", [0, 0, 0, 0])
            try:
                detection.bbox_x1 = float(bbox[0])
                detection.bbox_y1 = float(bbox[1])
                detection.bbox_x2 = float(bbox[2])
                detection.bbox_y2 = float(bbox[3])
            except Exception:
                detection.bbox_x1 = detection.bbox_y1 = detection.bbox_x2 = detection.bbox_y2 = 0.0
            detection.plate_image = plate_img_b64

            db.session.add(detection)

            detections.append(
                {
                    "plate_number": result.get("plate_text"),
                    "confidence": float(result.get("confidence", 0.0)),
                    "bbox": bbox,
                }
            )

        db.session.commit()

        # Emit results back to client
        emit(
            "detection_result",
            {"detections": detections, "timestamp": datetime.utcnow().isoformat()},
        )

    except Exception as e:
        emit("error", {"message": str(e)})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
