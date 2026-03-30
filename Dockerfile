# ---- Build frontend ----
FROM node:20-slim AS frontend-builder
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ---- Runtime: nginx + uvicorn ----
FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx \
    && rm -rf /var/lib/apt/lists/* \
    && rm -f /etc/nginx/sites-enabled/default

# Backend
WORKDIR /backend
COPY backend/pyproject.toml .
RUN pip install --no-cache-dir -e .
COPY backend/app/ ./app/

# Frontend static files
COPY --from=frontend-builder /app/dist /usr/share/nginx/html

# Nginx config (explicit 0.0.0.0:80 + proxy to localhost)
COPY docker/nginx.combined.conf /etc/nginx/conf.d/default.conf

# Startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

EXPOSE 80
CMD ["/start.sh"]
