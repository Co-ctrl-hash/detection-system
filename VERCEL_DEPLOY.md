# Vercel Deployment Guide

## Important Note About Vercel Limitations

⚠️ **Vercel has serverless function limitations that make full YOLOv7 deployment challenging:**

- **File Size Limit**: 50MB (YOLOv7 model is 72MB)
- **Memory Limit**: 1GB (PyTorch + YOLOv7 needs ~2GB)
- **Execution Time**: 60s max (model loading takes 20-30s)

**Recommended Deployment Options:**

1. **Frontend Only on Vercel** (Recommended)
   - Deploy React frontend to Vercel
   - Host backend on Heroku/Railway/Render/DigitalOcean

2. **Lightweight API on Vercel**
   - Deploy minimal Flask API without YOLOv7
   - Use external API for heavy processing

3. **Full Deployment Alternatives**
   - Railway.app (Better for Python backends)
   - Render.com (Generous free tier)
   - Heroku (Classic choice)
   - DigitalOcean App Platform
   - Google Cloud Run
   - AWS Lambda (with container support)

## Option 1: Deploy Frontend to Vercel

### Step 1: Prepare Frontend

```bash
cd frontend
npm install
npm run build
```

### Step 2: Create `vercel.json` in frontend folder

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "VITE_API_URL": "https://your-backend-url.herokuapp.com"
  }
}
```

### Step 3: Deploy

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy from frontend directory
cd frontend
vercel
```

## Option 2: Deploy Backend to Railway.app (Recommended)

Railway.app is perfect for Python backends with no cold starts.

### Step 1: Create `railway.json`

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python run_app.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Step 2: Create `Procfile`

```
web: python run_app.py
```

### Step 3: Deploy

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Connect your GitHub repository
4. Select "Deploy from GitHub repo"
5. Choose `detection-system`
6. Add environment variables:
   - `DEVICE=cpu`
   - `MODEL_WEIGHTS=models/yolov7.pt`
   - `CONF_THRESHOLD=0.25`
7. Click "Deploy"

### Step 4: Get Your Railway URL

After deployment, you'll get a URL like:
`https://your-app.railway.app`

Update your frontend `.env` to point to this URL.

## Option 3: Deploy to Render.com

### Step 1: Create `render.yaml`

```yaml
services:
  - type: web
    name: plate-detection-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python run_app.py"
    envVars:
      - key: DEVICE
        value: cpu
      - key: MODEL_WEIGHTS
        value: models/yolov7.pt
      - key: CONF_THRESHOLD
        value: "0.25"
    plan: free
```

### Step 2: Deploy

1. Go to [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select `detection-system`
5. Render will auto-detect Python
6. Click "Create Web Service"

## Option 4: Full Docker Deployment (DigitalOcean/AWS/GCP)

For production with GPU support:

### 1. Build Docker Image

```bash
docker build -f docker/Dockerfile.cpu -t plate-detection:latest .
```

### 2. Test Locally

```bash
docker run -p 5000:5000 plate-detection:latest
```

### 3. Deploy to DigitalOcean

```bash
# Install doctl
brew install doctl  # macOS
# or download from https://github.com/digitalocean/doctl

# Authenticate
doctl auth init

# Create app
doctl apps create --spec .do/app.yaml

# or use DigitalOcean web interface
```

## Environment Variables for All Deployments

```bash
# Required
MODEL_WEIGHTS=models/yolov7.pt
DEVICE=cpu
CONF_THRESHOLD=0.25

# Optional
DATABASE_URL=postgresql://...  # or MongoDB URL
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this
MAX_UPLOAD_SIZE_MB=50
CORS_ORIGINS=https://your-frontend.vercel.app
```

## Post-Deployment Checklist

- [ ] Test `/api/health` endpoint
- [ ] Test image upload
- [ ] Check logs for errors
- [ ] Monitor memory usage
- [ ] Set up error tracking (Sentry)
- [ ] Configure CORS for frontend domain
- [ ] Add custom domain (optional)
- [ ] Set up SSL certificate (usually automatic)
- [ ] Add monitoring/alerting
- [ ] Document API endpoint URL

## Troubleshooting

### "Module not found" errors
```bash
# Ensure requirements.txt includes all dependencies
pip freeze > requirements.txt
```

### "Model file not found"
```bash
# Make sure models/ directory is committed to git
# Check .gitignore doesn't exclude *.pt files
git lfs track "*.pt"  # if using Git LFS
```

### "Out of memory" errors
- Increase server memory
- Use CPU-only deployment
- Consider model quantization
- Implement model caching

### Cold start delays
- Use Railway/Render (no cold starts on free tier)
- Implement health check warming
- Consider always-on instance

## Cost Comparison

| Platform | Free Tier | Best For |
|----------|-----------|----------|
| Vercel | Yes (Frontend) | React/Next.js apps |
| Railway | 500 hrs/month | Python backends, no cold starts |
| Render | 750 hrs/month | Full-stack apps |
| Heroku | No free tier | Enterprise (paid) |
| DigitalOcean | $5/month | Production, GPU support |
| AWS Lambda | Limited | Serverless, light workloads |

## Recommended Setup

**For Portfolio/Demo:**
- Frontend: Vercel (free)
- Backend: Railway.app (free 500 hrs)
- Database: MongoDB Atlas (free 512MB)

**For Production:**
- Frontend: Vercel (hobby plan)
- Backend: DigitalOcean ($12/month)
- Database: Managed PostgreSQL
- CDN: Cloudflare (free)

---

**Next Steps:**
1. Choose your deployment platform
2. Follow the specific guide above
3. Update frontend API URL
4. Test thoroughly
5. Share your live demo!

**Need help?** Open an issue on GitHub!
