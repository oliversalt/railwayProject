# Word Embeddings Explorer 🔤

A modern web application for exploring semantic relationships between words using GloVe word embeddings. This project demonstrates a full-stack architecture with a static frontend hosted on GitHub Pages and a FastAPI backend deployed on Google Cloud Run.

![Architecture](https://img.shields.io/badge/Frontend-GitHub%20Pages-181717?logo=github)
![Backend](https://img.shields.io/badge/Backend-Google%20Cloud%20Run-4285F4?logo=google-cloud)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)

## ✨ Features

-   **Word Similarity**: Compare how semantically similar two words are (cosine similarity score)
-   **Nearest Neighbors**: Find the most similar words to any given word
-   **Word Analogies**: Solve word vector math problems (e.g., "king - man + woman = queen")
-   **Visual Equation Builder**: Interactive UI for building complex word analogies with +/- operators
-   **Real-time Loading Progress**: Live updates on model loading status with progress bar
-   **Mobile Responsive**: Works seamlessly on desktop, tablet, and mobile devices

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER'S BROWSER                           │
│          https://yourusername.github.io/repo                │
│                                                             │
│  [index.html] [script.js] [styles.css]                     │
│       ↓ (Static files served from GitHub Pages)            │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS API Requests
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            GOOGLE CLOUD RUN (Backend API)                   │
│     https://word-vector-api-xxx.a.run.app                  │
│                                                             │
│  • FastAPI application in Docker container                 │
│  • GloVe embeddings (400,000 words, 50 dimensions)         │
│  • Pre-loaded model for fast cold starts (~30-60s)         │
│  • Auto-scaling (0 to 10 instances)                        │
│  • Rate limiting (60 req/min default)                      │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 How It Works

### Word Embeddings

The application uses **GloVe (Global Vectors for Word Representation)**, a pre-trained word embedding model that converts words into 50-dimensional vectors. Words with similar meanings have vectors that are close together in this high-dimensional space.

### Frontend (GitHub Pages)

-   Pure HTML/CSS/JavaScript - no build process needed
-   Fetches data from the Cloud Run API
-   Interactive UI with real-time status updates
-   Polls `/loading-status` endpoint during model initialization

### Backend (Google Cloud Run)

-   **FastAPI**: High-performance Python web framework
-   **Gensim**: Library for loading and querying GloVe embeddings
-   **Docker**: Containerized deployment with model pre-downloaded during build
-   **CORS**: Configured to allow requests from any origin (can be restricted to GitHub Pages URL)

## 📋 API Endpoints

| Endpoint          | Method | Parameters            | Description                         |
| ----------------- | ------ | --------------------- | ----------------------------------- |
| `/health`         | GET    | -                     | Health check with model status      |
| `/loading-status` | GET    | -                     | Current loading progress (0-100%)   |
| `/similarity`     | GET    | `word1`, `word2`      | Cosine similarity between two words |
| `/neighbors`      | GET    | `word`, `topn`        | Most similar words                  |
| `/analogy`        | GET    | `a`, `b`, `c`, `topn` | Solve A - B + C = ?                 |

## 🛠️ Local Development

### Frontend Only

```bash
# Simply open index.html in a browser
# Or serve with Python
python -m http.server 8000
# Visit http://localhost:8000
```

### Backend (FastAPI)

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py
# API runs on http://localhost:8000
```

### Docker (Local)

```bash
# Build
docker build -t word-vector-api .

# Run
docker run -p 8080:8080 word-vector-api
# API runs on http://localhost:8080
```

## ☁️ Deployment

### Deploy Frontend to GitHub Pages

1. Push code to GitHub repository
2. Go to Settings → Pages
3. Source: Deploy from branch `main`, folder `/` (root)
4. Your site will be live at `https://yourusername.github.io/repo`

### Deploy Backend to Google Cloud Run

```bash
# Login and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com

# Build container image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/word-vector-api

# Deploy to Cloud Run
gcloud run deploy word-vector-api \
  --image gcr.io/YOUR_PROJECT_ID/word-vector-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 600 \
  --max-instances 10 \
  --cpu-boost
```

### Update Frontend with API URL

After deploying to Cloud Run, update `script.js` line 2:

```javascript
const API_BASE_URL = "https://your-cloud-run-url.a.run.app";
```

## 💰 Cost Estimates

**GitHub Pages**: Free for public repositories

**Google Cloud Run** (with 4GB RAM, 2 CPU):

-   Free tier: 2 million requests/month
-   Estimated cost: $3-10/month for light usage
-   Cold starts: 30-60 seconds (model loads from pre-downloaded file)
-   Optional: Set `--min-instances 1` for instant response (~$10-15/month)

## 🔒 Security

-   ✅ No API keys or secrets exposed
-   ✅ CORS configured (can be restricted to specific origins)
-   ✅ Rate limiting enabled (60 requests/minute default)
-   ✅ Input validation with regex patterns
-   ✅ All user inputs are sanitized and converted to lowercase
-   ✅ Public Cloud Run URL (unauthenticated) - suitable for demo/portfolio

## 📦 Files Structure

```
.
├── index.html          # Frontend UI
├── script.js           # Frontend logic & API calls
├── styles.css          # Modern dark theme styling
├── main.py             # FastAPI backend
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container configuration
├── .dockerignore       # Files to exclude from Docker build
├── .gitignore          # Files to exclude from Git
└── README.md           # This file
```

## 🎓 Learning Resources

-   [GloVe: Global Vectors for Word Representation](https://nlp.stanford.edu/projects/glove/)
-   [FastAPI Documentation](https://fastapi.tiangolo.com/)
-   [Google Cloud Run Docs](https://cloud.google.com/run/docs)
-   [Gensim Documentation](https://radimrehurek.com/gensim/)

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Feel free to fork, modify, and use this project for your own learning!

## ⚡ Performance Tips

-   **Faster Cold Starts**: Model is pre-downloaded in Docker image (reduces startup from 2-3 min to 30-60s)
-   **Keep Warm**: Use `--min-instances 1` to keep one instance always running
-   **Smaller Model**: Switch to `glove-twitter-25` for faster loading (edit `main.py` line 51)
-   **Caching**: Frontend uses status polling to show real-time loading progress

---

Built with ❤️ using FastAPI, GloVe, and Google Cloud Run
