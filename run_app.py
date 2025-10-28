"""Simple Flask app runner - just run the server without extra complexity"""
import os
os.environ.setdefault('FLASK_ENV', 'development')

print("🚀 Starting Flask server...")
print("Loading YOLOv7 model (this takes ~20 seconds on first run)...")

from backend.app import app, socketio

print("✅ Model loaded successfully!")
print("🌐 Server running at http://localhost:5000")
print("📊 Health check: http://localhost:5000/api/health")
print("\nPress Ctrl+C to stop\n")

if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=False,
        use_reloader=False,
        log_output=True
    )
