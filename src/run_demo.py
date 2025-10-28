r"""Demo wrapper that runs the official YOLOv7 detect.py and then performs OCR on detected plates.

Usage (PowerShell):
python src\run_demo.py --yolov7-dir external\yolov7 --weights models\yolov7.pt --source assets\test.jpg

This script:
- Calls external/yolov7/detect.py with --save-txt --save-conf (so labels are written)
- Reads label files and crops plate regions from the original images
- Runs EasyOCR on each crop and writes results to CSV
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
import csv
import cv2
import pandas as pd

from src.ocr import ocr_read_plate
from src.utils import yolo_label_to_box


def run_yolov7_detect(yolov7_dir: Path, weights: Path, source: Path, conf_thres: float):
    # Build command to call YOLOv7 detect.py
    detect_py = yolov7_dir / "detect.py"
    if not detect_py.exists():
        raise FileNotFoundError(
            f"detect.py not found in {yolov7_dir}. Clone the official repo to that path."
        )

    cmd = [
        sys.executable,
        str(detect_py),
        "--weights",
        str(weights),
        "--source",
        str(source),
        "--conf",
        str(conf_thres),
        "--save-txt",  # saves labels in runs/detect/exp/labels
        "--save-conf",
    ]

    print("Running YOLOv7 detect: ", " ".join(cmd))
    subprocess.check_call(cmd)


def find_latest_run_detect_folder(runs_root: Path) -> Path:
    # YOLOv7 writes to runs/detect/exp, exp1, exp2... Return the latest
    detect_root = runs_root / "detect"
    if not detect_root.exists():
        raise FileNotFoundError(
            f"No runs/detect directory found under {runs_root}. Did detection run successfully?"
        )
    exps = sorted([p for p in detect_root.iterdir() if p.is_dir()], key=lambda p: p.stat().st_mtime)
    return exps[-1]


def process_labels_and_ocr(run_exp_dir: Path, source: Path, out_csv: Path):
    labels_dir = run_exp_dir / "labels"
    if not labels_dir.exists():
        raise FileNotFoundError(f"Labels directory not found: {labels_dir}")

    rows = []

    for label_file in labels_dir.glob("*.txt"):
        # corresponding source image name
        image_name = label_file.stem + label_file.suffix.replace(".txt", "")
        # YOLOv7 uses original filename (no extension in label file stem is the source filename without ext)
        # We will try to find the source image by stem
        candidates = list(source.parent.glob(label_file.stem + ".*"))
        if candidates:
            img_path = candidates[0]
        else:
            # fallback: use source if single source provided
            img_path = source

        img = cv2.imread(str(img_path))
        if img is None:
            print(f"Warning: failed to read {img_path}")
            continue
        h, w = img.shape[:2]

        with open(label_file, "r", encoding="utf8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 5:
                    continue
                cls = parts[0]
                x_c, y_c, bw, bh = map(float, parts[1:5])
                x1, y1, x2, y2 = yolo_label_to_box(x_c, y_c, bw, bh, w, h)
                # clip
                x1, y1, x2, y2 = map(int, [max(0, x1), max(0, y1), min(w - 1, x2), min(h - 1, y2)])
                crop = img[y1:y2, x1:x2]
                if crop.size == 0:
                    continue
                text, conf = ocr_read_plate(crop)
                rows.append(
                    {
                        "image": str(img_path.name),
                        "class": cls,
                        "bbox": f"{x1},{y1},{x2},{y2}",
                        "plate_text": text,
                        "plate_conf": conf,
                    }
                )

    if rows:
        df = pd.DataFrame(rows)
        df.to_csv(out_csv, index=False)
        print(f"OCR results written to {out_csv}")
    else:
        print("No plate crops / OCR results produced.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--yolov7-dir",
        type=Path,
        required=True,
        help="Path to cloned YOLOv7 repo (external/yolov7)",
    )
    parser.add_argument("--weights", type=Path, required=True, help="YOLOv7 weights path (.pt)")
    parser.add_argument(
        "--source", type=Path, required=True, help="Image or folder or video source"
    )
    parser.add_argument("--conf-thres", type=float, default=0.25)
    parser.add_argument(
        "--runs-root", type=Path, default=Path("runs"), help="Root runs directory (default: runs)"
    )

    args = parser.parse_args()

    run_yolov7_detect(args.yolov7_dir, args.weights, args.source, args.conf_thres)
    run_exp = find_latest_run_detect_folder(args.runs_root)
    out_csv = run_exp / "ocr_results.csv"
    process_labels_and_ocr(run_exp, args.source, out_csv)


if __name__ == "__main__":
    main()
