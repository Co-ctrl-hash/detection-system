# Installation Guide

## Prerequisites

### System Requirements
- **OS**: Windows 10/11, Ubuntu 20.04+, or macOS 11+
- **Python**: 3.8 or higher (3.10 recommended)
- **GPU** (optional but recommended):
  - NVIDIA GPU with CUDA 11.8+ support
  - At least 6GB VRAM for training (RTX 2060 or better)
  - 4GB VRAM minimum for inference

### Software Dependencies
- Git
- CUDA Toolkit 11.8+ (for GPU support)
- cuDNN 8.x (for GPU support)

---

## Installation Steps

### 1. Clone the Repository

```powershell
git clone https://github.com/yourusername/plate-detection-yolov7.git
cd plate-detection-yolov7
```

### 2. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install PyTorch

**GPU (CUDA 11.8):**
```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**CPU only:**
```powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

**Verify installation:**
```powershell
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```

### 4. Install Project Dependencies

```powershell
pip install -r requirements.txt
```

### 5. Clone YOLOv7 Repository

```powershell
git clone https://github.com/WongKinYiu/yolov7.git external\yolov7
pip install -r external\yolov7\requirements.txt
```

### 6. Download Pretrained Weights

**YOLOv7 COCO weights:**
```powershell
mkdir models
Invoke-WebRequest -Uri "https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7.pt" -OutFile "models\yolov7.pt"
```

**Or manually download:**
- Visit: https://github.com/WongKinYiu/yolov7/releases
- Download `yolov7.pt` to `models/` directory

### 7. Verify Installation

```powershell
python -c "from src.utils import yolo_label_to_box; print('Utils OK')"
python -c "import easyocr; print('EasyOCR OK')"
```

---

## Docker Installation (Alternative)

### Prerequisites
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- NVIDIA Docker runtime (for GPU support)

### Build and Run

**GPU:**
```powershell
docker build -f docker\Dockerfile.gpu -t plate-detector:gpu .
docker run --gpus all -it plate-detector:gpu bash
```

**CPU:**
```powershell
docker build -f docker\Dockerfile.cpu -t plate-detector:cpu .
docker run -it plate-detector:cpu bash
```

---

## Troubleshooting

### Issue: `torch.cuda.is_available()` returns False

**Solution:**
- Verify NVIDIA driver installed: `nvidia-smi`
- Reinstall PyTorch with correct CUDA version
- Check CUDA compatibility with your GPU

### Issue: EasyOCR fails to import

**Solution:**
```powershell
pip install easyocr==1.6.2 --no-deps
pip install torch torchvision opencv-python-headless scipy pillow scikit-image python-bidi pyyaml ninja
```

### Issue: YOLOv7 detect.py not found

**Solution:**
- Ensure YOLOv7 cloned to `external/yolov7`
- Use `--yolov7-dir` flag to specify custom path

### Issue: Out of memory during training

**Solution:**
- Reduce batch size in `configs/train_config.yaml`
- Use smaller image size (640 instead of 1280)
- Enable gradient accumulation
- Use YOLOv7-tiny instead

### Issue: Slow inference on CPU

**Expected behavior** - CPU inference is much slower than GPU. For production:
- Export to ONNX and use ONNXRuntime
- Use smaller input size
- Consider cloud GPU or edge device

---

## Platform-Specific Notes

### Windows
- Use PowerShell or Windows Terminal
- If execution policy blocks scripts: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- For long paths, enable: `git config --system core.longpaths true`

### Linux
- Install system dependencies:
  ```bash
  sudo apt-get update
  sudo apt-get install -y python3-dev libgl1-mesa-glx libglib2.0-0
  ```

### macOS
- No CUDA support; use CPU or MPS backend (PyTorch 2.0+)
- Install via Homebrew: `brew install python@3.10`

---

## Next Steps

After successful installation:

1. **Test inference**:
   ```powershell
   python src\run_demo.py --yolov7-dir external\yolov7 --weights models\yolov7.pt --source assets\sample.jpg
   ```

2. **Prepare dataset**:
   ```powershell
   python data\scripts\download_datasets.py
   ```

3. **Train model**:
   ```powershell
   python src\train.py --config configs\train_config.yaml
   ```

4. **Read documentation**:
   - [DEPLOY.md](DEPLOY.md) - Deployment guide
   - [ETHICS.md](ETHICS.md) - Privacy and ethics
   - [TIMELINE.md](TIMELINE.md) - Project timeline

---

## Getting Help

- **Issues**: https://github.com/yourusername/plate-detection-yolov7/issues
- **Discussions**: https://github.com/yourusername/plate-detection-yolov7/discussions
- **Email**: support@yourproject.com

---

## System Validation Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] PyTorch installed and CUDA available (if using GPU)
- [ ] Project dependencies installed
- [ ] YOLOv7 repository cloned
- [ ] Pretrained weights downloaded
- [ ] Test inference runs successfully
- [ ] No import errors

**Installation complete! You're ready to start training and deploying.**
