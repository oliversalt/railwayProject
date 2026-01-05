"""
Word Vector API - FastAPI application for semantic word operations
Uses GloVe embeddings loaded into memory for fast vector operations
"""

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import gensim.downloader as api
from typing import List, Dict, Any, Optional
import logging
import uvicorn
import os
import gc
from datetime import datetime
from contextlib import asynccontextmanager
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to store the model
model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the GloVe model at startup and clean up at shutdown"""
    print("🚀 Starting Word Vector API...")
    
    # Initialize loading state
    app.state.model_loaded = False
    app.state.loading_status = "Starting up..."
    app.state.loading_progress = 0
    app.state.model = None
    
    try:
        print("📥 Loading GloVe model (downloading if needed - may take 5-10 minutes on first run)...")
        app.state.loading_status = "Downloading GloVe model..."
        app.state.loading_progress = 25
        
        import time
        start_time = time.time()
        
        app.state.loading_status = "Loading model into memory..."
        app.state.loading_progress = 50
        
        # Load the model
        print("Loading model...")
        app.state.model = api.load('glove-wiki-gigaword-50')
        print("Model loaded successfully!")
        
        app.state.loading_status = "Optimizing memory usage..."
        app.state.loading_progress = 75
        
        # Force garbage collection to optimize memory usage
        gc.collect()
        
        load_time = time.time() - start_time
        
        print(f"✅ GloVe model loaded successfully in {load_time:.1f} seconds!")
        print(f"📚 Vocabulary size: {len(app.state.model.key_to_index):,} words")
        print("🌐 API is ready!")
        
        # Mark model as loaded AFTER successful loading
        app.state.model_loaded = True
        app.state.loading_status = "Ready!"
        app.state.loading_progress = 100
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        import traceback
        traceback.print_exc()
        app.state.model = None
        app.state.model_loaded = False
        app.state.loading_status = f"Error: {str(e)}"
        app.state.loading_progress = 0
        # Don't raise - let the app start anyway so we can see the error
    
    yield
    
    print("🔄 Shutting down Word Vector API...")
    # Clean up resources
    if hasattr(app.state, 'model') and app.state.model:
        del app.state.model
    gc.collect()

# Create FastAPI app with lifespan events
app = FastAPI(
    title="Word Vector API",
    description="Semantic word operations using GloVe embeddings",
    version="1.0.0",
    lifespan=lifespan
)

# --- Security & Performance Middleware ---
# CORS: Allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now (can restrict to GitHub Pages URL later)
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"]
)

# Rate limiting: default + per-endpoint overrides
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return PlainTextResponse("Too Many Requests", status_code=429)

# Root endpoint - API info
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Word Vector API",
        "version": "1.0",
        "status": "running",
        "endpoints": ["/health", "/similarity", "/neighbors", "/analogy", "/most_similar"]
    }

@app.get("/similarity")
@limiter.limit("30/minute")
async def get_similarity(
    request: Request,
    word1: str = Query(..., description="First word", min_length=1, max_length=32, pattern=r"^[A-Za-z-]+$"),
    word2: str = Query(..., description="Second word", min_length=1, max_length=32, pattern=r"^[A-Za-z-]+$")
):
    """
    Calculate cosine similarity between two words
    
    Args:
        word1: First word for comparison
        word2: Second word for comparison
    
    Returns:
        JSON with similarity score between -1 and 1
    """
    # Check if model is loaded using app.state
    if not getattr(app.state, 'model_loaded', False) or not hasattr(app.state, 'model') or app.state.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Check if both words exist in vocabulary
        if word1.lower() not in app.state.model.key_to_index:
            raise HTTPException(status_code=404, detail=f"Word '{word1}' not found in vocabulary")
        if word2.lower() not in app.state.model.key_to_index:
            raise HTTPException(status_code=404, detail=f"Word '{word2}' not found in vocabulary")
        
        # Calculate similarity
        similarity = app.state.model.similarity(word1.lower(), word2.lower())
        
        return {
            "word1": word1.lower(),
            "word2": word2.lower(),
            "similarity": float(similarity)
        }
    
    except Exception as e:
        logger.error(f"Error calculating similarity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analogy")
@limiter.limit("30/minute")
async def solve_analogy(
    request: Request,
    a: str = Query(..., description="Word A in analogy A - B + C = ?", min_length=1, max_length=32, pattern=r"^[A-Za-z-]+$"),
    b: str = Query(..., description="Word B in analogy A - B + C = ?", min_length=1, max_length=32, pattern=r"^[A-Za-z-]+$"),
    c: str = Query(..., description="Word C in analogy A - B + C = ?", min_length=1, max_length=32, pattern=r"^[A-Za-z-]+$"),
    topn: int = Query(default=1, ge=1, le=20, description="Number of results to return")
):
    """
    Solve word vector analogy: A - B + C = ?
    Example: king - man + woman = queen
    
    Args:
        a: First word (positive)
        b: Second word (negative) 
        c: Third word (positive)
        topn: Number of results to return
    
    Returns:
        JSON with most similar words to the analogy result
    """
    # Check if model is loaded using app.state
    if not getattr(app.state, 'model_loaded', False) or not hasattr(app.state, 'model') or app.state.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Check if all words exist in vocabulary
        words = [a.lower(), b.lower(), c.lower()]
        for word in words:
            if word not in app.state.model.key_to_index:
                raise HTTPException(status_code=404, detail=f"Word '{word}' not found in vocabulary")
        
        # Solve analogy: a - b + c
        results = app.state.model.most_similar(
            positive=[a.lower(), c.lower()],
            negative=[b.lower()],
            topn=topn
        )
        
        return {
            "analogy": f"{a} - {b} + {c}",
            "results": [
                {
                    "word": word,
                    "similarity": float(score)
                }
                for word, score in results
            ]
        }
    
    except Exception as e:
        logger.error(f"Error solving analogy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/neighbors")
@limiter.limit("30/minute")
async def get_neighbors(
    request: Request,
    word: str = Query(..., description="Word to find neighbors for", min_length=1, max_length=32, pattern=r"^[A-Za-z-]+$"),
    topn: int = Query(default=10, ge=1, le=20, description="Number of neighbors to return")
):
    """
    Find the most similar words to a given word
    
    Args:
        word: Target word
        topn: Number of similar words to return
    
    Returns:
        JSON with most similar words and their similarity scores
    """
    # Check if model is loaded using app.state
    if not getattr(app.state, 'model_loaded', False) or not hasattr(app.state, 'model') or app.state.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Check if word exists in vocabulary
        if word.lower() not in app.state.model.key_to_index:
            raise HTTPException(status_code=404, detail=f"Word '{word}' not found in vocabulary")
        
        # Get most similar words
        similar_words = app.state.model.most_similar(word.lower(), topn=topn)
        
        return {
            "word": word.lower(),
            "neighbors": [
                {
                    "word": similar_word,
                    "similarity": float(score)
                }
                for similar_word, score in similar_words
            ]
        }
    
    except Exception as e:
        logger.error(f"Error finding neighbors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint for hosting platforms"""
    model_loaded = getattr(app.state, 'model_loaded', False)
    return {
        "status": "ready" if model_loaded else "initializing",
        "timestamp": datetime.now().isoformat(),
        "service": "Word Vector API",
        "model_loaded": model_loaded,
        "vocabulary_size": len(app.state.model.key_to_index) if model_loaded and hasattr(app.state, 'model') and app.state.model is not None else 0
    }


