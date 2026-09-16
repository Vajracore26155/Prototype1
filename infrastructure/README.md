# Vajra Core Infrastructure

**Phase 0.5 Foundation - Production-Oriented Development Environment**

---

## Overview

This directory contains the infrastructure configuration for Vajra Core's production-ready development environment.

## Components

### Core Services

| Service | Purpose | Port | Default Credentials |
|---------|---------|------|---------------------|
| **PostgreSQL** | Primary database | 5432 | vajra / vajra_dev_password |
| **Redis** | Job queue & cache | 6379 | - / vajra_redis_password |
| **MinIO** | Object storage (S3-compatible) | 9000, 9001 | minioadmin / minioadmin123 |
| **Keycloak** | Authentication (optional) | 8080 | admin / admin_password |
| **Celery Worker** | Background jobs (optional) | - | - |
| **Flower** | Task monitoring (optional) | 5555 | admin / flower_password |

---

## Quick Start

### 1. Minimal Setup (Core Services Only)

Start PostgreSQL, Redis, and MinIO:

```powershell
docker compose up -d postgres redis minio minio-init
```

### 2. With Authentication

Start with Keycloak:

```powershell
docker compose --profile auth up -d
```

### 3. With Workers

Start with Celery workers:

```powershell
docker compose --profile workers up -d
```

### 4. Full Stack

Start everything:

```powershell
docker compose --profile auth --profile workers up -d
```

---

## Service Details

### PostgreSQL

**Image**: postgres:15-alpine  
**Container**: vajra-postgres

**Databases Created**:
- `vajra_core` - Main application database
- `keycloak` - Authentication database

**Extensions Enabled**:
- uuid-ossp - UUID generation
- pg_trgm - Text search
- pgcrypto - Cryptographic functions

**Connection String**:
```
postgresql://vajra:vajra_dev_password@localhost:5432/vajra_core
```

**Health Check**: `pg_isready` command

---

### Redis

**Image**: redis:7-alpine  
**Container**: vajra-redis

**Configuration**:
- Persistence: AOF enabled
- Password: vajra_redis_password

**Connection String**:
```
redis://:vajra_redis_password@localhost:6379/0
```

**Database Usage**:
- DB 0: Celery broker
- DB 1: Celery results
- DB 2: Application cache (future)

**Health Check**: PING command

---

### MinIO

**Image**: minio/minio:latest  
**Container**: vajra-minio

**Buckets Created**:
- `vajra-configs` - Configuration files
- `vajra-reports` - PDF reports
- `vajra-artifacts` - Generated artifacts

**Access Points**:
- API: http://localhost:9000
- Console: http://localhost:9001

**Credentials**:
- Access Key: minioadmin
- Secret Key: minioadmin123

**S3-Compatible Endpoint**:
```
http://localhost:9000
```

**Health Check**: /minio/health/live

---

### Keycloak (Optional - Profile: auth)

**Image**: quay.io/keycloak/keycloak:23.0  
**Container**: vajra-keycloak

**Admin Console**: http://localhost:8080  
**Admin Credentials**: admin / admin_password

**Database**: Separate PostgreSQL database (keycloak)

**Mode**: Development mode (start-dev)

**Realm**: vajra (to be created manually)

---

### Celery Worker (Optional - Profile: workers)

**Container**: vajra-celery-worker

**Purpose**: Background job processing for:
- Configuration parsing
- Compliance evaluation
- Report generation
- Bulk operations

**Concurrency**: 4 workers (configurable)

**Dependencies**:
- PostgreSQL
- Redis
- MinIO

---

### Flower (Optional - Profile: workers, monitoring)

**Container**: vajra-celery-flower  
**UI**: http://localhost:5555

**Purpose**: Real-time monitoring of Celery tasks

**Basic Auth**: admin / flower_password

---

## Environment Configuration

Copy `.env.example` to `.env` and configure:

```powershell
Copy-Item .env.example .env
```

### Key Variables

```bash
# Database
DATABASE_URL=postgresql://vajra:vajra_dev_password@localhost:5432/vajra_core
USE_POSTGRES=true

# Redis
REDIS_URL=redis://:vajra_redis_password@localhost:6379/0

# MinIO
MINIO_ENDPOINT=localhost:9000
USE_MINIO=true

# Keycloak (if using auth profile)
KEYCLOAK_ENABLED=true
```

---

## Management Commands

### Start Services

```powershell
# Core only
docker compose up -d

# With specific profile
docker compose --profile auth up -d
docker compose --profile workers up -d
```

