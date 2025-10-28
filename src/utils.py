"""Utility helpers for the demo."""

from __future__ import annotations

from typing import Tuple


def yolo_label_to_box(
    xc: float, yc: float, bw: float, bh: float, img_w: int, img_h: int
) -> Tuple[float, float, float, float]:
    """Convert YOLO normalized center-format to pixel box (x1,y1,x2,y2).

    xc, yc, bw, bh are in normalized [0,1] relative to image size.
    """
    x_center = xc * img_w
    y_center = yc * img_h
    box_w = bw * img_w
    box_h = bh * img_h
    x1 = x_center - box_w / 2.0
    y1 = y_center - box_h / 2.0
    x2 = x_center + box_w / 2.0
    y2 = y_center + box_h / 2.0
    return x1, y1, x2, y2
