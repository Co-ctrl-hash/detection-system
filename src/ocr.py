"""Simple EasyOCR wrapper for plate reading."""
from __future__ import annotations

import numpy as np
import easyocr
import cv2

# Lazy-load reader to reduce startup time for imports
_READER = None


def get_reader(lang_list=None):
    global _READER
    if _READER is None:
        if lang_list is None:
            lang_list = ["en"]
        _READER = easyocr.Reader(lang_list, gpu=False)  # set gpu=True if GPU and CUDA available
    return _READER


def ocr_read_plate(crop: np.ndarray) -> tuple[str, float]:
    """Run EasyOCR on BGR/OpenCV image crop. Returns (text, confidence).

    If no result, returns ('', 0.0).
    """
    reader = get_reader()
    # convert to RGB
    img_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
    results = reader.readtext(img_rgb, detail=1)
    if not results:
        return "", 0.0
    # choose the top result by confidence
    best = max(results, key=lambda r: r[2])
    text = best[1]
    conf = float(best[2])
    return text, conf
