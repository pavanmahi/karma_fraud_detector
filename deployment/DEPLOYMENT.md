# Deployment Guide

This guide will help you deploy your Karma Fraud Detector application using Docker and various cloud platforms.

## 🐳 Docker Setup

### Prerequisites
- Docker installed on your machine
- Docker Compose (usually comes with Docker Desktop)

### Quick Start (Local Development)

1. **Build and run locally:**
   ```bash
   # Make the deployment script executable
   chmod +x deploy.sh
   
   # Build and start the application
   ./deploy.sh build
   ```

2. **Access your application:**
   - Backend API: http://localhost:8000
   - Frontend: http://localhost:3000
   - API Health Check: http://localhost:8000/api/health

3. **Stop the application:**
   ```bash
   ./deploy.sh stop
   ```

### Manual Docker Commands

If you prefer to run commands manually:

```bash
# Build the backend
docker build -t turtil-backend .

# Build the frontend
docker build -t turtil-frontend ./frontend

# Run with docker-compose
docker-compose up -d

# Stop services
docker-compose down
```

## ☁️ Cloud Deployment

### Option 1: Render.com (Recommended - Free Tier)

Render.com offers a generous free tier and is very easy to use.

#### Steps:

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Add Docker deployment configuration"
   git push origin main
   ```

2. **Create a Render account**
   - Go to [render.com](https://render.com)
   - Sign up with your GitHub account

3. **Deploy the Backend:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - **Name**: `turtil-backend`
     - **Environment**: `Docker`
     - **Region**: Choose closest to you
     - **Branch**: `main`
     - **Build Command**: `docker build -t turtil-backend .`
     - **Start Command**: `docker run -p $PORT:8000 turtil-backend`
     - **Health Check Path**: `/api/health`

4. **Deploy the Frontend:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - **Name**: `turtil-frontend`
     - **Environment**: `Docker`
     - **Root Directory**: `frontend`
     - **Build Command**: `docker build -t turtil-frontend .`
     - **Start Command**: `docker run -p $PORT:80 turtil-frontend`

5. **Update Frontend API URL:**
   - In the frontend service, add environment variable:
     - **Key**: `REACT_APP_API_URL`
     - **Value**: `https://your-backend-url.onrender.com`

### Option 2: Railway.app

Railway offers a simple deployment experience with good free tier.

#### Steps:

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy using the script:**
   ```bash
   ./deploy.sh railway
   ```

3. **Or deploy manually:**
   ```bash
   railway login
   railway init
   railway up
   ```

### Option 3: Fly.io

Fly.io offers global deployment with a generous free tier.

#### Steps:

1. **Install Fly CLI:**
   ```bash
   # macOS
   brew install flyctl
   
   # Windows
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   ```

2. **Deploy:**
   ```bash
   flyctl auth login
   flyctl launch
   flyctl deploy
   ```

### Option 4: Heroku

Heroku supports Docker deployments.

#### Steps:

1. **Install Heroku CLI:**
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Deploy:**
   ```bash
   heroku login
   heroku create your-app-name
   heroku container:push web
   heroku container:release web
   ```

## 🔧 Configuration

### Environment Variables

The application uses these environment variables:

- `PYTHONPATH`: Set to `/app` (already configured in Dockerfile)
- `PORT`: Port for the backend (set by cloud platforms)
- `REACT_APP_API_URL`: Backend API URL for frontend

### Health Checks

The backend includes a health check endpoint at `/api/health` that returns:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 📊 Monitoring

### Logs

View application logs:

```bash
# Local
docker-compose logs -f

# Render
# Use the Render dashboard

# Railway
railway logs

# Fly.io
flyctl logs
```

### Metrics

The application exposes these endpoints:
- `/api/health` - Health check
- `/api/version` - Version information

## 🚀 Production Considerations

### Security

1. **Environment Variables**: Never commit sensitive data
2. **HTTPS**: Most platforms provide HTTPS automatically
3. **CORS**: Configure CORS properly for production
4. **Rate Limiting**: Consider adding rate limiting for API endpoints

### Performance

1. **Caching**: Add Redis for session caching
2. **CDN**: Use a CDN for static assets
3. **Database**: Consider using a managed database service
4. **Monitoring**: Add application monitoring (e.g., Sentry)

### Scaling

1. **Horizontal Scaling**: Most platforms support auto-scaling
2. **Load Balancing**: Use multiple instances for high availability
3. **Database**: Use read replicas for heavy read workloads

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**: Make sure ports 8000 and 3000 are available
2. **Memory issues**: Increase memory limits in cloud platform settings
3. **Build failures**: Check Dockerfile syntax and dependencies
4. **Health check failures**: Verify the health endpoint is working

### Debug Commands

```bash
# Check container status
docker ps

# View container logs
docker logs <container_id>

# Access container shell
docker exec -it <container_id> /bin/bash

# Check network connectivity
docker network ls
```

## 📝 Next Steps

After deployment:

1. **Test the API**: Use the deployed API endpoints
2. **Update Frontend**: Point frontend to the deployed backend
3. **Set up CI/CD**: Automate deployments with GitHub Actions
4. **Add Monitoring**: Set up logging and monitoring
5. **Custom Domain**: Configure a custom domain name

## 🆘 Support

If you encounter issues:

1. Check the logs using the commands above
2. Verify your Docker configuration
3. Test locally first
4. Check platform-specific documentation
5. Review the troubleshooting section above 