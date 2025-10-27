# Vercel Deployment Guide

## ⚠️ Important Notice

**This project has been pushed to GitHub successfully!** ✅

However, **Vercel deployment has limitations** for this full-stack ML application:

### Why Vercel Alone Won't Work:
1. **Backend Requirements**: 
   - YOLOv7 model (~75MB) exceeds serverless function limits
   - Requires GPU acceleration for real-time detection
   - Needs WebSocket support for live video streaming
   - Long-running ML inference processes

2. **Vercel Strengths**:
   - Perfect for static React frontends
   - Serverless functions (limited to 50MB, 10s timeout)
   - Not suitable for heavy ML workloads

## ✅ Recommended Deployment Strategy

### Option 1: Hybrid Deployment (BEST for this project)

#### Frontend on Vercel (FREE):
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy frontend only
cd frontend
vercel --prod
```

#### Backend on Railway/Render:

**Railway** (Recommended - $5/month):
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init

# Deploy backend
railway up

# Add environment variables in Railway dashboard
```

**Or Render** (Free tier available):
1. Go to https://render.com
2. "New +" → "Web Service"
3. Connect GitHub: `Co-ctrl-hash/detection-system`
4. Configure:
   - **Name**: plate-detection-backend
   - **Root Directory**: (leave empty)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python backend/app.py`
5. Add Environment Variables from `.env.example`
6. Click "Create Web Service"

### Option 2: Full Docker Deployment

Deploy to platforms supporting Docker:
- **Render** (Docker support)
- **Railway** (Docker support)
- **Google Cloud Run**
- **AWS ECS**
- **Azure Container Instances**

```bash
# Build image
docker build -t plate-detection -f docker/Dockerfile.cpu .

# Test locally
docker run -p 5000:5000 -p 5173:5173 plate-detection

# Push to registry and deploy
```

### Option 3: Traditional VPS

Deploy to VPS with GPU:
- **DigitalOcean Droplets**
- **AWS EC2 (with GPU)**
- **Google Compute Engine**
- **Linode**

## 📋 Step-by-Step: Vercel Frontend + Railway Backend

### Step 1: Deploy Backend to Railway

1. **Go to Railway**:
   - Visit https://railway.app
   - Sign in with GitHub

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `Co-ctrl-hash/detection-system`

3. **Configure Backend**:
   - Railway will auto-detect it's a Python project
   - Add these environment variables in Railway dashboard:
     ```
     FLASK_ENV=production
     SECRET_KEY=your-secret-key-here
     MODEL_WEIGHTS=models/yolov7.pt
     DEVICE=cpu
     CONF_THRESHOLD=0.25
     DATABASE_URL=sqlite:///plates.db
     CORS_ORIGINS=https://your-vercel-app.vercel.app
     ```

4. **Get Backend URL**:
   - Railway will provide a URL like: `https://your-app.railway.app`
   - Copy this URL

### Step 2: Configure Frontend for Production

1. **Update Frontend Environment**:
   ```bash
   cd frontend
   
   # Edit .env.production
   notepad .env.production
   ```

2. **Add your Railway backend URL**:
   ```
   VITE_API_URL=https://your-app.railway.app
   VITE_SOCKET_URL=https://your-app.railway.app
   ```

### Step 3: Deploy Frontend to Vercel

1. **Via Vercel CLI**:
   ```bash
   # Install Vercel CLI
   npm install -g vercel
   
   # Login
   vercel login
   
   # Deploy
   cd frontend
   vercel --prod
   ```

2. **Or via Vercel Dashboard**:
   - Go to https://vercel.com
   - Click "Add New..." → "Project"
   - Import `Co-ctrl-hash/detection-system`
   - Configure:
     - **Framework Preset**: Vite
     - **Root Directory**: `frontend`
     - **Build Command**: `npm run build`
     - **Output Directory**: `dist`
   - Add Environment Variables:
     - `VITE_API_URL`: Your Railway backend URL
     - `VITE_SOCKET_URL`: Your Railway backend URL
   - Click "Deploy"

### Step 4: Update CORS in Backend

1. **Update Railway Environment Variables**:
   ```
   CORS_ORIGINS=https://your-vercel-app.vercel.app
   ```

2. **Redeploy Railway backend** (automatic on env change)

### Step 5: Test Deployment

1. Visit your Vercel URL: `https://your-app.vercel.app`
2. Test upload feature
3. Check browser console for API connection
4. Verify WebSocket connection for live detection

## 🔧 Troubleshooting

### CORS Errors:
- Make sure `CORS_ORIGINS` in Railway includes your Vercel URL
- Check Railway backend logs

### API Not Connecting:
- Verify `VITE_API_URL` in Vercel environment variables
- Check Railway backend is running
- Test backend directly: `https://your-app.railway.app/api/detections`

### WebSocket Fails:
- Railway supports WebSockets by default
- Check `VITE_SOCKET_URL` is correct
- Ensure frontend uses WSS (secure WebSocket) for HTTPS sites

### Model Loading Errors:
- Railway free tier has memory limits
- May need to upgrade Railway plan for YOLOv7
- Consider using ONNX optimized model

## 💰 Cost Breakdown

### Free Option:
- **Vercel**: Free (frontend)
- **Render**: Free tier (backend with limitations)
- **Total**: $0/month
- **Limitations**: Limited CPU, may be slow

### Recommended Option:
- **Vercel**: Free (frontend)
- **Railway**: $5/month (backend with better performance)
- **Total**: $5/month
- **Benefits**: Better performance, 500 hours/month

### Production Option:
- **Vercel**: Free (frontend)
- **Railway Pro**: $20/month (backend with GPU support)
- **Total**: $20/month
- **Benefits**: GPU acceleration, faster detection

## 📚 Additional Resources

- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs
- **Render Docs**: https://render.com/docs

## ✅ Current Status

- ✅ Code pushed to GitHub: https://github.com/Co-ctrl-hash/detection-system
- ✅ Ready for Vercel frontend deployment
- ✅ Ready for Railway/Render backend deployment
- ✅ Environment configuration files created
- ✅ Deployment documentation complete

## 🚀 Quick Deploy Commands

```bash
# Deploy Frontend to Vercel
cd frontend
vercel --prod

# Deploy Backend to Railway
railway login
railway init
railway up

# Or deploy everything with Docker
docker-compose up -d
```

## 📞 Need Help?

Check the full `DEPLOYMENT.md` for more deployment options including:
- AWS deployment
- Google Cloud deployment
- Docker deployment
- Traditional server setup
