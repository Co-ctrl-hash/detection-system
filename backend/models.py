"""Database models for plate detection system."""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Detection(db.Model):
    """Model for storing detected license plates."""
    
    __tablename__ = 'detections'
    
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), nullable=False, index=True)
    confidence = db.Column(db.Float, nullable=False)
    camera_id = db.Column(db.String(50), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Bounding box coordinates
    bbox_x1 = db.Column(db.Integer)
    bbox_y1 = db.Column(db.Integer)
    bbox_x2 = db.Column(db.Integer)
    bbox_y2 = db.Column(db.Integer)
    
    # Store plate crop as base64 encoded image (optional)
    plate_image = db.Column(db.Text)
    
    # Additional metadata
    notes = db.Column(db.Text)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'plate_number': self.plate_number,
            'confidence': float(self.confidence),
            'camera_id': self.camera_id,
            'timestamp': self.timestamp.isoformat(),
            'bbox': {
                'x1': self.bbox_x1,
                'y1': self.bbox_y1,
                'x2': self.bbox_x2,
                'y2': self.bbox_y2
            },
            'plate_image': self.plate_image,
            'notes': self.notes
        }
    
    def __repr__(self):
        return f'<Detection {self.id}: {self.plate_number} at {self.timestamp}>'


class Camera(db.Model):
    """Model for camera configuration (optional)."""
    
    __tablename__ = 'cameras'
    
    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    rtsp_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'camera_id': self.camera_id,
            'name': self.name,
            'location': self.location,
            'rtsp_url': self.rtsp_url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Camera {self.camera_id}: {self.name}>'
