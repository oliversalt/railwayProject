"""
Word Vector API - FastAPI application for semantic word operations
Uses GloVe embeddings loaded into memory for fast vector operations
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import gensim.downloader as api
from typing import List, Dict, Any, Optional
import logging
import uvicorn
import os
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to store the model
model = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the GloVe model on startup and keep it in memory"""
    global model
    logger.info("Loading GloVe model...")
    try:
        # Load the 100-dimensional GloVe model
        model = api.load("glove-wiki-gigaword-100")
        logger.info(f"Model loaded successfully. Vocabulary size: {len(model.key_to_index)}")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise e
    
    yield
    
    # Cleanup (if needed)
    logger.info("Shutting down...")

# Create FastAPI app with lifespan events
app = FastAPI(
    title="Word Vector API",
    description="Semantic word operations using GloVe embeddings",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Word Vector API is running",
        "model_loaded": model is not None,
        "vocabulary_size": len(model.key_to_index) if model else 0
    }

@app.get("/similarity")
async def get_similarity(
    word1: str = Query(..., description="First word"),
    word2: str = Query(..., description="Second word")
):
    """
    Calculate cosine similarity between two words
    
    Args:
        word1: First word for comparison
        word2: Second word for comparison
    
    Returns:
        JSON with similarity score between -1 and 1
    """
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Check if both words exist in vocabulary
        if word1.lower() not in model.key_to_index:
            raise HTTPException(status_code=404, detail=f"Word '{word1}' not found in vocabulary")
        if word2.lower() not in model.key_to_index:
            raise HTTPException(status_code=404, detail=f"Word '{word2}' not found in vocabulary")
        
        # Calculate similarity
        similarity = model.similarity(word1.lower(), word2.lower())
        
        return {
            "word1": word1.lower(),
            "word2": word2.lower(),
            "similarity": float(similarity)
        }
    
    except Exception as e:
        logger.error(f"Error calculating similarity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analogy")
async def solve_analogy(
    a: str = Query(..., description="Word A in analogy A - B + C = ?"),
    b: str = Query(..., description="Word B in analogy A - B + C = ?"),
    c: str = Query(..., description="Word C in analogy A - B + C = ?"),
    topn: int = Query(default=1, description="Number of results to return")
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
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Check if all words exist in vocabulary
        words = [a.lower(), b.lower(), c.lower()]
        for word in words:
            if word not in model.key_to_index:
                raise HTTPException(status_code=404, detail=f"Word '{word}' not found in vocabulary")
        
        # Solve analogy: a - b + c
        results = model.most_similar(
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
async def get_neighbors(
    word: str = Query(..., description="Word to find neighbors for"),
    topn: int = Query(default=10, description="Number of neighbors to return")
):
    """
    Find the most similar words to a given word
    
    Args:
        word: Target word
        topn: Number of similar words to return
    
    Returns:
        JSON with most similar words and their similarity scores
    """
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Check if word exists in vocabulary
        if word.lower() not in model.key_to_index:
            raise HTTPException(status_code=404, detail=f"Word '{word}' not found in vocabulary")
        
        # Get most similar words
        similar_words = model.most_similar(word.lower(), topn=topn)
        
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

@app.get("/vocabulary")
async def get_vocabulary_info():
    """
    Get information about the loaded vocabulary
    
    Returns:
        JSON with vocabulary statistics
    """
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "vocabulary_size": len(model.key_to_index),
        "vector_dimensions": model.vector_size,
        "sample_words": list(model.key_to_index.keys())[:20]  # First 20 words as sample
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
