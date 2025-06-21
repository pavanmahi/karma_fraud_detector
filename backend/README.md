# Karma Fraud Detector API

A machine learning API for detecting fraudulent karma activities on social platforms.

## Features

- **Fraud Detection**: Analyzes user karma logs to detect suspicious patterns
- **ML Models**: Uses scikit-learn and sentence transformers for analysis
- **FastAPI**: RESTful API with automatic documentation
- **Health Checks**: Built-in health monitoring

## API Endpoints

- `POST /api/analyze` - Analyze user karma logs for fraud
- `GET /api/health` - Health check endpoint
- `GET /api/version` - API version information

## Usage

Send a POST request to `/api/analyze` with user karma log data to get fraud analysis results.

## Model Information

This API uses trained machine learning models to detect:
- Suspicious upvote patterns
- Spam content detection
- Low-effort content identification
- Mutual upvote schemes 