"""Flask backend for real-time number plate detection system with MongoDB.

This is an alternative to app.py that uses MongoDB instead of SQL databases.

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

# Initialize Flask app
app = Flask(__name__)

# MongoDB Configuration
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/plates_db')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize extensions
CORS(app, origins=['http://localhost:3000', 'http://localhost:5173'])
mongo = PyMongo(app)
socketio = SocketIO(app, cors_allowed_origins='*')

# Initialize detector
detector = PlateDetector(
    yolov7_weights=os.getenv('MODEL_WEIGHTS', 'models/yolov7.pt'),
    device=os.getenv('DEVICE', '0'),
    conf_threshold=float(os.getenv('CONF_THRESHOLD', '0.25'))
)

# Create upload folder
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        # Test MongoDB connection
        mongo.db.command('ping')
        db_status = 'connected'
    except Exception:
        db_status = 'disconnected'
    
    return jsonify({
        'status': 'healthy',
        'model_loaded': detector.model is not None,
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/detect', methods=['POST'])
def detect_plate():
    """Detect plates in uploaded image.
    
    Request:
        - file: image file (multipart/form-data)
        - camera_id: optional camera identifier
    
    Response:
        - detections: list of detected plates with bbox, confidence, text
        - detection_id: database record ID
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    camera_id = request.form.get('camera_id', 'default')
    
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    
    # Read image
    img_bytes = file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return jsonify({'error': 'Invalid image format'}), 400
    
    # Run detection
    results = detector.detect(img)
    
    # Save to MongoDB
    detection_records = []
    for result in results:
        # Save cropped plate image
        plate_img = result['plate_crop']
        _, buffer = cv2.imencode('.jpg', plate_img)
        plate_img_b64 = base64.b64encode(buffer).decode('utf-8')
        
        detection_doc = DetectionMongo.create(
            plate_number=result['plate_text'],
            confidence=result['confidence'],
            camera_id=camera_id,
            bbox=result['bbox'],
            plate_image=plate_img_b64
        )
        
        result_id = mongo.db.detections.insert_one(detection_doc).inserted_id
        
        detection_records.append({
            'id': str(result_id),
            'plate_number': result['plate_text'],
            'confidence': float(result['confidence']),
            'bbox': result['bbox'],
            'ocr_confidence': float(result['ocr_confidence'])
        })
    
    return jsonify({
        'success': True,
        'detections': detection_records,
        'count': len(results),
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/detect/video', methods=['POST'])
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
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    camera_id = request.form.get('camera_id', 'default')
    sample_rate = int(request.form.get('sample_rate', 5))
    
    # Save video temporarily (use secure filename)
    filename = secure_filename(file.filename)
    video_path = Path(app.config['UPLOAD_FOLDER']) / filename
    file.save(str(video_path))
    
    # Process video
    cap = cv2.VideoCapture(str(video_path))
    frame_count = 0
    all_detections = []
    processed_frames = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Sample frames
        if frame_count % sample_rate == 0:
            if frame is None:
                break

            results = detector.detect(frame) or []

            for result in results:
                _, buffer = cv2.imencode('.jpg', result['plate_crop'])
                plate_img_b64 = base64.b64encode(buffer).decode('utf-8')

                detection_doc = DetectionMongo.create(
                    plate_number=result['plate_text'],
                    confidence=result['confidence'],
                    camera_id=camera_id,
                    bbox=result['bbox'],
                    plate_image=plate_img_b64
                )
                
                mongo.db.detections.insert_one(detection_doc)
                all_detections.append(result['plate_text'])

            processed_frames += 1
        
        frame_count += 1
    
    cap.release()
    
    # Clean up
    video_path.unlink()
    
    return jsonify({
        'success': True,
        'total_frames': frame_count,
        'processed_frames': processed_frames,
        'detections': all_detections,
        'unique_plates': len(set(all_detections))
    })


@app.route('/api/detections', methods=['GET'])
def get_detections():
    """Get detection history with pagination and filters.
    
    Query params:
        - page: page number (default: 1)
        - per_page: items per page (default: 50)
        - camera_id: filter by camera
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    camera_id = request.args.get('camera_id')
    
    # Build query
    query = {}
    if camera_id:
        query['camera_id'] = camera_id
    
    # Get total count
    total = mongo.db.detections.count_documents(query)
    
    # Get paginated results
    skip = (page - 1) * per_page
    cursor = mongo.db.detections.find(query).sort('_id', -1).skip(skip).limit(per_page)
    
    detections = [DetectionMongo.to_dict(doc) for doc in cursor]
    
    return jsonify({
        'detections': detections,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    })


@app.route('/api/detections/<detection_id>', methods=['GET'])
def get_detection(detection_id):
    """Get specific detection by ID."""
    try:
        doc = mongo.db.detections.find_one({'_id': ObjectId(detection_id)})
        if doc is None:
            return jsonify({'error': 'Detection not found'}), 404
        return jsonify(DetectionMongo.to_dict(doc))
    except Exception as e:
        return jsonify({'error': 'Invalid ID format'}), 400


@app.route('/api/detections/<detection_id>', methods=['DELETE'])
def delete_detection(detection_id):
    """Delete a detection record."""
    try:
        result = mongo.db.detections.delete_one({'_id': ObjectId(detection_id)})
        if result.deleted_count == 0:
            return jsonify({'error': 'Detection not found'}), 404
        return jsonify({'success': True, 'message': 'Detection deleted'})
    except Exception as e:
        return jsonify({'error': 'Invalid ID format'}), 400


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get detection statistics."""
    total = mongo.db.detections.count_documents({})
    
    # Get unique plates using aggregation
    pipeline = [
        {'$group': {'_id': '$plate_number'}},
        {'$count': 'unique_plates'}
    ]
    unique_result = list(mongo.db.detections.aggregate(pipeline))
    unique_plates = unique_result[0]['unique_plates'] if unique_result else 0
    
    # Get unique cameras
    cameras = mongo.db.detections.distinct('camera_id')
    
    return jsonify({
        'total_detections': total,
        'unique_plates': unique_plates,
        'cameras': cameras
    })


@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    print('Client connected')
    emit('connection_response', {'status': 'connected'})


@socketio.on('video_frame')
def handle_video_frame(data):
    """Process video frame from WebSocket.
    
    Expected data:
        - frame: base64 encoded image
        - camera_id: camera identifier
    """
    try:
        # Validate payload
        if 'frame' not in data:
            emit('error', {'message': 'No frame provided'})
            return

        # Decode frame
        img_data = base64.b64decode(data['frame'])
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Guard: ensure decode succeeded
        if img is None:
            emit('error', {'message': 'Invalid frame data'})
            return

        # Detect plates
        results = detector.detect(img) or []

        # Save to DB and emit results
        detections = []
        for result in results:
            _, buffer = cv2.imencode('.jpg', result['plate_crop'])
            plate_img_b64 = base64.b64encode(buffer).decode('utf-8')
            
            detection_doc = DetectionMongo.create(
                plate_number=result['plate_text'],
                confidence=result['confidence'],
                camera_id=data.get('camera_id', 'live'),
                bbox=result['bbox'],
                plate_image=plate_img_b64
            )
            
            result_id = mongo.db.detections.insert_one(detection_doc).inserted_id
            
            detections.append({
                'id': str(result_id),
                'plate_number': result['plate_text'],
                'confidence': float(result['confidence']),
                'bbox': result['bbox']
            })
        
        # Emit results back to client
        emit('detection_result', {
            'detections': detections,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        emit('error', {'message': str(e)})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
