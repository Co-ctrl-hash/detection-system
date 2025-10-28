"""Plate detector module wrapping YOLOv7 + OCR."""
from __future__ import annotations

import sys
from pathlib import Path
import cv2
import numpy as np
import torch
from typing import List, Dict, Any

# Add YOLOv7 to path
yolov7_path = Path(__file__).parent.parent / 'external' / 'yolov7'
if yolov7_path.exists():
    sys.path.insert(0, str(yolov7_path))

try:
    from models.experimental import attempt_load
    from utils.general import non_max_suppression, scale_coords
    from utils.torch_utils import select_device
    from utils.datasets import letterbox
except ImportError:
    print("Warning: YOLOv7 modules not found. Ensure external/yolov7 is cloned.")
    attempt_load = None

# OCR import
try:
    import easyocr
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Warning: EasyOCR not installed. OCR will be disabled.")


class PlateDetector:
    """YOLOv7-based plate detector with OCR integration."""
    
    def __init__(
        self,
        yolov7_weights: str = 'models/yolov7.pt',
        device: str = 'cpu',  # Default to CPU to avoid CUDA errors
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        img_size: int = 640
    ):
        """Initialize detector.
        
        Args:
            yolov7_weights: Path to YOLOv7 weights file.
            device: CUDA device ('0', '1', etc.) or 'cpu'. Defaults to 'cpu'.
            conf_threshold: Confidence threshold for detections.
            iou_threshold: IoU threshold for NMS.
            img_size: Input image size.
        """
        # Safe device selection - check CUDA availability
        if attempt_load:
            if device != 'cpu':
                # Check if CUDA is available before using GPU
                try:
                    import torch
                    if not torch.cuda.is_available():
                        print(f"Warning: CUDA not available. Switching from device '{device}' to 'cpu'")
                        device = 'cpu'
                except Exception:
                    device = 'cpu'
            self.device = select_device(device)
        else:
            self.device = 'cpu'
        
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.img_size = img_size
        
        # Load model
        if attempt_load and Path(yolov7_weights).exists():
            try:
                # Try loading with weights_only=False for PyTorch 2.6+ compatibility
                self.model = attempt_load(yolov7_weights, map_location=self.device)
                self.model.eval()
                print(f"Model loaded: {yolov7_weights} on {self.device}")
            except Exception as e:
                # Fallback: patch torch.load to use weights_only=False
                import torch
                original_load = torch.load
                torch.load = lambda *args, **kwargs: original_load(*args, **{**kwargs, 'weights_only': False})
                try:
                    self.model = attempt_load(yolov7_weights, map_location=self.device)
                    self.model.eval()
                    print(f"Model loaded: {yolov7_weights} on {self.device}")
                finally:
                    torch.load = original_load
        else:
            self.model = None
            print(f"Warning: Model not loaded. Weights not found or YOLOv7 not available.")
        
        # Load OCR reader
        self.ocr_reader = None
        if OCR_AVAILABLE:
            try:
                self.ocr_reader = easyocr.Reader(['en'], gpu=(str(self.device) != 'cpu'))
                print("OCR reader initialized")
            except Exception as e:
                print(f"Warning: OCR reader failed to initialize: {e}")
    
    def preprocess(self, img: np.ndarray) -> torch.Tensor:
        """Preprocess image for YOLOv7 input.
        
        Args:
            img: OpenCV image (BGR, HWC format).
        
        Returns:
            Preprocessed tensor (1, 3, H, W).
        """
        # Letterbox resize
        img_resized = letterbox(img, self.img_size, stride=32)[0]
        
        # Convert BGR to RGB
        img_rgb = img_resized[:, :, ::-1].transpose(2, 0, 1)
        img_rgb = np.ascontiguousarray(img_rgb)
        
        # To tensor and normalize
        img_tensor = torch.from_numpy(img_rgb).to(self.device)
        img_tensor = img_tensor.float() / 255.0
        
        if img_tensor.ndimension() == 3:
            img_tensor = img_tensor.unsqueeze(0)
        
        return img_tensor
    
    def run_ocr(self, plate_crop: np.ndarray) -> tuple[str, float]:
        """Run OCR on plate crop.
        
        Args:
            plate_crop: Cropped plate image.
        
        Returns:
            (plate_text, confidence)
        """
        if self.ocr_reader is None:
            return "NO_OCR", 0.0
        
        try:
            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2RGB)
            results = self.ocr_reader.readtext(img_rgb, detail=1)
            
            if results:
                # Get result with highest confidence
                # EasyOCR returns list of tuples: (bbox, text, confidence)
                best = max(results, key=lambda r: r[2])  # type: ignore[index]
                text: str = best[1].strip().upper()  # type: ignore[index]
                conf = float(best[2])  # type: ignore[index]
                return text, conf
            else:
                return "UNKNOWN", 0.0
        except Exception as e:
            print(f"OCR error: {e}")
            return "ERROR", 0.0
    
    def detect(self, img: np.ndarray) -> List[Dict[str, Any]]:
        """Detect plates in image and run OCR.
        
        Args:
            img: Input image (BGR format).
        
        Returns:
            List of detection dicts with keys:
                - bbox: [x1, y1, x2, y2]
                - confidence: detection confidence
                - plate_text: OCR result
                - ocr_confidence: OCR confidence
                - plate_crop: cropped plate image
        """
        if self.model is None:
            return []
        
        original_img = img.copy()
        h, w = img.shape[:2]
        
        # Preprocess
        img_tensor = self.preprocess(img)
        
        # Inference
        with torch.no_grad():
            pred = self.model(img_tensor)[0]
        
        # NMS
        pred = non_max_suppression(
            pred, self.conf_threshold, self.iou_threshold, classes=None, agnostic=False
        )[0]
        
        results = []
        
        if pred is not None and len(pred):
            # Scale boxes back to original image
            pred[:, :4] = scale_coords(img_tensor.shape[2:], pred[:, :4], img.shape).round()
            
            for *xyxy, conf, cls in pred:
                x1, y1, x2, y2 = map(int, xyxy)
                
                # Clip coordinates
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)
                
                # Crop plate
                plate_crop = original_img[y1:y2, x1:x2]
                
                if plate_crop.size == 0:
                    continue
                
                # Run OCR
                plate_text, ocr_conf = self.run_ocr(plate_crop)
                
                results.append({
                    'bbox': [x1, y1, x2, y2],
                    'confidence': float(conf),
                    'plate_text': plate_text,
                    'ocr_confidence': ocr_conf,
                    'plate_crop': plate_crop
                })
        
        return results
