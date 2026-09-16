# Vajra Core Infrastructure Setup Guide

## Prerequisites

### 1. Docker Desktop Installation

**Status Check**:
```powershell
docker --version
docker compose version
```

If Docker is not installed:

**Windows**:
1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop/
2. Install and restart your computer
3. Start Docker Desktop application
4. Wait for "Docker Desktop is running" message

**Verify Docker is Running**:
```powershell
docker ps
```

Should return an empty list (not an error).

---

## Setup Options

Vajra Core supports multiple deployment modes:

### Option 1: Local Development (No Docker)

**Uses**:
- SQLite database
- Filesystem storage
- Synchronous processing

**Configuration** (.env):
```bash
USE_POSTGRES=false
USE_MINIO=false
FEATURE_ASYNC_PROCESSING=false
DATABASE_URL=sqlite:///./data/sih26155.db
```

**Start Application**:
```powershell
# Backend
cd backend
python -m uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm run dev
```

**Best For**:
- Quick testing
- Development without Docker
- Single-user scenarios

---

### Option 2: Hybrid Mode (Partial Docker)

**Uses**:
- PostgreSQL (Docker)
- Redis (Docker)
- MinIO (Docker)
- Application runs locally

**Start Infrastructure**:
```powershell
docker compose up -d postgres redis minio minio-init
```

**Configuration** (.env):
```bash
USE_POSTGRES=true
USE_MINIO=true
FEATURE_ASYNC_PROCESSING=false
DATABASE_URL=postgresql://vajra:vajra_dev_password@localhost:5432/vajra_core
MINIO_ENDPOINT=localhost:9000
```

**Run Migrations**:
```powershell
cd backend
alembic upgrade head
```

**Start Application**:
```powershell
# Backend
cd backend
python -m uvicorn app.main:app --reload

# Frontend (separate terminal)
cd frontend
npm run dev
```

**Best For**:
- Production-like development
- Testing with real databases
- Code debugging with local process

---

### Option 3: Full Docker Stack (Future)

**Uses**:
- All services in Docker
- Celery workers
- Full async processing

**Start Everything**:
```powershell
docker compose --profile workers up -d
```

**Best For**:
- Production simulation
- Performance testing
- Multi-worker scenarios

---

## Current Recommendation: Hybrid Mode

For Phase 0.5, we recommend **Hybrid Mode**:

1. Infrastructure in Docker (easy to manage)
2. Application running locally (easy to debug)
3. Production-ready data layer
4. Simple development workflow

---

## Step-by-Step Setup (Hybrid Mode)

### Step 1: Start Docker Desktop

```powershell
# Check if Docker is running
docker ps
```

If error, start Docker Desktop application and wait for it to be ready.

### Step 2: Start Infrastructure

```powershell
# From project root
docker compose up -d postgres redis minio minio-init
```

### Step 3: Verify Services

```powershell
docker compose ps
```

Should show:
- vajra-postgres (healthy)
- vajra-redis (healthy)
- vajra-minio (healthy)
- vajra-minio-init (exited 0 - this is normal)

### Step 4: Check Logs (If Issues)

```powershell
docker compose logs postgres
docker compose logs redis
docker compose logs minio
```

### Step 5: Configure Environment

```powershell
# Copy example if .env doesn't exist
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```

Edit `.env`:
```bash
USE_POSTGRES=true
USE_MINIO=true
DATABASE_URL=postgresql://vajra:vajra_dev_password@localhost:5432/vajra_core
MINIO_ENDPOINT=localhost:9000
```

### Step 6: Install Backend Dependencies (if not done)

```powershell
cd backend
pip install -r requirements.txt
```

### Step 7: Setup Database Migrations

```powershell
# Install Alembic
pip install alembic psycopg2-binary

# Initialize Alembic (if not done)
# alembic init alembic

# Run migrations
alembic upgrade head
```

### Step 8: Start Backend

