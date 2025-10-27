# Deployment Guide

## Overview
This guide covers deploying the Number Plate Detection System to production. The system requires:
- **Frontend**: Static React app (deployable to Vercel, Netlify, etc.)
- **Backend**: Python Flask API with ML models (requires server with Python support)

## Important Note About Vercel

⚠️ **Vercel has limitations for this project:**
- Vercel is optimized for **serverless functions** and **static sites**
- This project requires:
  - Heavy ML models (YOLOv7 - ~75MB)
  - GPU acceleration for real-time detection
  - WebSocket connections for live video streaming
  - Long-running processes

**Recommended deployment strategy:**
1. Deploy **Frontend only** to Vercel
2. Deploy **Backend** to a platform that supports Python with ML:
   - Railway
   - Render
   - Heroku
   - AWS EC2
   - Google Cloud Run
   - DigitalOcean

## Option 1: Frontend on Vercel + Backend Elsewhere (RECOMMENDED)

### Step 1: Deploy Backend to Railway/Render

#### Using Railway:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

#### Using Render:
1. Go to https://render.com
2. Create new "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python backend/app.py`
   - **Environment Variables**: Add from `.env.example`

### Step 2: Deploy Frontend to Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to project root
cd "c:\Users\HP\Desktop\new project"

# Deploy
vercel

# Follow prompts:
# - Set root directory to: frontend
# - Build command: npm run build
# - Output directory: dist
```

Or use Vercel Dashboard:
1. Go to https://vercel.com
2. Import Git Repository
3. Configure:
   - **Framework**: Vite
   - **Root Directory**: frontend
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### Step 3: Update Frontend API URL

Edit `frontend/src/App.jsx` or create environment variable:

```javascript
const API_URL = process.env.VITE_API_URL || 'https://your-backend-url.railway.app';
const SOCKET_URL = process.env.VITE_SOCKET_URL || 'https://your-backend-url.railway.app';
```

Create `frontend/.env.production`:
```bash
VITE_API_URL=https://your-backend-url.railway.app
VITE_SOCKET_URL=https://your-backend-url.railway.app
```

## Option 2: Full Deployment on AWS/GCP/Azure

### AWS EC2:
```bash
# SSH into EC2 instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Clone repository
git clone https://github.com/Co-ctrl-hash/detection-system.git
cd detection-system

# Run setup
chmod +x setup.sh
./setup.sh

# Install PM2 for process management
npm install -g pm2

# Start backend
pm2 start backend/app.py --interpreter python3 --name plate-backend

# Serve frontend with nginx
sudo apt install nginx
sudo cp frontend/dist/* /var/www/html/
```

## Option 3: Docker Deployment

### Build and Deploy:
```bash
# Build Docker image
docker build -t plate-detection -f docker/Dockerfile.gpu .

# Run container
docker run -d -p 5000:5000 -p 3000:3000 plate-detection

# Or use docker-compose
docker-compose up -d
```

### Deploy to Cloud:
```bash
# Tag for Docker Hub
docker tag plate-detection yourusername/plate-detection:latest

# Push to Docker Hub
docker push yourusername/plate-detection:latest

# Deploy on cloud provider's container service
# (AWS ECS, Google Cloud Run, Azure Container Instances)
```

## Environment Variables for Production

Create `.env` file on server:
```bash
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this
DATABASE_URL=postgresql://user:password@host:5432/dbname
MODEL_WEIGHTS=models/yolov7.pt
DEVICE=0  # GPU
CONF_THRESHOLD=0.25
CORS_ORIGINS=https://your-frontend-url.vercel.app
```

## Database Setup for Production

### PostgreSQL (Recommended):
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb plates_db

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://username:password@localhost/plates_db
```

### MySQL:
```bash
# Install MySQL
sudo apt install mysql-server

# Create database
mysql -u root -p
CREATE DATABASE plates_db;

# Update DATABASE_URL
DATABASE_URL=mysql://username:password@localhost/plates_db
```

## Frontend Build Configuration

Update `frontend/vite.config.js` for production:

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:5000',
        changeOrigin: true,
      },
      '/socket.io': {
        target: process.env.VITE_SOCKET_URL || 'http://localhost:5000',
        ws: true,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser',
  }
})
```

## Post-Deployment Checklist

- [ ] Backend is running and accessible
- [ ] Frontend can connect to backend API
- [ ] WebSocket connections working
- [ ] Database is properly migrated
- [ ] YOLOv7 weights are downloaded
- [ ] CORS origins are configured
- [ ] SSL certificates installed (use Let's Encrypt)
- [ ] Environment variables set correctly
- [ ] Monitoring and logging configured
- [ ] Backup strategy implemented

## Quick Deploy Commands

### Push to GitHub:
```powershell
git remote add origin https://github.com/Co-ctrl-hash/detection-system.git
git branch -M main
git push -u origin main
```

### Deploy Frontend to Vercel:
```bash
cd frontend
vercel --prod
```

### Deploy Backend to Railway:
```bash
railway up
```

## Monitoring

Set up monitoring for:
- API response times
- Detection accuracy
- Server resources (CPU, RAM, GPU)
- Error rates
- Database performance

Use tools like:
- Sentry (error tracking)
- Prometheus + Grafana (metrics)
- LogRocket (frontend monitoring)

## Support

For issues, check:
- Backend logs: `logs/app.log`
- Frontend console errors
- Network tab in browser DevTools
- Server resource usage

## Cost Estimates

### Free Tier Options:
- **Vercel**: Free for frontend (100GB bandwidth)
- **Railway**: $5/month (500 hours)
- **Render**: Free tier available (with limitations)

### Recommended Setup:
- **Frontend (Vercel)**: Free
- **Backend (Railway/Render)**: $5-20/month
- **Database (Railway/Render)**: Included
- **Total**: ~$10-20/month

### Enterprise Setup:
- **AWS EC2 (GPU instance)**: $500+/month
- **Database**: $50+/month
- **CDN**: $20+/month
- **Total**: $600+/month
