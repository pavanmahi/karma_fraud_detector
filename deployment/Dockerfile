# Ultra-lightweight build for Render free tier
# Stage 1: Build Frontend (minimal)
FROM node:18-alpine AS frontend-build

WORKDIR /app
# Copy only package files first for better caching
COPY frontend/package*.json ./
# Install only production dependencies
RUN npm ci --only=production --no-audit --no-fund

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# Stage 2: Minimal Backend
FROM python:3.11-slim

WORKDIR /app

# Install only curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy requirements and install with optimizations
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy only essential files
COPY app/ ./app/
COPY model/ ./model/
COPY data/ ./data/

# Copy frontend build
COPY --from=frontend-build /app/build ./frontend/build

# Expose port
EXPOSE 8000

# Environment variables
ENV PYTHONPATH=/app
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Simple health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=2 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start with single worker
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--log-level", "warning"] 