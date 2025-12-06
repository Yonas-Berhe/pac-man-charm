# Combined Dockerfile for frontend + backend
# Multi-stage build for deployment

# ==================================
# Stage 1: Build Frontend
# ==================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY frontend/ .

# Set API URL for production build
ARG VITE_API_URL=/api/v1
ENV VITE_API_URL=$VITE_API_URL

# Build the application
RUN npm run build

# ==================================
# Stage 2: Production
# ==================================
FROM python:3.12-slim

WORKDIR /app

# Install nginx and supervisor
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy backend dependency files
COPY backend/pyproject.toml backend/uv.lock ./

# Install backend dependencies
RUN uv sync --frozen --no-dev

# Copy backend application code
COPY backend/ .

# Copy frontend build from builder stage
COPY --from=frontend-builder /app/frontend/dist /var/www/html

# Copy nginx configuration
COPY deploy/nginx.conf /etc/nginx/sites-available/default

# Copy supervisor configuration
COPY deploy/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose port
EXPOSE 80

# Start supervisor (manages nginx + uvicorn)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