@app.get("/loading-status")
async def loading_status():
    """Get current loading status and progress"""
    return {
        "model_loaded": getattr(app.state, 'model_loaded', False),
        "loading_status": getattr(app.state, 'loading_status', 'Unknown'),
        "loading_progress": getattr(app.state, 'loading_progress', 0),
        "vocabulary_size": len(app.state.model.key_to_index) if getattr(app.state, 'model_loaded', False) and hasattr(app.state, 'model') and app.state.model else 0
    }


@app.get("/vocabulary")
async def get_vocabulary_info():
    """
    Get information about the loaded vocabulary
    
    Returns:
        JSON with vocabulary statistics
    """
    # Check if model is loaded using app.state
    if not getattr(app.state, 'model_loaded', False) or not hasattr(app.state, 'model') or app.state.model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "vocabulary_size": len(app.state.model.key_to_index),
        "vector_dimensions": app.state.model.vector_size,
        "sample_words": list(app.state.model.key_to_index.keys())[:20]  # First 20 words as sample
    }

if __name__ == "__main__":
    # Detect hosting platform and set appropriate port
    port = int(os.environ.get("PORT", 8000))
    
    # Check if running on various hosting platforms
    is_render = os.getenv('RENDER') is not None
    is_railway = os.getenv('RAILWAY_ENVIRONMENT') is not None
    is_heroku = os.getenv('DYNO') is not None
    
    if is_render:
        print("🌐 Detected Render.com hosting")
    elif is_railway:
        print("🚂 Detected Railway hosting")
    elif is_heroku:
        print("🟣 Detected Heroku hosting")
    else:
        print("💻 Running locally")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
