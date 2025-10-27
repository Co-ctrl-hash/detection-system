"""Dataset downloader and preparation utilities for license plate detection.

Provides helpers to download public datasets (CCPD, UFPR-ALPR) and convert to YOLO format.
"""
from __future__ import annotations

import os
import urllib.request
from pathlib import Path
from typing import Optional
import zipfile
import shutil


def download_file(url: str, dest: Path, force: bool = False):
    """Download a file from URL to destination."""
    if dest.exists() and not force:
        print(f"File already exists: {dest}")
        return
    
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {url} -> {dest}")
    urllib.request.urlretrieve(url, dest)
    print(f"Downloaded to {dest}")


def extract_zip(zip_path: Path, extract_to: Path):
    """Extract a zip file."""
    print(f"Extracting {zip_path} to {extract_to}")
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(extract_to)
    print(f"Extracted to {extract_to}")


def download_ccpd_sample(data_root: Path):
    """Download CCPD sample dataset.
    
    Note: Full CCPD dataset is very large (~10GB+). This downloads a small sample.
    For production, clone the full repo: https://github.com/detectRecog/CCPD
    """
    print("CCPD dataset must be manually downloaded from:")
    print("https://github.com/detectRecog/CCPD")
    print("Clone the repo and follow their instructions to download splits.")
    print(f"Place extracted data in: {data_root / 'ccpd'}")


def download_ufpr_alpr(data_root: Path):
    """Download UFPR-ALPR dataset.
    
    Public dataset link: https://web.inf.ufpr.br/vri/databases/ufpr-alpr/
    """
    print("UFPR-ALPR dataset can be downloaded from:")
    print("https://web.inf.ufpr.br/vri/databases/ufpr-alpr/")
    print("Download and extract to:")
    print(f"{data_root / 'ufpr-alpr'}")


def prepare_dataset_structure(data_root: Path):
    """Create standard YOLO dataset directory structure."""
    dirs = [
        data_root / "images" / "train",
        data_root / "images" / "val",
        data_root / "images" / "test",
        data_root / "labels" / "train",
        data_root / "labels" / "val",
        data_root / "labels" / "test",
        data_root / "raw",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    print(f"Created dataset structure in {data_root}")


def main():
    """Main entry point for dataset preparation."""
    import argparse
    parser = argparse.ArgumentParser(description="Download and prepare license plate datasets")
    parser.add_argument("--data-root", type=Path, default=Path("data/plates"),
                        help="Root directory for datasets")
    parser.add_argument("--dataset", choices=["ccpd", "ufpr", "all"], default="all",
                        help="Which dataset to download")
    args = parser.parse_args()

    prepare_dataset_structure(args.data_root)

    if args.dataset in ["ccpd", "all"]:
        download_ccpd_sample(args.data_root)
    
    if args.dataset in ["ufpr", "all"]:
        download_ufpr_alpr(args.data_root)

    print("\n=== Next Steps ===")
    print("1. Download the datasets from the links above")
    print("2. Convert annotations to YOLO format using data/scripts/convert_annotations.py")
    print("3. Split data into train/val/test and place in data/plates/images/ and data/plates/labels/")
    print("4. Update data/plates/data.yaml with correct paths")
    print("5. Run training: python src/train.py --config configs/train_config.yaml")


if __name__ == "__main__":
    main()
