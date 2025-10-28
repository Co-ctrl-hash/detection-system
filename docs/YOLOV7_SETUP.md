# YOLOv7 Model Setup - Warning Resolution Guide

## ✅ **Status After Fixes**

All YOLOv7 dependencies are now installed! The warnings you see are **expected** until you download the model weights file.

## 🔍 **Understanding the Warnings**

### Warning 1: "YOLOv7 modules not found" ✅ **RESOLVED**
**What it meant:** Missing Python dependencies for YOLOv7  
**Fixed by:** Installed matplotlib, scipy, tensorboard, seaborn, etc.  
**Status:** ✅ No longer appears

### Warning 2: "Model not loaded. Weights not found" ⚠️ **EXPECTED**
**What it means:** The actual YOLO model weights file doesn't exist yet  
**Why:** The `models/yolov7.pt` file needs to be downloaded (it's a large file ~75MB)  
**Status:** ⚠️ Normal - you need to download weights

### Warning 3: "Using CPU" ℹ️ **INFORMATIONAL**
**What it means:** No GPU detected, using CPU for inference  
**Why:** Your system doesn't have NVIDIA CUDA GPU  
**Status:** ℹ️ Expected - CPU works fine, just slower

## 📥 **Download YOLOv7 Weights**

You have **two options**:

### Option 1: Official YOLOv7 Weights (Recommended for actual detection)

Download pre-trained YOLOv7 weights:

```powershell
# Create models directory if it doesn't exist
New-Item -ItemType Directory -Force -Path models

# Download YOLOv7 weights (~75MB)
Invoke-WebRequest -Uri "https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7.pt" -OutFile "models/yolov7.pt"
```

**Alternative download links:**
- YOLOv7: https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7.pt
- YOLOv7-tiny (smaller, faster): https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7-tiny.pt

### Option 2: Use License Plate Fine-tuned Model (Better for plates)

If you want better license plate detection, you'll need to either:
1. Download a fine-tuned model for license plates (if available)
2. Train your own using the Kaggle dataset we integrated

## 🧪 **Verify Setup**

After downloading weights:

```powershell
python -c "from backend.detector import PlateDetector; d = PlateDetector(device='cpu'); print('Model loaded:', d.model is not None)"
```

Expected output:
```
Model loaded: models/yolov7.pt on cpu
OCR reader initialized
Model loaded: True
```

## 🚀 **Test Detection**

After weights are downloaded, test with a sample image:

```powershell
python -c "
from backend.detector import PlateDetector
import cv2

detector = PlateDetector(device='cpu')
img = cv2.imread('path/to/your/image.jpg')
if img is not None:
    results = detector.detect(img)
    print(f'Detections: {len(results)}')
    for r in results:
        print(f'Plate: {r[\"plate_text\"]} (confidence: {r[\"confidence\"]:.2f})')
"
```

## ⚙️ **Environment Configuration**

Update your `.env` file:

```bash
# For CPU (current setup)
DEVICE=cpu
MODEL_WEIGHTS=models/yolov7.pt

# For GPU (if you have NVIDIA GPU with CUDA)
# DEVICE=0
# MODEL_WEIGHTS=models/yolov7.pt
```

## 📊 **Current Status Summary**

| Component | Status | Action Needed |
|-----------|--------|---------------|
| YOLOv7 Repository | ✅ Cloned | None |
| Python Dependencies | ✅ Installed | None |
| Model Weights | ❌ Missing | Download from link above |
| OCR (EasyOCR) | ✅ Working | None |
| CUDA/GPU | ❌ Not Available | Optional - CPU works fine |

## 🎯 **Quick Fix Commands**

**To eliminate all warnings, run these commands:**

```powershell
# 1. Download YOLOv7 weights
Invoke-WebRequest -Uri "https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7.pt" -OutFile "models/yolov7.pt"

# 2. Set environment to use CPU
$env:DEVICE="cpu"

# 3. Test the app
python -c "from backend.app import app; c=app.test_client(); r=c.get('/api/health'); print(r.data.decode())"
```

Expected health check result:
```json
{
  "status": "healthy",
  "model_loaded": true,  ← Should be true after weights download
  "timestamp": "..."
}
```

## 🔄 **Training Your Own Model (Advanced)**

To train YOLOv7 on license plates using the Kaggle dataset:

1. Organize the Kaggle dataset (we already have the download script)
2. Convert annotations to YOLO format
3. Update `data/plates/data.yaml`
4. Run training:

```powershell
cd external/yolov7
python train.py --weights yolov7.pt --data ../../data/plates/data.yaml --epochs 100 --batch-size 16 --img 640 --device cpu
```

## ❓ **FAQ**

**Q: Can I use the app without downloading weights?**  
A: The app will start, but detection won't work. All endpoints will return empty results.

**Q: Why is it using CPU instead of GPU?**  
A: Your system doesn't have an NVIDIA GPU with CUDA installed. CPU works fine for testing.

**Q: How big is the weights file?**  
A: ~75MB for yolov7.pt, ~12MB for yolov7-tiny.pt

**Q: Do I need both PyTorch and YOLOv7?**  
A: Yes. PyTorch (already installed) is the framework, YOLOv7 is the model architecture, and the .pt file contains the trained weights.

## 📝 **Summary**

**The warnings are expected behavior:**
1. ✅ YOLOv7 Python modules - **FIXED** (dependencies installed)
2. ⚠️ Model weights missing - **NORMAL** (download required)
3. ℹ️ Using CPU - **OK** (works fine without GPU)

**Next step:** Download `yolov7.pt` weights file to enable actual plate detection!
