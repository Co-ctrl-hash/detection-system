# Full-Stack Setup Guide

## System Architecture

This project consists of three main components:

1. **Frontend** - React.js web application (in `frontend/`)
2. **Backend** - Flask API server (in `backend/`)
3. **ML Model** - YOLOv7 detection + EasyOCR recognition

## Prerequisites

- **Python 3.8+**
- **Node.js 16+** and npm
- **CUDA 11.8+** (for GPU support)
- **Git**

---

## Backend Setup

### 1. Create Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install PyTorch

**GPU (CUDA 11.8):**
```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**CPU only:**
```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### 3. Install Backend Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Clone YOLOv7

```powershell
git clone https://github.com/WongKinYiu/yolov7.git external\yolov7
pip install -r external\yolov7\requirements.txt
```

### 5. Download Model Weights

```powershell
mkdir models
Invoke-WebRequest -Uri "https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7.pt" -OutFile "models\yolov7.pt"
```

### 6. Configure Environment

```powershell
copy .env.example .env
# Edit .env with your configuration
```

### 7. Initialize Database

```powershell
python -c "from backend.app import app, db; app.app_context().push(); db.create_all(); print('Database initialized')"
```

### 8. Run Backend Server

```powershell
python backend\app.py
```

Backend will run on `http://localhost:5000`

---

## Frontend Setup

### 1. Navigate to Frontend Directory

```powershell
cd frontend
```

### 2. Install Dependencies

```powershell
npm install
```

### 3. Start Development Server

```powershell
npm run dev
```

Frontend will run on `http://localhost:3000`

---

## Running the Full System

### Terminal 1 - Backend:
```powershell
.\.venv\Scripts\Activate.ps1
python backend\app.py
```

### Terminal 2 - Frontend:
```powershell
cd frontend
npm run dev
```

### Access the Application

Open your browser and navigate to: `http://localhost:3000`

---

## Features Overview

### 1. Live Detection
- Real-time webcam feed processing
- WebSocket-based communication
- Bounding box visualization
- Recent detections panel

### 2. Upload File
- Upload images or videos
- Batch processing for videos
- Instant detection results
- Confidence scores

### 3. Detection History
- Paginated table of all detections
- Filter by camera
- Sort and search
- Delete records

### 4. Statistics Dashboard
- Total detections count
- Unique plates identified
- Camera activity
- Charts and visualizations

---

## API Endpoints

### Health Check
```
GET /api/health
```

### Detect Plates in Image
```
POST /api/detect
Content-Type: multipart/form-data

Body:
- file: image file
- camera_id: (optional) camera identifier
```

### Detect Plates in Video
```
POST /api/detect/video
Content-Type: multipart/form-data

Body:
- file: video file
- camera_id: (optional) camera identifier
- sample_rate: (optional) frame sampling rate (default: 5)
```

### Get Detection History
```
GET /api/detections?page=1&per_page=50&camera_id=webcam
```

### Get Detection by ID
```
GET /api/detections/<id>
```

### Delete Detection
```
DELETE /api/detections/<id>
```

### Get Statistics
```
GET /api/stats
```

### WebSocket Events

**Client → Server:**
- `video_frame`: Send video frame for detection
  ```javascript
  {
    frame: base64_encoded_image,
    camera_id: "webcam"
  }
  ```

**Server → Client:**
- `connection_response`: Connection established
- `detection_result`: Detection results
  ```javascript
  {
    detections: [{plate_number, confidence, bbox}],
    timestamp: "ISO-8601"
  }
  ```
- `error`: Error message

---

## Database Schema

### Detections Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| plate_number | String(20) | Detected plate text |
| confidence | Float | Detection confidence (0-1) |
| camera_id | String(50) | Camera identifier |
| timestamp | DateTime | Detection timestamp |
| bbox_x1, bbox_y1 | Integer | Bounding box top-left |
| bbox_x2, bbox_y2 | Integer | Bounding box bottom-right |
| plate_image | Text | Base64 encoded plate crop |
| notes | Text | Optional notes |

---

## Production Deployment

### Using Docker

See [DEPLOY.md](docs/DEPLOY.md) for Docker deployment instructions.

### Environment Variables

Set these in production:
- `FLASK_ENV=production`
- `SECRET_KEY=<random-secret-key>`
- `DATABASE_URL=<production-database-url>`
- `CORS_ORIGINS=<production-frontend-url>`

### Database Migration

For production, use PostgreSQL or MySQL:

```powershell
# Install database driver
pip install psycopg2-binary  # PostgreSQL
# OR
pip install pymysql  # MySQL

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:pass@host/dbname
```

---

## Troubleshooting

### Backend Issues

**Port 5000 already in use:**
```powershell
# Change PORT in .env or:
python backend\app.py --port 5001
```

**Database errors:**
```powershell
# Recreate database
rm plates.db
python -c "from backend.app import app, db; app.app_context().push(); db.create_all()"
```

**Model not loading:**
- Ensure YOLOv7 cloned to `external/yolov7`
- Check weights path in `.env`
- Verify PyTorch installation with `python -c "import torch; print(torch.__version__)"`

### Frontend Issues

**Dependencies not installing:**
```powershell
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**CORS errors:**
- Ensure backend is running
- Check CORS_ORIGINS in backend `.env`
- Verify proxy settings in `frontend/vite.config.js`

**WebSocket connection fails:**
- Check backend logs
- Verify Socket.IO versions match
- Ensure firewall allows WebSocket connections

---

## Development Tips

### Hot Reload

Both frontend and backend support hot reload:
- Frontend: Vite automatically reloads on file changes
- Backend: Use `FLASK_ENV=development` for auto-reload

### Debugging

**Backend:**
```python
# Add breakpoints in code
import pdb; pdb.set_trace()
```

**Frontend:**
```javascript
// Use browser DevTools Console
console.log('Debug:', data)
```

### Testing

**Backend:**
```powershell
pytest tests/ -v
```

**Frontend:**
```powershell
cd frontend
npm test
```

---

## Next Steps

1. **Train Custom Model**: Use `src/train.py` with your dataset
2. **Deploy to Production**: Follow [DEPLOY.md](docs/DEPLOY.md)
3. **Add Features**: Multi-camera support, alerts, exports
4. **Optimize Performance**: TensorRT, model quantization
5. **Enhance UI**: Custom themes, dashboards, reports

---

## Support

- **Documentation**: See `docs/` folder
- **Issues**: https://github.com/yourusername/plate-detection-yolov7/issues
- **Email**: hello@innovateintern.com

---

**Happy detecting! 🚗📸**
