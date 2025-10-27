# Sample Assets

This directory contains sample images for testing the number plate detection system.

## Usage

Place test images here and run:

```powershell
python src\run_demo.py --yolov7-dir external\yolov7 --weights models\yolov7.pt --source assets\sample.jpg
```

## Sample Images

You can download sample license plate images from:

- **CCPD Dataset**: https://github.com/detectRecog/CCPD
- **UFPR-ALPR**: https://web.inf.ufpr.br/vri/databases/ufpr-alpr/
- **OpenImages**: https://storage.googleapis.com/openimages/web/index.html (search for "license plate")

## Creating Test Cases

For best results, include images with:
- Various lighting conditions (day/night/twilight)
- Different distances (close-up, medium, far)
- Different angles (frontal, angled, oblique)
- Occlusions (partial obstruction)
- Motion blur
- Different plate styles (regional variations)

## Example File Structure

```
assets/
├── test_day_frontal.jpg
├── test_night_angled.jpg
├── test_occluded.jpg
├── test_blurry.jpg
└── video_sample.mp4
```

## Privacy Notice

**Do not commit real license plate images to public repositories without anonymization.**

If creating test data:
- Use synthetic/generated plates
- Blur real plates in public images
- Obtain consent if using real plates
- Follow local privacy laws
