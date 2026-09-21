# VAJRA CORE Deployment Guide

Complete guide for deploying VAJRA CORE to production.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Database Setup](#database-setup)
6. [Monitoring Setup](#monitoring-setup)
7. [Security Configuration](#security-configuration)
8. [Backup & Recovery](#backup--recovery)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

**Minimum:**
- 4 CPU cores
- 8 GB RAM
- 50 GB SSD storage
- Ubuntu 22.04 LTS or RHEL 8+

**Recommended:**
- 8+ CPU cores
- 16 GB+ RAM
- 100 GB+ SSD storage
- Load balancer for high availability

### Software Requirements

- Docker 24.0+ and Docker Compose 2.20+
- PostgreSQL 15+
- Redis 7+
- Python 3.11+
- Node.js 18+ (for frontend)

---

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/vajra-core.git
cd vajra-core
```

### 2. Configure Environment Variables

Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql://vajra:secure_password@postgres:5432/vajra
POSTGRES_USER=vajra
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=vajra

# Redis
REDIS_URL=redis://redis:6379/0

# Security
JWT_SECRET_KEY=your-secure-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# Application
APP_NAME=VAJRA-CORE
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Storage
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE_MB=100

# AI/ML
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=notifications@example.com
SMTP_PASSWORD=your-smtp-password
```

### 3. Generate Secrets

```bash
# Generate JWT secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate webhook secret
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Docker Deployment

### Production Deployment with Docker Compose

```bash
# Start all services
docker-compose -f docker-compose.production.yml up -d

# View logs
docker-compose -f docker-compose.production.yml logs -f

# Stop services
docker-compose -f docker-compose.production.yml down
```

### Build Custom Image

```bash
# Build production image
docker build -t vajra-core:latest -f docker/Dockerfile.production .

# Tag for registry
docker tag vajra-core:latest your-registry.com/vajra-core:v1.0.0

# Push to registry
docker push your-registry.com/vajra-core:v1.0.0
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  api:
    image: vajra-core:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://vajra:password@postgres:5432/vajra
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=vajra
      - POSTGRES_PASSWORD=secure_password
      - POSTGRES_DB=vajra
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: always

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    restart: always

volumes:
  postgres_data:
  redis_data:
```

---

## Kubernetes Deployment

### 1. Create Namespace

```bash
kubectl create namespace vajra
```

### 2. Create Secrets

```bash
# Database credentials
kubectl create secret generic vajra-db-secret \
  --from-literal=username=vajra \
  --from-literal=password=secure_password \
  -n vajra

# JWT secret
kubectl create secret generic vajra-jwt-secret \
  --from-literal=secret-key=your-jwt-secret \
  -n vajra
```

### 3. Deploy PostgreSQL

```yaml
# postgres-deployment.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: vajra
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: vajra-db-secret
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: vajra-db-secret
              key: password
        - name: POSTGRES_DB
          value: vajra
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 50Gi
```

### 4. Deploy VAJRA API

```yaml
# api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: vajra-api
  namespace: vajra
spec:
  replicas: 3
  selector:
    matchLabels:
      app: vajra-api
  template:
    metadata:
      labels:
        app: vajra-api
    spec:
      containers:
      - name: api
        image: your-registry.com/vajra-core:v1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: "postgresql://$(POSTGRES_USER):$(POSTGRES_PASSWORD)@postgres:5432/vajra"
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: vajra-jwt-secret
              key: secret-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: vajra-api
  namespace: vajra
spec:
  selector:
    app: vajra-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

### 5. Deploy with kubectl

```bash
kubectl apply -f postgres-deployment.yaml
kubectl apply -f api-deployment.yaml

# Check status
kubectl get pods -n vajra
kubectl get services -n vajra
```

---

## Database Setup

### 1. Initialize Database

```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Or in Kubernetes
kubectl exec -it vajra-api-xxx -n vajra -- alembic upgrade head
```

### 2. Create Admin User

```bash
# Connect to API container
docker-compose exec api python

# Or create via API
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "password": "SecurePassword123!",
    "role": "ADMIN"
  }'
```

### 3. Database Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U vajra vajra > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T postgres psql -U vajra vajra < backup_20260918.sql
```

---

## Monitoring Setup

### 1. Deploy Prometheus

```bash
cd monitoring
docker-compose up -d prometheus
```

### 2. Deploy Grafana

```bash
docker-compose up -d grafana

# Access Grafana: http://localhost:3000
# Default credentials: admin/admin
```

### 3. Import Dashboards

1. Login to Grafana
2. Go to Dashboards → Import
3. Upload `monitoring/grafana-dashboard.json`
4. Select Prometheus data source

### 4. Configure Alerts

```bash
# Test alert rules
promtool check rules monitoring/alert_rules.yml

# Reload Prometheus config
curl -X POST http://localhost:9090/-/reload
```

---

## Security Configuration

### 1. SSL/TLS Setup

```bash
# Generate self-signed certificate (development)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem

# For production, use Let's Encrypt:
certbot certonly --standalone -d api.vajra.example.com
```

### 2. Firewall Rules

```bash
# Allow only necessary ports
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw enable
```

### 3. Security Headers

Configured in `app/security/headers.py`:
- X-Frame-Options
- Content-Security-Policy
- Strict-Transport-Security
- X-Content-Type-Options

### 4. Rate Limiting

Configured in `app/security/rate_limiter.py`:
- 60 requests/minute (default)
- 5 requests/minute (auth)
- 10 requests/minute (uploads)

---

## Backup & Recovery

### Automated Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
docker-compose exec -T postgres pg_dump -U vajra vajra | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Configuration backup
tar -czf "$BACKUP_DIR/configs_$DATE.tar.gz" backend/.env backend/app/compliance/rules.yaml

# Uploads backup
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" backend/uploads/

# Keep only last 7 days
find "$BACKUP_DIR" -name "*.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

### Schedule with Cron

```bash
# Add to crontab
0 2 * * * /path/to/backup.sh >> /var/log/vajra-backup.log 2>&1
```

---

## Troubleshooting

### Check Logs

```bash
# Docker Compose
docker-compose logs -f api

# Kubernetes
kubectl logs -f vajra-api-xxx -n vajra

# Follow specific service
docker-compose logs -f postgres redis
```

### Common Issues

#### Database Connection Error

```bash
# Check database is running
docker-compose ps postgres

# Test connection
docker-compose exec api python -c "from app.database import engine; print(engine.connect())"
```

#### High Memory Usage

```bash
# Check container stats
docker stats

# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G
```

#### Slow API Responses

```bash
# Check system resources
docker stats
htop

# View slow queries
docker-compose exec postgres psql -U vajra -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"

# Check Redis
docker-compose exec redis redis-cli INFO stats
```

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/health/db

# Redis health
curl http://localhost:8000/health/redis
```

---

## Scaling

### Horizontal Scaling (Kubernetes)

```bash
# Scale API replicas
kubectl scale deployment vajra-api --replicas=5 -n vajra

# Autoscaling
kubectl autoscale deployment vajra-api \
  --cpu-percent=70 \
  --min=3 \
  --max=10 \
  -n vajra
```

### Vertical Scaling

Update resource limits in deployment configurations.

---

## Production Checklist

- [ ] Environment variables configured
- [ ] Secrets generated and secured
- [ ] Database initialized with migrations
- [ ] Admin user created
- [ ] SSL certificates installed
- [ ] Firewall configured
- [ ] Monitoring setup (Prometheus/Grafana)
- [ ] Backup script configured
- [ ] Log rotation configured
- [ ] Rate limiting enabled
- [ ] Security headers configured
- [ ] Health checks passing
- [ ] Load testing completed
- [ ] Disaster recovery plan documented

---

## Support

For deployment issues:
- Documentation: https://docs.vajra.example.com
- Issues: https://github.com/your-org/vajra-core/issues
- Email: support@vajra.example.com
