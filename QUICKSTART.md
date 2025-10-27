# ⚡ Quick Setup & Run Instructions

## 🎯 Goal
Get the full-stack Number Plate Detection system running in under 10 minutes.

## 📋 Prerequisites Checklist
- [ ] Python 3.8+ installed
- [ ] Node.js 16+ and npm installed
- [ ] Git installed
- [ ] NVIDIA GPU with CUDA 11.8+ (optional, can use CPU)

---

## 🚀 Setup Steps

### Step 1: Clone & Navigate (1 min)
```powershell
git clone <your-repo-url>
cd "new project"
```

### Step 2: Backend Setup (3 mins)
```powershell
# Create virtual environment
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# Install PyTorch (choose one):
# For GPU (CUDA 11.8):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
# For CPU only:
# pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install backend dependencies
pip install -r requirements.txt

# Clone YOLOv7
git clone https://github.com/WongKinYiu/yolov7.git external\yolov7
pip install -r external\yolov7\requirements.txt

# Download model weights
mkdir models
Invoke-WebRequest -Uri "https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7.pt" -OutFile "models\yolov7.pt"

# Setup environment
copy .env.example .env

# Initialize database
python -c "from backend.app import app, db; app.app_context().push(); db.create_all(); print('Database ready!')"
```

### Step 3: Frontend Setup (2 mins)
**Open a new terminal:**
```powershell
cd frontend
npm install
```

### Step 4: Run the System (1 min)

**Option A - Automated (Recommended):**
```powershell
.\start.ps1
```

**Option B - Manual:**

Terminal 1 (Backend):
```powershell
.\.venv\Scripts\Activate.ps1
python backend\app.py
```

Terminal 2 (Frontend):
```powershell
cd frontend
npm run dev
```

---

## 🌐 Access the Application

Once both servers are running:

**Frontend UI:** http://localhost:3000  
**Backend API:** http://localhost:5000  
**API Health Check:** http://localhost:5000/api/health

---

## 🎨 What You Can Do

1. **Live Detection** tab:
   - Click "Start Camera" to use your webcam
   - See real-time plate detection with bounding boxes
   - View recent detections in the side panel

2. **Upload File** tab:
   - Upload an image or video file
   - Get instant detection results
   - See all detected plates with confidence scores

3. **Detection History** tab:
   - Browse all past detections
   - Filter by camera ID
   - Paginate through results
   - Delete records

4. **Statistics** tab:
   - View total detections
   - See unique plates count
   - Check camera activity
   - Visualize data with charts

---

## 🧪 Quick Test

### Test 1: API Health Check
```powershell
curl http://localhost:5000/api/health
```

Expected output:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "..."
}
```

### Test 2: Upload Image via API
```powershell
curl -X POST http://localhost:5000/api/detect -F "file=@path\to\image.jpg"
```

### Test 3: Frontend Access
Open browser → http://localhost:3000 → Should see the app UI

---

## ❌ Troubleshooting

### Backend won't start
```powershell
# Check if port 5000 is in use
netstat -ano | findstr :5000

# If in use, change port in .env:
# PORT=5001
```

### Frontend won't start
```powershell
# Clear and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Model not loading
```powershell
# Verify YOLOv7 is cloned
ls external\yolov7

# Verify weights exist
ls models\yolov7.pt

# Check PyTorch
python -c "import torch; print(torch.__version__)"
```

### Database errors
```powershell
# Delete and recreate
rm plates.db
python -c "from backend.app import app, db; app.app_context().push(); db.create_all()"
```

### CORS errors in browser
- Ensure backend is running on port 5000
- Check frontend proxy in `frontend/vite.config.js`
- Verify CORS_ORIGINS in backend `.env`

---

## 🎓 Next Steps

1. **Train your own model:**
   ```powershell
   python src\train.py --config configs\train_config.yaml
   ```

2. **Deploy with Docker:**
   ```powershell
   docker-compose up
   ```

3. **Read full documentation:**
   - [Full-Stack Setup](docs/FULLSTACK_SETUP.md)
   - [Deployment Guide](docs/DEPLOY.md)
   - [API Documentation](README.md#api-documentation)

---

## 📞 Need Help?

- Check [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for complete feature list
- Read [FULLSTACK_SETUP.md](docs/FULLSTACK_SETUP.md) for detailed instructions
- Email: hello@innovateintern.com
- Website: www.innovateintern.com

---

**🎉 You're all set! Start detecting plates in real-time!**
