# ClearCraft Deployment Guide

Complete guide for deploying ClearCraft in different environments.

---

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Production Deployment](#production-deployment)
4. [Cloud Platforms](#cloud-platforms)
5. [Environment Configuration](#environment-configuration)
6. [Monitoring & Logging](#monitoring--logging)
7. [Scaling & Performance](#scaling--performance)
8. [Security Considerations](#security-considerations)
9. [Troubleshooting](#troubleshooting)

---

## Local Development

### Quick Start

```bash
# Clone repository
git clone https://github.com/yourorg/clearcraft.git
cd clearcraft

# Run automated setup
./setup.sh

# Activate virtual environment
source venv/bin/activate

# Start development server
clearcraft server --reload
```

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Configure environment
cp .env.sample .env
# Edit .env with your settings

# Start server
uvicorn clearcraft.server:app --reload --host 0.0.0.0 --port 8000
```

### Development Tools

```bash
# Linting
ruff check clearcraft/

# Type checking
mypy clearcraft/

# Testing
pytest --cov=clearcraft

# Format code
ruff format clearcraft/
```

---

## Docker Deployment

### Single Container

```bash
# Build image
docker build -t clearcraft:latest .

# Run container
docker run -d \
  --name clearcraft \
  -p 8000:8000 \
  -e DEEPINFRA_API_TOKEN=your_token \
  -v clearcraft-cache:/app/.cache \
  clearcraft:latest

# View logs
docker logs -f clearcraft

# Stop container
docker stop clearcraft
```

### Docker Compose (Recommended)

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

### Custom Configuration

```yaml
# docker-compose.override.yml
version: '3.8'

services:
  clearcraft:
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
    ports:
      - "8080:8000"  # Custom port
```

```bash
docker-compose up -d
```

---

## Production Deployment

### Requirements

- **Python**: 3.10 or higher
- **RAM**: 2GB minimum, 4GB recommended (8GB for LLM mode)
- **Disk**: 5GB for application + models
- **CPU**: 2+ cores recommended

### Systemd Service (Linux)

```bash
# Create service file
sudo nano /etc/systemd/system/clearcraft.service
```

```ini
[Unit]
Description=ClearCraft Text Enhancement Service
After=network.target

[Service]
Type=simple
User=clearcraft
Group=clearcraft
WorkingDirectory=/opt/clearcraft
Environment="PATH=/opt/clearcraft/venv/bin"
EnvironmentFile=/opt/clearcraft/.env
ExecStart=/opt/clearcraft/venv/bin/uvicorn clearcraft.server:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable clearcraft
sudo systemctl start clearcraft

# Check status
sudo systemctl status clearcraft

# View logs
sudo journalctl -u clearcraft -f
```

### Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/clearcraft
upstream clearcraft {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name clearcraft.example.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name clearcraft.example.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/clearcraft.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/clearcraft.example.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Proxy settings
    location / {
        proxy_pass http://clearcraft;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts for long-running requests
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
    }

    # Static files (if served separately)
    location /static/ {
        alias /opt/clearcraft/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/clearcraft /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Cloud Platforms

### AWS EC2

```bash
# Launch Ubuntu 22.04 instance (t3.medium or larger)

# Install dependencies
sudo apt update
sudo apt install -y python3.10 python3.10-venv nginx

# Deploy application
cd /opt
sudo git clone https://github.com/yourorg/clearcraft.git
cd clearcraft
sudo chown -R ubuntu:ubuntu /opt/clearcraft

# Setup
./setup.sh
source venv/bin/activate

# Configure systemd service (see above)
# Configure nginx (see above)

# Setup SSL with Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d clearcraft.example.com
```

### AWS ECS (Docker)

```yaml
# task-definition.json
{
  "family": "clearcraft",
  "containerDefinitions": [
    {
      "name": "clearcraft",
      "image": "yourregistry/clearcraft:latest",
      "memory": 4096,
      "cpu": 2048,
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "HOST", "value": "0.0.0.0"},
        {"name": "PORT", "value": "8000"}
      ],
      "secrets": [
        {
          "name": "DEEPINFRA_API_TOKEN",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:clearcraft-api-token"
        }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/healthz || exit 1"],
        "interval": 30,
        "timeout": 10,
        "retries": 3
      },
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/clearcraft",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Run

```bash
# Build and push image
docker build -t gcr.io/PROJECT_ID/clearcraft:latest .
docker push gcr.io/PROJECT_ID/clearcraft:latest

# Deploy
gcloud run deploy clearcraft \
  --image gcr.io/PROJECT_ID/clearcraft:latest \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --timeout 120s \
  --set-env-vars "HOST=0.0.0.0,PORT=8080" \
  --set-secrets "DEEPINFRA_API_TOKEN=clearcraft-api-token:latest" \
  --allow-unauthenticated
```

### Heroku

```bash
# Create app
heroku create clearcraft-app

# Add buildpack
heroku buildpacks:set heroku/python

# Set config
heroku config:set DEEPINFRA_API_TOKEN=your_token

# Deploy
git push heroku main

# Scale
heroku ps:scale web=2:standard-2x
```

---

## Environment Configuration

### Production Settings

```bash
# .env.production
HOST=0.0.0.0
PORT=8000
DEBUG=false

# DeepInfra
DEEPINFRA_API_TOKEN=your_production_token
DEEPINFRA_MODEL=meta-llama/Llama-4-Maverick-17B

# Processing
MAX_TEXT_LENGTH=50000
CHUNK_SIZE=1000

# Quality Guardrails
MAX_CHANGE_RATIO=0.30
SIMILARITY_MIN=0.92
PRESERVE_CITATIONS=true

# Security & Privacy
ENABLE_DISCLOSURE=true
REDACT_PII_IN_LOGS=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/clearcraft/clearcraft.log
```

### Secrets Management

**AWS Secrets Manager:**
```bash
# Store secret
aws secretsmanager create-secret \
  --name clearcraft/deepinfra-token \
  --secret-string "your_token_here"

# Retrieve in code
import boto3

client = boto3.client('secretsmanager')
response = client.get_secret_value(SecretId='clearcraft/deepinfra-token')
token = response['SecretString']
```

**Docker Secrets:**
```bash
# Create secret
echo "your_token" | docker secret create deepinfra_token -

# Use in compose
services:
  clearcraft:
    secrets:
      - deepinfra_token
```

---

## Monitoring & Logging

### Health Checks

```bash
# Simple check
curl http://localhost:8000/healthz

# Comprehensive check
curl http://localhost:8000/api/health/comprehensive
```

### Prometheus Metrics (Optional)

```python
# Add to clearcraft/server.py
from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)
```

### Log Aggregation

**ELK Stack Example:**
```yaml
# docker-compose.yml
services:
  clearcraft:
    logging:
      driver: "fluentd"
      options:
        fluentd-address: localhost:24224
        tag: clearcraft
```

---

## Scaling & Performance

### Horizontal Scaling

```bash
# Multiple uvicorn workers
uvicorn clearcraft.server:app --workers 4

# Load balancer (nginx upstream)
upstream clearcraft {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
    server 127.0.0.1:8004;
}
```

### Caching

```python
# Redis caching for model embeddings
from redis import Redis
import pickle

cache = Redis(host='localhost', port=6379)

def get_cached_embedding(text: str):
    key = f"emb:{hash(text)}"
    cached = cache.get(key)
    if cached:
        return pickle.loads(cached)

    embedding = model.encode(text)
    cache.setex(key, 3600, pickle.dumps(embedding))
    return embedding
```

### Performance Tuning

```bash
# Optimize PyTorch
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4

# Increase file descriptors
ulimit -n 65536

# Tune kernel parameters
sudo sysctl -w net.core.somaxconn=65535
```

---

## Security Considerations

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### SSL/TLS Setup

```bash
# Let's Encrypt
sudo certbot --nginx -d clearcraft.example.com

# Auto-renewal
sudo crontab -e
# Add: 0 0 * * * certbot renew --quiet
```

### Rate Limiting (Nginx)

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=20;
    proxy_pass http://clearcraft;
}
```

---

## Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

**2. spaCy Model Not Found**
```bash
python -m spacy download en_core_web_sm
```

**3. Port Already in Use**
```bash
# Find process
lsof -i :8000

# Kill process
kill -9 PID
```

**4. Memory Issues**
```bash
# Increase swap (Linux)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Debug Mode

```bash
# Enable debug logging
DEBUG=true LOG_LEVEL=DEBUG clearcraft server
```

---

## Backup & Recovery

### Data Backup

```bash
# Backup configuration
tar -czf clearcraft-config-$(date +%Y%m%d).tar.gz \
  .env rules/ templates/

# Backup models (optional - can be re-downloaded)
tar -czf clearcraft-models-$(date +%Y%m%d).tar.gz .cache/
```

### Disaster Recovery

```bash
# Restore from backup
tar -xzf clearcraft-config-20250108.tar.gz

# Reinstall dependencies
pip install -r requirements.txt

# Download models
python -m spacy download en_core_web_sm

# Restart service
sudo systemctl restart clearcraft
```

---

## Support

- **Documentation**: See README.md, USAGE.md, METHODS.md
- **Issues**: https://github.com/yourorg/clearcraft/issues
- **Email**: support@clearcraft.example

---

**Last Updated**: 2025-01-08
**Version**: 1.0.0
