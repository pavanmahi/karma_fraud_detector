# Hugging Face Spaces compatible Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create cache directory with proper permissions
RUN mkdir -p /tmp/huggingface_cache && chmod 777 /tmp/huggingface_cache

# Set environment variables for cache
ENV HF_HOME=/tmp/huggingface_cache
ENV TRANSFORMERS_CACHE=/tmp/huggingface_cache
ENV SENTENCE_TRANSFORMERS_HOME=/tmp/huggingface_cache

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY model/ ./model/
COPY data/ ./data/

# Create the app.py file that HF Spaces expects
RUN echo 'import uvicorn\nfrom app.main import app\n\nif __name__ == "__main__":\n    uvicorn.run(app, host="0.0.0.0", port=7860)' > app.py

# Expose port (HF Spaces uses 7860)
EXPOSE 7860

# Set environment variables
ENV PYTHONPATH=/code
ENV PORT=7860

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=2 \
    CMD curl -f http://localhost:7860/api/health || exit 1

# Start the application
CMD ["python", "app.py"] 