```powershell
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 9: Start Frontend (Separate Terminal)

```powershell
cd frontend
npm run dev
```

### Step 10: Access Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

---

## Verification

### Test PostgreSQL Connection

```powershell
docker exec vajra-postgres psql -U vajra -d vajra_core -c "SELECT version();"
```

### Test Redis Connection

```powershell
docker exec vajra-redis redis-cli -a vajra_redis_password ping
```

Should return: `PONG`

### Test MinIO Console

Open http://localhost:9001 in browser
- Username: minioadmin
- Password: minioadmin123

Should see 3 buckets:
- vajra-configs
- vajra-reports
- vajra-artifacts

---

## Troubleshooting

### Docker Desktop Not Running

**Symptoms**:
```
failed to connect to the docker API
```

**Solution**:
1. Open Docker Desktop application
2. Wait for "Docker Desktop is running"
3. Run `docker ps` to verify

### Port Already in Use

**Symptoms**:
```
Bind for 0.0.0.0:5432 failed: port is already allocated
```

**Solution**:
```powershell
# Check what's using the port
netstat -ano | findstr :5432

# Either:
# 1. Stop the conflicting service, OR
# 2. Change port in .env file:
POSTGRES_PORT=5433
```

### PostgreSQL Not Healthy

**Check Logs**:
```powershell
docker compose logs postgres
```

**Common Issues**:
- Initialization script errors
- Permission problems
- Data volume corruption

**Solution**:
```powershell
# Stop and remove volumes
docker compose down -v

# Start fresh
docker compose up -d postgres
```

### MinIO Buckets Not Created

**Symptoms**:
- MinIO console shows no buckets

**Solution**:
```powershell
# Re-run init container
docker compose up minio-init
```

### Can't Connect from Application

**Check**:
1. Services are healthy: `docker compose ps`
2. Ports are accessible: `netstat -ano | findstr :5432`
3. Firewall not blocking localhost
4. Connection string in .env is correct

---

## Stopping Services

### Stop All Services

```powershell
docker compose down
```

### Stop But Keep Data

```powershell
docker compose stop
```

### Stop and Remove All Data

```powershell
docker compose down -v
```

**WARNING**: This deletes all database data!

---

## Data Management

### Backup PostgreSQL

```powershell
docker exec vajra-postgres pg_dump -U vajra vajra_core > backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').sql
```

### Restore PostgreSQL

```powershell
Get-Content backup_20260916_172615.sql | docker exec -i vajra-postgres psql -U vajra -d vajra_core
```

### Access PostgreSQL Shell

```powershell
docker exec -it vajra-postgres psql -U vajra -d vajra_core
```

### Access Redis CLI

```powershell
docker exec -it vajra-redis redis-cli -a vajra_redis_password
```

---

## Environment Variables Reference

### Database Selection

```bash
# Use PostgreSQL (Docker)
USE_POSTGRES=true
DATABASE_URL=postgresql://vajra:vajra_dev_password@localhost:5432/vajra_core

# Use SQLite (Local file)
USE_POSTGRES=false
DATABASE_URL=sqlite:///./data/sih26155.db
```

### Storage Selection

```bash
# Use MinIO (Docker)
USE_MINIO=true
MINIO_ENDPOINT=localhost:9000

# Use Filesystem (Local)
USE_MINIO=false
UPLOAD_DIR=./data/uploads
```

### Async Processing

```bash
# Enable Celery (Requires Redis)
FEATURE_ASYNC_PROCESSING=true
REDIS_URL=redis://:vajra_redis_password@localhost:6379/0

# Disable (Synchronous only)
FEATURE_ASYNC_PROCESSING=false
```

---

## Next Steps

After infrastructure is running:

1. ✅ **Verify Health Checks**
2. ✅ **Run Database Migrations**
3. ✅ **Test Application Startup**
4. ✅ **Upload Test Configuration**
5. ✅ **Run Audit**
6. ✅ **Verify Report Generation**

---

## Getting Help

### Check Status Dashboard

```powershell
docker compose ps
docker compose logs --tail=50
```

### View Resource Usage

```powershell
docker stats
```

### Full Infrastructure Reset

```powershell
# Stop everything
docker compose down -v

# Remove all Vajra images
docker images | Select-String vajra | ForEach-Object { docker rmi $_.ToString().Split()[0] }

# Start fresh
docker compose up -d postgres redis minio minio-init
```

---

**Document Version**: 0.5.0  
**Last Updated**: 2026-09-16  
**Status**: Phase 0.5 Foundation
