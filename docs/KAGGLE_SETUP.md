# Kaggle Dataset Integration Guide

## Overview
This project can automatically download the **Indian Number Plates Dataset** from Kaggle using the Kaggle API.

**Dataset**: https://www.kaggle.com/datasets/dataclusterlabs/indian-number-plates-dataset

---

## Setup Kaggle API Credentials

### Step 1: Get Your Kaggle API Key

1. **Go to Kaggle**: https://www.kaggle.com
2. **Login** to your account (or create one if you don't have it)
3. Click on your **profile picture** (top right)
4. Select **"Settings"**
5. Scroll down to **"API"** section
6. Click **"Create New API Token"**
7. This will download a file called **`kaggle.json`**

### Step 2: Install the API Key

#### On Windows:
```powershell
# Create .kaggle directory in your user folder
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.kaggle"

# Copy kaggle.json to the directory
Copy-Item "Downloads\kaggle.json" "$env:USERPROFILE\.kaggle\kaggle.json"

# Set file permissions (read-only for security)
icacls "$env:USERPROFILE\.kaggle\kaggle.json" /inheritance:r /grant:r "$env:USERNAME:R"
```

**Or manually**:
1. Open File Explorer
2. Navigate to `C:\Users\<YourUsername>\`
3. Create folder `.kaggle` (if it doesn't exist)
4. Move `kaggle.json` into `.kaggle` folder
5. Final path: `C:\Users\<YourUsername>\.kaggle\kaggle.json`

#### On Linux/Mac:
```bash
# Create .kaggle directory
mkdir -p ~/.kaggle

# Move kaggle.json
mv ~/Downloads/kaggle.json ~/.kaggle/

# Set permissions
chmod 600 ~/.kaggle/kaggle.json
```

---

## Download the Dataset

### Method 1: Using Our Download Script (Recommended)

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the download script
python data/scripts/download_kaggle_dataset.py
```

**With options**:
```powershell
# Download and organize for YOLO training
python data/scripts/download_kaggle_dataset.py --organize

# Specify custom output directory
python data/scripts/download_kaggle_dataset.py --output data/my_dataset
```

### Method 2: Direct Python Code

```python
import kagglehub

# Download latest version
path = kagglehub.dataset_download("dataclusterlabs/indian-number-plates-dataset")

print("Path to dataset files:", path)
```

### Method 3: Using Kaggle CLI

```powershell
# Install kaggle CLI
pip install kaggle

# Download dataset
kaggle datasets download -d dataclusterlabs/indian-number-plates-dataset

# Unzip
Expand-Archive indian-number-plates-dataset.zip -DestinationPath data/kaggle_dataset
```

---

## Dataset Information

### About the Dataset
- **Name**: Indian Number Plates Dataset
- **Source**: Kaggle (dataclusterlabs)
- **Size**: ~500MB - 2GB (varies by version)
- **Images**: Thousands of Indian vehicle number plates
- **Format**: Images with annotations

### What You'll Get
```
indian-number-plates-dataset/
├── images/              # License plate images
├── annotations/         # Bounding box annotations
└── metadata/            # Additional info
```

---

## After Download

### 1. Verify Download
```powershell
python data/scripts/download_kaggle_dataset.py
```

Output should show:
```
✅ Download complete!
📁 Dataset downloaded to: C:\Users\...\kagglehub\datasets\...
📊 Total files downloaded: XXXX
```

### 2. Organize for YOLO Training

Use our conversion script:
```powershell
python data/scripts/convert_annotations.py `
  --input <path-to-kaggle-dataset> `
  --output data/plates `
  --format kaggle
```

This will create:
```
data/plates/
├── train/
│   ├── images/          # Training images
│   └── labels/          # YOLO format labels (.txt)
├── val/
│   ├── images/          # Validation images
│   └── labels/          # YOLO format labels
└── test/
    ├── images/          # Test images
    └── labels/          # YOLO format labels
```

### 3. Update Configuration

Edit `data/plates/data.yaml`:
```yaml
# Dataset paths
train: data/plates/train/images
val: data/plates/val/images
test: data/plates/test/images

# Number of classes
nc: 1

# Class names
names: ['plate']
```

### 4. Start Training

```powershell
python src/train.py
```

---

## Troubleshooting

### Error: "Kaggle API credentials not found"

**Solution**:
1. Make sure `kaggle.json` is in the correct location
2. Windows: `C:\Users\<YourUsername>\.kaggle\kaggle.json`
3. Linux/Mac: `~/.kaggle/kaggle.json`

### Error: "403 Forbidden"

**Solution**:
1. Go to dataset page: https://www.kaggle.com/datasets/dataclusterlabs/indian-number-plates-dataset
2. Click "Download" to accept terms
3. Try downloading again

### Error: "Unauthorized"

**Solution**:
1. Regenerate your API token on Kaggle
2. Download new `kaggle.json`
3. Replace old `kaggle.json` with new one

### Download is Slow

**Solution**:
- Dataset is large (500MB - 2GB)
- Download speed depends on your internet
- Use `--output` flag to specify local directory

### Dataset Already Downloaded

**Solution**:
- Kagglehub caches downloads in `~/.cache/kagglehub/`
- Delete cache to re-download: `rm -rf ~/.cache/kagglehub/`
- Or use the cached version (path shown in output)

---

## Alternative Datasets

If you prefer other datasets, modify the script:

```python
# CCPD Dataset (Chinese plates)
path = kagglehub.dataset_download("your-dataset-slug")

# Custom dataset
path = kagglehub.dataset_download("username/dataset-name")
```

---

## Integration with Project

### Update `.env` File

```bash
# Add dataset path
KAGGLE_DATASET_PATH=/path/to/downloaded/dataset
```

### Use in Training

The downloaded dataset will automatically be detected by:
- `src/train.py` - Training script
- `data/scripts/convert_annotations.py` - Annotation converter
- `data/scripts/download_datasets.py` - Dataset manager

---

## Quick Start Commands

```powershell
# 1. Setup Kaggle credentials (one-time)
# Follow steps above to get kaggle.json

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Download dataset
python data/scripts/download_kaggle_dataset.py

# 4. Convert to YOLO format
python data/scripts/convert_annotations.py --input <dataset-path> --output data/plates

# 5. Start training
python src/train.py
```

---

## Summary

✅ **Installed**: `kagglehub` package
✅ **Script**: `data/scripts/download_kaggle_dataset.py`
✅ **Integration**: Ready to download Indian number plates dataset
✅ **Automatic**: Dataset conversion to YOLO format available

**Next**: Set up your Kaggle API credentials and run the download script!
