"""
Flask backend for real-time number plate detection system with MongoDB.

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
from flask_socketio import SocketIO, emit
from flask_pymongo import PyMongo
from datetime import datetime
from bson import ObjectId
import os
import cv2
import numpy as np
import base64
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.models_mongodb import DetectionMongo
from backend.detector import PlateDetector

# ------------------------------------------------------
# Flask & MongoDB setup
# ------------------------------------------------------
app = Flask(__name__)
app.config.update(
    MONGO_URI=os.getenv(
        "MONGO_URI",
        "mongodb+srv://mukherjeenilima705_db_user:RkN3R5EwgJTpk9gJ@numberplatedetection.wcwef31.mongodb.net/numberplate_detection"
        "?retryWrites=true&w=majority&appName=NumberPlateDetection",
    ),
    UPLOAD_FOLDER="uploads",
    MAX_CONTENT_LENGTH=50 * 1024 * 1024,  # 50MB
    SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"),
)

CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])
mongo = PyMongo(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ------------------------------------------------------
# YOLOv7 detector initialization
# ------------------------------------------------------
detector = PlateDetector(
    yolov7_weights=os.getenv("MODEL_WEIGHTS", "models/yolov7.pt"),
    device=os.getenv("DEVICE", "0"),
    conf_threshold=float(os.getenv("CONF_THRESHOLD", "0.25")),
)

# Ensure upload folder exists
upload_dir = Path(app.config["UPLOAD_FOLDER"])
upload_dir.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------
# Health Check
# ------------------------------------------------------
@app.route("/api/health", methods=["GET"])
def health_check():
    try:
        mongo.db.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return jsonify(
        {
            "status": "healthy",
            "model_loaded": getattr(detector, "model", None) is not None,
            "database": db_status,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


# ------------------------------------------------------
# Single Image Detection
# ------------------------------------------------------
@app.route("/api/detect", methods=["POST"])
def detect_plate():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    camera_id = request.form.get("camera_id", "default")

    if not file or not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    img_bytes = file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return jsonify({"error": "Invalid image format"}), 400

    results = detector.detect(img) or []
    detection_records = []

    for result in results:
        plate_crop = result.get("plate_crop")
        if plate_crop is None:
            continue

        ok, buffer = cv2.imencode(".jpg", plate_crop)
        if not ok:
            continue
        plate_img_b64 = base64.b64encode(buffer).decode("utf-8")
        
        plate_text = result.get("plate_text", "UNKNOWN")
        detection_doc = DetectionMongo.create(
            plate_number=plate_text,
            confidence=float(result.get("confidence", 0.0)),
            camera_id=camera_id,
            bbox=result.get("bbox", [0, 0, 0, 0]),
            plate_image=plate_img_b64,
        )

        inserted = mongo.db.detections.insert_one(detection_doc)
        detection_records.append(
            {
                "id": str(inserted.inserted_id),
                "plate_number": plate_text,
                "confidence": float(result.get("confidence", 0.0)),
                "bbox": result.get("bbox", [0, 0, 0, 0]),
                "ocr_confidence": float(result.get("ocr_confidence", 0.0)),
            }
        )

    return jsonify(
        {
            "success": True,
            "detections": detection_records,
            "count": len(detection_records),
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


# ------------------------------------------------------
# Video Detection
# ------------------------------------------------------
@app.route("/api/detect/video", methods=["POST"])
def detect_video():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    camera_id = request.form.get("camera_id", "default")
    sample_rate = int(request.form.get("sample_rate", 5))

    if not file or not file.filename:
        return jsonify({"error": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    video_path = upload_dir / filename
    file.save(str(video_path))

    cap = cv2.VideoCapture(str(video_path))
    frame_count = processed_frames = 0
    all_detections: list[str] = []

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if frame is None:
                frame_count += 1
                continue

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

                    plate_text = result.get("plate_text", "UNKNOWN")
                    detection_doc = DetectionMongo.create(
                        plate_number=plate_text,
                        confidence=float(result.get("confidence", 0.0)),
                        camera_id=camera_id,
                        bbox=result.get("bbox", [0, 0, 0, 0]),
                        plate_image=plate_img_b64,
                    )
                    mongo.db.detections.insert_one(detection_doc)
                    if plate_text:
                        all_detections.append(plate_text)
                processed_frames += 1
            frame_count += 1
    finally:
        cap.release()
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


# ------------------------------------------------------
# Detection History & CRUD
# ------------------------------------------------------
@app.route("/api/detections", methods=["GET"])
def get_detections():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)
    camera_id = request.args.get("camera_id")

    query = {}
    if camera_id:
        query["camera_id"] = camera_id

    total = mongo.db.detections.count_documents(query)
    skip = (page - 1) * per_page
    cursor = (
        mongo.db.detections.find(query)
        .sort("_id", -1)
        .skip(skip)
        .limit(per_page)
    )

    detections = [DetectionMongo.to_dict(doc) for doc in cursor]
    return jsonify(
        {
            "detections": detections,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
        }
    )


@app.route("/api/detections/<detection_id>", methods=["GET"])
def get_detection(detection_id: str):
    try:
        doc = mongo.db.detections.find_one({"_id": ObjectId(detection_id)})
        if not doc:
            return jsonify({"error": "Detection not found"}), 404
        return jsonify(DetectionMongo.to_dict(doc))
    except Exception:
        return jsonify({"error": "Invalid ID format"}), 400


@app.route("/api/detections/<detection_id>", methods=["DELETE"])
def delete_detection(detection_id: str):
    try:
        result = mongo.db.detections.delete_one({"_id": ObjectId(detection_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Detection not found"}), 404
        return jsonify({"success": True, "message": "Detection deleted"})
    except Exception:
        return jsonify({"error": "Invalid ID format"}), 400


# ------------------------------------------------------
# Stats Endpoint
# ------------------------------------------------------
@app.route("/api/stats", methods=["GET"])
def get_stats():
    total = mongo.db.detections.count_documents({})
    pipeline = [{"$group": {"_id": "$plate_number"}}, {"$count": "unique_plates"}]
    result = list(mongo.db.detections.aggregate(pipeline))
    unique_plates = result[0]["unique_plates"] if result else 0
    cameras = mongo.db.detections.distinct("camera_id")

    return jsonify(
        {
            "total_detections": total,
            "unique_plates": unique_plates,
            "cameras": cameras,
        }
    )


# ------------------------------------------------------
# WebSocket: Live Stream Frames
# ------------------------------------------------------
@socketio.on("connect")
def handle_connect():
    print("Client connected")
    emit("connection_response", {"status": "connected"})


@socketio.on("video_frame")
def handle_video_frame(data):
    try:
        frame_b64 = data.get("frame")
        if not frame_b64:
            emit("error", {"message": "No frame provided"})
            return

        img_data = base64.b64decode(frame_b64)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            emit("error", {"message": "Invalid frame data"})
            return

        results = detector.detect(img) or []
        detections = []

        for result in results:
            plate_crop = result.get("plate_crop")
            if plate_crop is None:
                continue

            ok, buffer = cv2.imencode(".jpg", plate_crop)
            if not ok:
                continue
            plate_img_b64 = base64.b64encode(buffer).decode("utf-8")
            
            plate_text = result.get("plate_text", "UNKNOWN")
            detection_doc = DetectionMongo.create(
                plate_number=plate_text,
                confidence=float(result.get("confidence", 0.0)),
                camera_id=data.get("camera_id", "live"),
                bbox=result.get("bbox", [0, 0, 0, 0]),
                plate_image=plate_img_b64,
            )

            inserted = mongo.db.detections.insert_one(detection_doc)
            detections.append(
                {
                    "id": str(inserted.inserted_id),
                    "plate_number": plate_text,
                    "confidence": float(result.get("confidence", 0.0)),
                    "bbox": result.get("bbox", [0, 0, 0, 0]),
                }
            )

        emit(
            "detection_result",
            {"detections": detections, "timestamp": datetime.utcnow().isoformat()},
        )
    except Exception as e:
        emit("error", {"message": str(e)})


# ------------------------------------------------------
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
