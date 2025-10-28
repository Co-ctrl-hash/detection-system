"""
Download Indian Number Plates Dataset from Kaggle
"""
import os
import sys
from pathlib import Path
import shutil

try:
    import kagglehub
except ImportError:
    print("Error: kagglehub not installed. Run: pip install kagglehub")
    sys.exit(1)


def download_indian_plates_dataset(output_dir: str = "data/kaggle_dataset"):
    """
    Download Indian Number Plates Dataset from Kaggle.
    
    Before running this script, you need to set up Kaggle API credentials:
    
    1. Go to https://www.kaggle.com/settings
    2. Scroll to "API" section
    3. Click "Create New API Token"
    4. This downloads kaggle.json
    5. Place kaggle.json in:
       - Windows: C:\\Users\\<YourUsername>\\.kaggle\\kaggle.json
       - Linux/Mac: ~/.kaggle/kaggle.json
    
    Args:
        output_dir: Directory to store the downloaded dataset
    """
    print("=" * 60)
    print("Downloading Indian Number Plates Dataset from Kaggle")
    print("=" * 60)
    print()
    
    # Check for Kaggle credentials
    kaggle_config_dir = Path.home() / ".kaggle"
    kaggle_json = kaggle_config_dir / "kaggle.json"
    
    if not kaggle_json.exists():
        print("❌ Kaggle API credentials not found!")
        print()
        print("Please set up your Kaggle API credentials:")
        print("1. Go to https://www.kaggle.com/settings")
        print("2. Scroll to 'API' section")
        print("3. Click 'Create New API Token'")
        print("4. Save kaggle.json to:", kaggle_config_dir)
        print()
        print("Creating .kaggle directory for you...")
        kaggle_config_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory created: {kaggle_config_dir}")
        print(f"📁 Please place your kaggle.json file in: {kaggle_json}")
        return None
    
    print(f"✅ Kaggle credentials found at: {kaggle_json}")
    print()
    
    try:
        # Download dataset using kagglehub
        print("📥 Downloading dataset: dataclusterlabs/indian-number-plates-dataset")
        print("This may take several minutes depending on your internet speed...")
        print()
        
        path = kagglehub.dataset_download("dataclusterlabs/indian-number-plates-dataset")
        
        print()
        print("✅ Download complete!")
        print(f"📁 Dataset downloaded to: {path}")
        print()
        
        # Create output directory if specified
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Copy or link to project directory
            print(f"📋 Dataset location: {path}")
            print(f"💡 You can copy files to: {output_path.absolute()}")
            print()
        
        # List downloaded files
        dataset_path = Path(path)
        if dataset_path.exists():
            files = list(dataset_path.rglob("*"))
            print(f"📊 Total files downloaded: {len(files)}")
            print()
            print("Sample files:")
            for i, file in enumerate(files[:10]):
                if file.is_file():
                    size = file.stat().st_size / (1024 * 1024)  # MB
                    print(f"  - {file.name} ({size:.2f} MB)")
            if len(files) > 10:
                print(f"  ... and {len(files) - 10} more files")
        
        print()
        print("=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print(f"1. Dataset path: {path}")
        print(f"2. Organize images into YOLO format (train/val/test)")
        print(f"3. Convert annotations to YOLO format (.txt files)")
        print(f"4. Update data/plates/data.yaml with paths")
        print(f"5. Start training with: python src/train.py")
        print()
        
        return path
        
    except Exception as e:
        print(f"❌ Error downloading dataset: {e}")
        print()
        print("Common issues:")
        print("1. Check internet connection")
        print("2. Verify Kaggle API credentials are correct")
        print("3. Ensure you've accepted dataset terms on Kaggle website")
        print("4. Visit: https://www.kaggle.com/datasets/dataclusterlabs/indian-number-plates-dataset")
        print()
        return None


def organize_dataset_for_yolo(source_path: str, yolo_dir: str = "data/plates"):
    """
    Organize downloaded dataset into YOLO format.
    
    Args:
        source_path: Path to downloaded Kaggle dataset
        yolo_dir: Output directory for YOLO-formatted data
    """
    print("\n📂 Organizing dataset for YOLO training...")
    
    source = Path(source_path)
    yolo_path = Path(yolo_dir)
    
    # Create YOLO directory structure
    for split in ['train', 'val', 'test']:
        (yolo_path / split / 'images').mkdir(parents=True, exist_ok=True)
        (yolo_path / split / 'labels').mkdir(parents=True, exist_ok=True)
    
    print(f"✅ YOLO directory structure created at: {yolo_path}")
    print("\n💡 Next: Use data/scripts/convert_annotations.py to convert annotations")
    print(f"   python data/scripts/convert_annotations.py --input {source_path} --output {yolo_dir}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download Indian Number Plates Dataset from Kaggle")
    parser.add_argument(
        '--output',
        type=str,
        default='data/kaggle_dataset',
        help='Output directory for dataset (default: data/kaggle_dataset)'
    )
    parser.add_argument(
        '--organize',
        action='store_true',
        help='Organize dataset into YOLO format after download'
    )
    
    args = parser.parse_args()
    
    # Download dataset
    dataset_path = download_indian_plates_dataset(args.output)
    
    # Organize if requested
    if dataset_path and args.organize:
        organize_dataset_for_yolo(dataset_path, 'data/plates')
