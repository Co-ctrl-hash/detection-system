# Deployment Guide for YOLOv7 Number Plate Detection System

## Docker Deployment

### Prerequisites
- Docker installed (version 20.10+)
- For GPU: NVIDIA Docker runtime installed
- Model weights downloaded to `models/` directory

### Build Docker Images

**GPU version:**
```powershell
docker build -f docker\Dockerfile.gpu -t plate-detector:gpu .
```

**CPU version:**
```powershell
docker build -f docker\Dockerfile.cpu -t plate-detector:cpu .
```

### Run Containers

**GPU inference:**
```powershell
docker run --gpus all -v ${PWD}\models:/app/models -v ${PWD}\data:/app/data -it plate-detector:gpu python src\run_demo.py --yolov7-dir external\yolov7 --weights models\best.pt --source data\test_image.jpg
```

**CPU inference:**
```powershell
docker run -v ${PWD}\models:/app/models -v ${PWD}\data:/app/data -it plate-detector:cpu python src\run_demo.py --yolov7-dir external\yolov7 --weights models\best.pt --source data\test_image.jpg
```

### Docker Compose

```powershell
cd docker
docker-compose up -d plate-detector-gpu
docker-compose exec plate-detector-gpu bash
```

## Edge Deployment

### NVIDIA Jetson (Nano/Xavier/Orin)

1. **Install JetPack SDK** (includes CUDA, cuDNN, TensorRT)
2. **Export model to ONNX:**
```powershell
python external\yolov7\export.py --weights models\best.pt --grid --simplify --img-size 640 640
```

3. **Convert ONNX to TensorRT:**
```bash
/usr/src/tensorrt/bin/trtexec --onnx=models/best.onnx --saveEngine=models/best.engine --fp16
```

4. **Run inference with TensorRT:**
```python
import tensorrt as trt
import pycuda.driver as cuda
# Load engine and run inference (see Jetson inference examples)
```

### Intel NCS2 (Neural Compute Stick)

1. **Install OpenVINO toolkit**
2. **Convert to OpenVINO IR:**
```bash
python /opt/intel/openvino/deployment_tools/model_optimizer/mo.py \
  --input_model models/best.onnx \
  --output_dir models/openvino
```

3. **Run with OpenVINO inference engine**

## Cloud Deployment (AWS/Azure/GCP)

### AWS EC2 with GPU (example: g4dn.xlarge)

1. Launch EC2 instance with Deep Learning AMI
2. Clone repo and install dependencies
3. Download weights from S3
4. Run inference or deploy as REST API using FastAPI

### Example FastAPI Service

Create `src/api.py`:
```python
from fastapi import FastAPI, File, UploadFile
import uvicorn

app = FastAPI()

@app.post("/detect")
async def detect_plate(file: UploadFile = File(...)):
    # Run detection and OCR
    # Return JSON with bbox and plate text
    return {"plate": "ABC1234", "confidence": 0.95}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Run:
```powershell
pip install fastapi uvicorn
python src\api.py
```

## ONNX Export for Production

Export YOLOv7 to ONNX for deployment without PyTorch:

```powershell
python external\yolov7\export.py --weights models\best.pt --grid --simplify --img-size 640 640
```

Run ONNX inference:
```python
import onnxruntime as ort
session = ort.InferenceSession("models/best.onnx")
outputs = session.run(None, {"images": input_tensor})
```

## TensorRT Optimization (NVIDIA GPUs)

For maximum performance on NVIDIA hardware:

```powershell
# Export to ONNX first
python external\yolov7\export.py --weights models\best.pt --grid --simplify

# Convert to TensorRT (Linux/Jetson)
trtexec --onnx=models\best.onnx --saveEngine=models\best.engine --fp16
```

## Performance Benchmarks (Example)

| Platform | Precision | FPS (640x640) | Latency (ms) |
|----------|-----------|---------------|--------------|
| RTX 3060 | FP32 | 120 | 8.3 |
| RTX 3060 | FP16 | 180 | 5.6 |
| GTX 1660 | FP32 | 75 | 13.3 |
| Jetson Xavier NX | FP16 | 45 | 22.2 |
| CPU (i7-10700) | FP32 | 5 | 200 |

## Monitoring & Logging

Recommended tools:
- **Prometheus + Grafana**: metrics (latency, throughput, errors)
- **ELK Stack**: log aggregation
- **Sentry**: error tracking

## Security & Privacy

- **Anonymize logs**: hash plate text before storing
- **Encrypt data at rest**: use encrypted volumes
- **Access control**: restrict API with authentication
- **Audit logging**: track who accessed what data

## Scaling

- **Horizontal scaling**: deploy multiple containers behind load balancer
- **GPU batching**: process multiple frames in parallel
- **Queue-based**: use Redis/RabbitMQ for async processing
