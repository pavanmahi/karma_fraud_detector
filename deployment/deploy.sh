#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    print_success "Docker is installed"
}

# Build and run locally
build_local() {
    print_status "Building and running application locally..."
    
    # Build images
    print_status "Building backend image..."
    docker build -t turtil-backend -f deployment/backend.Dockerfile .
    
    print_status "Building frontend image..."
    docker build -t turtil-frontend -f deployment/frontend.Dockerfile ./frontend
    
    # Run with docker-compose
    print_status "Starting services with docker-compose..."
    cd deployment && docker-compose up -d && cd ..
    
    print_success "Application is running!"
    print_status "Backend: http://localhost:8000"
    print_status "Frontend: http://localhost:3000"
    print_status "API Health: http://localhost:8000/api/health"
}

# Stop local services
stop_local() {
    print_status "Stopping local services..."
    cd deployment && docker-compose down && cd ..
    print_success "Services stopped"
}

# Deploy to Render
deploy_render() {
    print_status "Deploying to Render..."
    print_warning "Make sure you have:"
    print_warning "1. A Render account"
    print_warning "2. Your code pushed to GitHub"
    print_warning "3. Connected your GitHub repo to Render"
    
    print_status "To deploy:"
    print_status "1. Go to https://render.com"
    print_status "2. Create a new Web Service"
    print_status "3. Connect your GitHub repository"
    print_status "4. Select 'Docker' as the environment"
    print_status "5. Set build command: docker build -t turtil-backend -f deployment/backend.Dockerfile ."
    print_status "6. Set start command: docker run -p \$PORT:8000 turtil-backend"
    print_status "7. Set health check path: /api/health"
}

# Deploy to Railway
deploy_railway() {
    print_status "Deploying to Railway..."
    print_warning "Make sure you have Railway CLI installed: npm install -g @railway/cli"
    
    if command -v railway &> /dev/null; then
        print_status "Logging in to Railway..."
        railway login
        
        print_status "Deploying..."
        railway up
    else
        print_error "Railway CLI not found. Install with: npm install -g @railway/cli"
    fi
}

# Show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  build     Build and run application locally"
    echo "  stop      Stop local services"
    echo "  render    Deploy to Render.com"
    echo "  railway   Deploy to Railway.app"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build"
    echo "  $0 deploy_render"
}

# Main script
case "$1" in
    "build")
        check_docker
        build_local
        ;;
    "stop")
        stop_local
        ;;
    "render")
        deploy_render
        ;;
    "railway")
        deploy_railway
        ;;
    "help"|"--help"|"-h"|"")
        show_usage
        ;;
    *)
        print_error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac 