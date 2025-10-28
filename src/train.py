"""Training script for YOLOv7 number plate detection.

This wrapper calls the official YOLOv7 train.py with config-driven parameters.
Supports transfer learning from pretrained COCO weights.

Usage:
python src/train.py --config configs/train_config.yaml
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
import yaml


def load_config(config_path: Path) -> dict:
    """Load YAML config."""
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_yolov7_train(yolov7_dir: Path, config: dict):
    """Call YOLOv7 train.py with parameters from config."""
    train_py = yolov7_dir / "train.py"
    if not train_py.exists():
        raise FileNotFoundError(f"train.py not found in {yolov7_dir}")

    cmd = [
        sys.executable,
        str(train_py),
        "--workers",
        str(config.get("workers", 8)),
        "--device",
        str(config.get("device", "0")),
        "--batch-size",
        str(config.get("batch_size", 16)),
        "--epochs",
        str(config.get("epochs", 100)),
        "--data",
        str(config["data_yaml"]),
        "--img",
        str(config.get("img_size", 640)),
        "--cfg",
        str(config.get("cfg", "cfg/training/yolov7.yaml")),
        "--weights",
        str(config.get("weights", "")),
        "--name",
        config.get("name", "plate_detector"),
        "--hyp",
        str(config.get("hyp", "data/hyp.scratch.p5.yaml")),
    ]

    # optional args
    if config.get("cache_images"):
        cmd.append("--cache")
    if config.get("multi_scale"):
        cmd.append("--multi-scale")
    if config.get("nosave"):
        cmd.append("--nosave")
    if config.get("notest"):
        cmd.append("--notest")
    if config.get("evolve"):
        cmd.append("--evolve")
    if config.get("rect"):
        cmd.append("--rect")
    if config.get("adam"):
        cmd.append("--adam")
    if config.get("sync_bn"):
        cmd.append("--sync-bn")

    print("Running YOLOv7 training:", " ".join(cmd))
    subprocess.check_call(cmd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True, help="Path to training config YAML")
    parser.add_argument(
        "--yolov7-dir", type=Path, default=Path("external/yolov7"), help="Path to YOLOv7 repo"
    )
    args = parser.parse_args()

    config = load_config(args.config)
    run_yolov7_train(args.yolov7_dir, config)


if __name__ == "__main__":
    main()
