# Build stage
FROM node:18-alpine AS build

# Set working directory
WORKDIR /frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY frontend/ ./

# Copy nginx configuration to build context
COPY deployment/nginx.conf ./nginx.conf

# Build the app
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built app from build stage
COPY --from=build /frontend/build /usr/share/nginx/html

# Copy nginx configuration from build stage
COPY --from=build /frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 