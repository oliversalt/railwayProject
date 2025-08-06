# Google Cloud Run Quick Setup

## 🚀 Super Simple Deployment

### One-Time Setup (5 minutes):
1. **Install Google Cloud CLI**: https://cloud.google.com/sdk/docs/install
2. **Login & Setup**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR-PROJECT-ID
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com
   ```

### Deploy (Single Command):
```bash
gcloud run deploy word-vector-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --timeout 3600
```

### That's it! 🎉

**You get:**
- **Free URL**: `https://word-vector-api-xxx-uc.a.run.app`
- **2M requests/month FREE**
- **1GB RAM** (double Railway's limit)
- **Auto-scaling to zero** (no idle costs)
- **10-30 second cold starts** (fastest among free options)

**Perfect for your Word Vector API!**
