# Multi-stage build for complete application
# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-build

WORKDIR /app
# Copy frontend package files
COPY frontend/package*.json ./
# Install frontend dependencies
RUN npm ci --only=production

# Copy frontend source code
COPY frontend/ ./
# Build the React app
RUN npm run build

# Stage 2: Build Backend with Frontend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY app/ ./app/
COPY model/ ./model/
COPY data/ ./data/

# Copy built frontend from previous stage
COPY --from=frontend-build /app/build ./frontend/build

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 