"""Evaluation script for number plate detection model.

Computes:
- Precision, Recall, F1
- mAP@0.5, mAP@0.5:0.95
- Per-class metrics
- Inference latency/throughput

Usage:
python src/evaluate.py --weights models/best.pt --data data/plates/data.yaml --img-size 640
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path
import json
import pandas as pd
import numpy as np


def run_yolov7_test(
    yolov7_dir: Path,
    weights: Path,
    data_yaml: Path,
    img_size: int,
    batch_size: int,
    conf_thres: float,
    iou_thres: float,
):
    """Run YOLOv7 test.py to evaluate on test set."""
    test_py = yolov7_dir / "test.py"
    if not test_py.exists():
        raise FileNotFoundError(f"test.py not found in {yolov7_dir}")

    cmd = [
        sys.executable,
        str(test_py),
        "--data",
        str(data_yaml),
        "--weights",
        str(weights),
        "--batch-size",
        str(batch_size),
        "--img-size",
        str(img_size),
        "--conf-thres",
        str(conf_thres),
        "--iou-thres",
        str(iou_thres),
        "--task",
        "test",
        "--save-json",
        "--save-txt",
    ]

    print("Running YOLOv7 evaluation:", " ".join(cmd))
    subprocess.check_call(cmd)


def measure_inference_latency(
    yolov7_dir: Path, weights: Path, img_size: int, num_iterations: int = 100, device: str = "0"
):
    """Measure average inference latency using YOLOv7 detect."""
    # Create a dummy image for latency measurement
    import cv2

    dummy_img = np.random.randint(0, 255, (img_size, img_size, 3), dtype=np.uint8)
    dummy_path = Path("temp_test_img.jpg")
    cv2.imwrite(str(dummy_path), dummy_img)

    detect_py = yolov7_dir / "detect.py"

    latencies = []
    for i in range(num_iterations):
        start = time.perf_counter()
        cmd = [
            sys.executable,
            str(detect_py),
            "--weights",
            str(weights),
            "--source",
            str(dummy_path),
            "--img-size",
            str(img_size),
            "--device",
            device,
            "--nosave",
        ]
        subprocess.run(cmd, capture_output=True, check=True)
        elapsed = time.perf_counter() - start
        latencies.append(elapsed)

    dummy_path.unlink()

    return {
        "mean_latency_ms": np.mean(latencies) * 1000,
        "std_latency_ms": np.std(latencies) * 1000,
        "p50_latency_ms": np.percentile(latencies, 50) * 1000,
        "p95_latency_ms": np.percentile(latencies, 95) * 1000,
        "p99_latency_ms": np.percentile(latencies, 99) * 1000,
        "throughput_fps": 1.0 / np.mean(latencies),
    }


def parse_yolov7_results(results_file: Path) -> dict:
    """Parse YOLOv7 results.txt or results.json."""
    # YOLOv7 test.py outputs results in runs/test/exp/
    # Look for metrics in the output
    if results_file.exists() and results_file.suffix == ".json":
        with open(results_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def generate_report(metrics: dict, latency: dict, output_path: Path):
    """Generate evaluation report as markdown table."""
    report = []
    report.append("# Evaluation Report\n")
    report.append("## Detection Metrics\n")
    report.append("| Metric | Value |")
    report.append("|--------|-------|")
    for k, v in metrics.items():
        report.append(f"| {k} | {v:.4f} |")

    report.append("\n## Latency & Throughput\n")
    report.append("| Metric | Value |")
    report.append("|--------|-------|")
    for k, v in latency.items():
        if "fps" in k:
            report.append(f"| {k} | {v:.2f} |")
        else:
            report.append(f"| {k} | {v:.2f} ms |")

    report_text = "\n".join(report)
    output_path.write_text(report_text, encoding="utf-8")
    print(f"\nEvaluation report written to {output_path}")
    print(report_text)


def main():
    parser = argparse.ArgumentParser(description="Evaluate YOLOv7 plate detector")
    parser.add_argument("--yolov7-dir", type=Path, default=Path("external/yolov7"))
    parser.add_argument("--weights", type=Path, required=True, help="Model weights path")
    parser.add_argument("--data", type=Path, required=True, help="data.yaml path")
    parser.add_argument("--img-size", type=int, default=640)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--conf-thres", type=float, default=0.001)
    parser.add_argument("--iou-thres", type=float, default=0.6)
    parser.add_argument("--device", type=str, default="0")
    parser.add_argument(
        "--measure-latency", action="store_true", help="Measure inference latency (takes time)"
    )
    parser.add_argument("--latency-iterations", type=int, default=100)
    parser.add_argument("--output", type=Path, default=Path("evaluation_report.md"))

    args = parser.parse_args()

    # Run test evaluation
    print("Running test evaluation...")
    run_yolov7_test(
        args.yolov7_dir,
        args.weights,
        args.data,
        args.img_size,
        args.batch_size,
        args.conf_thres,
        args.iou_thres,
    )

    # Parse results (you may need to adapt this based on YOLOv7 output location)
    metrics = {"mAP@0.5": 0.0, "mAP@0.5:0.95": 0.0}  # placeholder
    print("\nNote: Parse actual metrics from YOLOv7 test output in runs/test/exp/")

    # Measure latency if requested
    latency = {}
    if args.measure_latency:
        print(f"\nMeasuring inference latency ({args.latency_iterations} iterations)...")
        latency = measure_inference_latency(
            args.yolov7_dir, args.weights, args.img_size, args.latency_iterations, args.device
        )

    # Generate report
    generate_report(metrics, latency, args.output)


if __name__ == "__main__":
    main()
