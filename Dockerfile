# ---- Build frontend ----
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ---- Runtime: nginx + uvicorn via supervisord ----
FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx supervisor \
    && rm -rf /var/lib/apt/lists/*

# Backend
WORKDIR /backend
COPY backend/pyproject.toml .
RUN pip install --no-cache-dir -e .
COPY backend/app/ ./app/

# Frontend static files
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# Nginx config — replace Docker Compose service name with localhost
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
RUN sed -i 's|http://backend:8000|http://127.0.0.1:8000|g' /etc/nginx/conf.d/default.conf \
    && rm -f /etc/nginx/sites-enabled/default

# Supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/app.conf

EXPOSE 80
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/app.conf"]
