FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the GloVe model during build (saves 2+ minutes on startup!)
RUN python -c "import gensim.downloader as api; api.load('glove-wiki-gigaword-50')"

# Copy application files
COPY main.py .
COPY wiki_giga_2024_50.txt .

# Expose port (Cloud Run uses PORT env var, default to 8080)
EXPOSE 8080

# Run the application
# Cloud Run sets the PORT environment variable, so we use it
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
