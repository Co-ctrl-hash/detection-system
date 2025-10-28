"""
Download YOLOv7 pretrained weights for license plate detection.

This script downloads the official YOLOv7 model weights file.
"""
import requests
from pathlib import Path
from tqdm import tqdm

# Model URLs
MODELS = {
    'yolov7': 'https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7.pt',
    'yolov7-tiny': 'https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7-tiny.pt',
    'yolov7x': 'https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7x.pt',
}

def download_model(model_name='yolov7', output_dir='models'):
    """
    Download YOLOv7 model weights.
    
    Args:
        model_name: Model to download ('yolov7', 'yolov7-tiny', or 'yolov7x')
        output_dir: Directory to save the model file
    """
    if model_name not in MODELS:
        print(f"❌ Unknown model: {model_name}")
        print(f"Available models: {', '.join(MODELS.keys())}")
        return False
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Download URL
    url = MODELS[model_name]
    filename = f"{model_name}.pt"
    filepath = output_path / filename
    
    # Check if already exists
    if filepath.exists():
        print(f"✅ Model already exists: {filepath}")
        response = input("Do you want to re-download? (y/N): ")
        if response.lower() != 'y':
            return True
    
    print(f"📥 Downloading {model_name} from {url}")
    print(f"💾 Saving to: {filepath}")
    
    try:
        # Stream download with progress bar
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filepath, 'wb') as f, tqdm(
            desc=filename,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                size = f.write(chunk)
                pbar.update(size)
        
        print(f"✅ Download complete: {filepath}")
        print(f"📊 File size: {filepath.stat().st_size / (1024*1024):.2f} MB")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Download failed: {e}")
        if filepath.exists():
            filepath.unlink()
        return False


def main():
    """Main function."""
    print("=" * 60)
    print("YOLOv7 Model Downloader")
    print("=" * 60)
    print()
    print("Available models:")
    print("  1. yolov7       - Standard model (~75 MB, best accuracy)")
    print("  2. yolov7-tiny  - Lightweight model (~12 MB, faster)")
    print("  3. yolov7x      - Extra large model (~140 MB, highest accuracy)")
    print()
    
    # Get user choice
    choice = input("Select model to download (1-3) or press Enter for yolov7: ").strip()
    
    model_map = {
        '1': 'yolov7',
        '2': 'yolov7-tiny',
        '3': 'yolov7x',
        '': 'yolov7'
    }
    
    model_name = model_map.get(choice, 'yolov7')
    
    print()
    success = download_model(model_name)
    
    if success:
        print()
        print("=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Update your .env file:")
        print(f"   MODEL_WEIGHTS=models/{model_name}.pt")
        print(f"   DEVICE=cpu")
        print()
        print("2. Test the detector:")
        print("   python -c \"from backend.detector import PlateDetector; d = PlateDetector(device='cpu'); print('Model loaded:', d.model is not None)\"")
        print()
        print("3. Start the application:")
        print("   python backend/app.py")
        print()
    else:
        print()
        print("=" * 60)
        print("❌ DOWNLOAD FAILED")
        print("=" * 60)
        print()
        print("Manual download:")
        print(f"  URL: {MODELS[model_name]}")
        print(f"  Save to: models/{model_name}.pt")
        print()


if __name__ == '__main__':
    main()
