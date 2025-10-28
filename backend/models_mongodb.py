"""MongoDB models for plate detection system.

This is an alternative to models.py for MongoDB usage.
Switch between SQL and MongoDB by changing imports in app.py.
"""
from datetime import datetime
from bson import ObjectId


class DetectionMongo:
    """Model for storing detected license plates in MongoDB."""
    
    @staticmethod
    def create(plate_number, confidence, camera_id, bbox, plate_image):
        """Create a detection document."""
        return {
            'plate_number': plate_number,
            'confidence': float(confidence),
            'camera_id': camera_id,
            'bbox': {
                'x1': float(bbox[0]),
                'y1': float(bbox[1]),
                'x2': float(bbox[2]),
                'y2': float(bbox[3])
            },
            'plate_image': plate_image,
            'created_at': datetime.utcnow()
        }
    
    @staticmethod
    def to_dict(doc):
        """Convert MongoDB document to API response dict."""
        if doc is None:
            return None
        return {
            'id': str(doc['_id']),
            'plate_number': doc.get('plate_number'),
            'confidence': float(doc.get('confidence', 0)),
            'camera_id': doc.get('camera_id'),
            'bbox': doc.get('bbox', {}),
            'plate_image': doc.get('plate_image'),
            'created_at': doc.get('created_at').isoformat() if doc.get('created_at') else None
        }


class CameraMongo:
    """Model for camera configuration in MongoDB."""
    
    @staticmethod
    def create(camera_id, name, location=None, rtsp_url=None, is_active=True):
        """Create a camera document."""
        return {
            'camera_id': camera_id,
            'name': name,
            'location': location,
            'rtsp_url': rtsp_url,
            'is_active': is_active,
            'created_at': datetime.utcnow()
        }
    
    @staticmethod
    def to_dict(doc):
        """Convert MongoDB document to API response dict."""
        if doc is None:
            return None
        return {
            'id': str(doc['_id']),
            'camera_id': doc.get('camera_id'),
            'name': doc.get('name'),
            'location': doc.get('location'),
            'rtsp_url': doc.get('rtsp_url'),
            'is_active': doc.get('is_active', True),
            'created_at': doc.get('created_at').isoformat() if doc.get('created_at') else None
        }
