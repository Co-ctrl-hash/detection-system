"""
Startup script for the number plate detection Flask server.
This script handles the initial slow loading of PyTorch/YOLOv7 with a progress indicator.
"""
import sys
import time
from threading import Thread

def show_loading():
    """Show a loading animation while imports happen."""
    chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    idx = 0
    while loading:
        sys.stdout.write(f'\r{chars[idx % len(chars)]} Loading PyTorch and YOLOv7 (this takes ~20-30 seconds on first run)...')
        sys.stdout.flush()
        idx += 1
        time.sleep(0.1)
    sys.stdout.write('\r' + ' ' * 100 + '\r')  # Clear line
    sys.stdout.flush()

# Start loading animation
loading = True
loader_thread = Thread(target=show_loading, daemon=True)
loader_thread.start()

try:
    # The slow imports
    print("🚀 Starting Number Plate Detection Server...")
    print("=" * 60)
    
    from backend.app import app, socketio
    
    loading = False
    time.sleep(0.2)  # Give animation time to clear
    
    print("✅ All modules loaded successfully!")
    print("✅ YOLOv7 model ready")
    print("✅ EasyOCR initialized")
    print("=" * 60)
    print(f"🌐 Server starting at http://localhost:5000")
    print(f"📊 Health check: http://localhost:5000/api/health")
    print(f"📖 API Documentation available in docs/")
    print("=" * 60)
    print("Press Ctrl+C to stop the server\n")
    
    # Start the Flask app
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    
except KeyboardInterrupt:
    loading = False
    print("\n\n👋 Server stopped by user")
    sys.exit(0)
except Exception as e:
    loading = False
    print(f"\n\n❌ Error starting server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
