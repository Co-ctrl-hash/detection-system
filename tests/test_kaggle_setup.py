"""
Quick test script for Kaggle dataset download
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import kagglehub
    print("✅ kagglehub installed successfully")
    print(f"   Version: {kagglehub.__version__ if hasattr(kagglehub, '__version__') else 'Unknown'}")
except ImportError:
    print("❌ kagglehub not installed")
    print("   Run: pip install kagglehub")
    sys.exit(1)

# Check for Kaggle credentials
kaggle_config = Path.home() / ".kaggle" / "kaggle.json"
if kaggle_config.exists():
    print(f"✅ Kaggle credentials found at: {kaggle_config}")
else:
    print(f"⚠️  Kaggle credentials NOT found")
    print(f"   Expected location: {kaggle_config}")
    print()
    print("To set up Kaggle API:")
    print("1. Go to https://www.kaggle.com/settings")
    print("2. Create API token (downloads kaggle.json)")
    print("3. Move to:", kaggle_config.parent)

print()
print("Ready to download datasets!")
print()
print("Usage:")
print("  python data/scripts/download_kaggle_dataset.py")