### Stop Services

```powershell
docker compose down
```

### Stop and Remove Data

```powershell
docker compose down -v
```

### View Logs

```powershell
# All services
docker compose logs -f

# Specific service
docker compose logs -f postgres
docker compose logs -f redis
docker compose logs -f minio
```

### Check Status

```powershell
docker compose ps
```

### Restart Service

```powershell
docker compose restart postgres
```

---

## Health Checks

All services include health checks. Check status:

```powershell
docker compose ps
```

Healthy services show `healthy` in the STATUS column.

### Manual Health Checks

**PostgreSQL**:
```powershell
docker exec vajra-postgres pg_isready -U vajra -d vajra_core
```

**Redis**:
```powershell
docker exec vajra-redis redis-cli -a vajra_redis_password ping
```

**MinIO**:
```powershell
curl http://localhost:9000/minio/health/live
```

---

## Data Persistence

### Volumes

| Volume | Purpose | Location |
|--------|---------|----------|
| postgres_data | Database files | Docker volume |
| redis_data | Redis persistence | Docker volume |
| minio_data | Object storage | Docker volume |
| worker_data | Worker temp files | Docker volume |

### Backup

**PostgreSQL**:
```powershell
docker exec vajra-postgres pg_dump -U vajra vajra_core > backup.sql
```

**Restore**:
```powershell
Get-Content backup.sql | docker exec -i vajra-postgres psql -U vajra -d vajra_core
```

**MinIO**: Use MinIO Client (mc) or S3 tools

---

## Networking

All services are connected via `vajra-network` bridge network.

Internal hostnames:
- postgres
- redis
- minio
- keycloak

Services can communicate using these hostnames.

---

## Troubleshooting

### Port Conflicts

Check if ports are already in use:

```powershell
netstat -ano | findstr :5432
netstat -ano | findstr :6379
netstat -ano | findstr :9000
netstat -ano | findstr :8080
```

Change ports in `.env` file if needed.

### Database Connection Issues

1. Check PostgreSQL is healthy:
   ```powershell
   docker compose ps postgres
   ```

2. Check logs:
   ```powershell
   docker compose logs postgres
   ```

3. Test connection:
   ```powershell
   docker exec vajra-postgres psql -U vajra -d vajra_core -c "SELECT version();"
   ```

### MinIO Bucket Issues

Buckets are created by `minio-init` service. If missing:

```powershell
# Restart init service
docker compose up minio-init
```

### Redis Authentication

Redis requires password. Ensure REDIS_URL includes password:
```
redis://:vajra_redis_password@localhost:6379/0
```

### Keycloak Startup Issues

Keycloak takes 30-60 seconds to start. Check logs:

```powershell
docker compose logs keycloak
```

Wait for "Started Server" message.

---

## Security Notes

### Development Only

**WARNING**: These credentials are for DEVELOPMENT ONLY.

In production:
- Use strong, randomly generated passwords
- Use secrets management (Vault, AWS Secrets Manager)
- Enable TLS/SSL
- Use internal networks
- Implement proper backup strategies

### Change Default Passwords

Update in `.env`:
- POSTGRES_PASSWORD
- REDIS_PASSWORD
- MINIO_ROOT_PASSWORD
- KEYCLOAK_ADMIN_PASSWORD
- JWT_SECRET_KEY
- SECRET_KEY

---

## Profiles

Docker Compose profiles allow optional services:

| Profile | Services Included |
|---------|------------------|
| (default) | postgres, redis, minio |
| auth | + keycloak |
| workers | + celery-worker, celery-flower |
| monitoring | celery-flower only |

---

## Next Steps

After starting infrastructure:

1. **Run migrations** (PostgreSQL)
   ```powershell
   cd backend
   alembic upgrade head
   ```

2. **Verify health** checks pass

3. **Access consoles**:
   - MinIO Console: http://localhost:9001
   - Keycloak Admin: http://localhost:8080
   - Flower Monitoring: http://localhost:5555

4. **Test connectivity** from application

5. **Migrate data** from SQLite (if applicable)

---

## References

- Docker Compose Documentation: https://docs.docker.com/compose/
- PostgreSQL: https://www.postgresql.org/docs/
- Redis: https://redis.io/documentation
- MinIO: https://min.io/docs/
- Keycloak: https://www.keycloak.org/documentation
- Celery: https://docs.celeryq.dev/

---

**Status**: Phase 0.5 Foundation  
**Last Updated**: 2026-09-16  
**Maintainer**: Vajra Core Engineering Team
