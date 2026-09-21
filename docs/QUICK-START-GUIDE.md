# VAJRA CORE - QUICK START GUIDE

**Version:** 1.0  
**Status:** Phase 4 Complete, Phase 5 In Progress

---

## 🚀 GETTING STARTED (5 MINUTES)

### Prerequisites
- Docker & Docker Compose installed
- Git installed
- 8GB RAM minimum
- 20GB disk space

### Quick Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd Prototype1

# 2. Create environment file
cp .env.example .env

# 3. Generate JWT secret
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)" >> .env

# 4. Start all services
docker-compose up -d

# 5. Wait for services to be healthy (30 seconds)
docker-compose ps

# 6. Run database migrations
docker-compose exec backend alembic upgrade head

# 7. Create admin user
docker-compose exec backend python scripts/create_admin.py

# 8. Access the API
curl http://localhost:8000/health
```

### Default Credentials
```
Email: admin@vajracore.local
Password: VajraAdmin@2026
```

---

## 🔑 AUTHENTICATION FLOW

### 1. Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@vajracore.local",
    "password": "VajraAdmin@2026"
  }'
```

Response:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 2592000
  }
}
```

### 2. Use Token
```bash
TOKEN="eyJhbGciOiJIUzI1NiIs..."

curl -X GET http://localhost:8000/api/configs \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📤 UPLOAD & AUDIT WORKFLOW

### 1. Upload Configuration
```bash
curl -X POST http://localhost:8000/api/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@cisco_router.cfg"
```

Response:
```json
{
  "success": true,
  "data": {
    "config_id": "CFG-000001",
    "vendor": "Cisco",
    "vendor_confidence": 0.95
  }
}
```

### 2. Run Audit
```bash
curl -X POST http://localhost:8000/api/audits/CFG-000001/run \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
{
  "success": true,
  "data": {
    "audit_id": "AUD-000001",
    "compliance_score": 78.5,
    "risk_score": 42.3,
    "risk_level": "MEDIUM",
    "passed_count": 15,
    "failed_count": 8
  }
}
```

### 3. Get Findings
```bash
curl -X GET http://localhost:8000/api/audits/AUD-000001/findings \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Download Report
```bash
curl -X GET http://localhost:8000/api/audits/AUD-000001/report \
  -H "Authorization: Bearer $TOKEN" \
  -o audit_report.pdf
```

---

## 🖥️ DEVICE MANAGEMENT (PHASE 5)

### 1. Create Device
```bash
curl -X POST http://localhost:8000/api/devices \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "router-edge-01",
    "ip_address": "192.168.1.1",
    "vendor": "Cisco",
    "device_type": "ROUTER",
    "location": "DataCenter-1",
    "criticality": "HIGH"
  }'
```

### 2. List Devices
```bash
curl -X GET "http://localhost:8000/api/devices?vendor=Cisco&limit=50" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Bulk Import from CSV
```bash
curl -X POST http://localhost:8000/api/devices/bulk-import \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@devices.csv"
```

CSV Format:
```csv
hostname,ip_address,vendor,model,device_type,location,criticality
router-01,192.168.1.1,Cisco,ASR1000,ROUTER,DC1,HIGH
switch-01,192.168.1.2,Juniper,EX4300,SWITCH,DC1,MEDIUM
firewall-01,192.168.1.3,Fortinet,FG-100F,FIREWALL,DC1,CRITICAL
```

---

## 🔍 MONITORING & MANAGEMENT

### Service URLs
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Flower (Celery):** http://localhost:5555
- **MinIO Console:** http://localhost:9001

### Health Check
```bash
# Simple health
curl http://localhost:8000/health

# Detailed health
curl http://localhost:8000/health/detailed
```

### Check Services
```bash
# All services
docker-compose ps

# Logs
docker-compose logs -f backend
docker-compose logs -f celery-worker
docker-compose logs -f postgres
```

### Database Access
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U vajra -d vajra_core

# List tables
\dt

# Query users
SELECT email, role, is_active FROM users;
```

---

## 👥 USER MANAGEMENT

### Create User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "analyst@example.com",
    "password": "SecurePass@123",
    "full_name": "Security Analyst",
    "role": "SECURITY_ANALYST"
  }'
```

### Roles
- **SUPER_ADMIN:** Full system access
- **ADMIN:** Organization admin
- **SECURITY_ANALYST:** Security operations
- **AUDITOR:** Compliance auditing
- **VIEWER:** Read-only access

---

## 🔧 CONFIGURATION

### Environment Variables (.env)
```bash
# API
API_HOST=0.0.0.0
API_PORT=8000

# Authentication
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=43200

# Database
USE_POSTGRES=true
DATABASE_URL=postgresql://vajra:vajra_secure_2026@postgres:5432/vajra_core

# Redis
REDIS_URL=redis://redis:6379/0

# MinIO
USE_MINIO=true
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123

# Security
ENABLE_RATE_LIMITING=true
RATE_LIMIT_PER_MINUTE=60

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 🐛 TROUBLESHOOTING

### Common Issues

**1. "Cannot connect to database"**
```bash
# Check if Postgres is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

**2. "Token expired"**
```bash
# Get new token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@vajracore.local","password":"VajraAdmin@2026"}'
```

**3. "Rate limit exceeded"**
```bash
# Disable rate limiting temporarily
echo "ENABLE_RATE_LIMITING=false" >> .env
docker-compose restart backend
```

**4. "Celery tasks not running"**
```bash
# Check Celery worker
docker-compose logs celery-worker

# Restart worker
docker-compose restart celery-worker

# Check Flower
open http://localhost:5555
```

**5. "Migration failed"**
```bash
# Check migration status
docker-compose exec backend alembic current

# Rollback
docker-compose exec backend alembic downgrade -1

# Re-run
docker-compose exec backend alembic upgrade head
```

### Reset Everything
```bash
# Stop all services
docker-compose down -v

# Remove all data
docker volume rm vajra_postgres_data vajra_redis_data vajra_minio_data

# Start fresh
docker-compose up -d
docker-compose exec backend alembic upgrade head
docker-compose exec backend python scripts/create_admin.py
```

---

## 📊 API ENDPOINTS REFERENCE

### Authentication
```
POST   /auth/register         - Register user
POST   /auth/login           - Login
GET    /auth/me              - Get current user
POST   /auth/logout          - Logout
POST   /auth/change-password - Change password
POST   /auth/verify-token    - Verify token
```

### Configurations
```
POST   /api/upload           - Upload config
GET    /api/configs          - List configs
GET    /api/configs/{id}     - Get config
DELETE /api/configs/{id}     - Delete config
```

### Audits
```
POST   /api/audits/{config_id}/run   - Run audit
GET    /api/audits/{audit_id}        - Get audit
GET    /api/audits/review-queue      - Review queue
GET    /api/dashboard/summary        - Dashboard
GET    /api/audits/{audit_id}/report - Download report
```

### Findings
```
GET    /api/audits/{audit_id}/findings - Get findings
```

### Learning (AI)
```
POST   /api/learning/interpret        - Interpret syntax
GET    /api/learning/pending          - Get pending
POST   /api/learning/mapping          - Accept mapping
POST   /api/learning/mapping/{id}/reject - Reject
PATCH  /api/learning/mapping/{id}     - Update
```

### Jobs
```
GET    /api/jobs/{job_id}  - Get job status
GET    /api/jobs           - List jobs
DELETE /api/jobs/{job_id}  - Delete job
```

### Devices (Phase 5)
```
POST   /api/devices                   - Create device
GET    /api/devices                   - List devices
GET    /api/devices/{id}              - Get device
PATCH  /api/devices/{id}              - Update device
DELETE /api/devices/{id}              - Delete device
POST   /api/devices/bulk-import       - Bulk import
GET    /api/devices/stats/summary     - Statistics
```

---

## 🎯 NEXT STEPS

### For Development:
1. Explore API docs: http://localhost:8000/docs
2. Upload sample configurations
3. Run audits and review findings
4. Test device management
5. Check Celery tasks in Flower

### For Testing:
1. Create test users with different roles
2. Test RBAC permissions
3. Upload multiple configurations
4. Test bulk operations
5. Verify multi-tenancy isolation

### For Production:
1. Generate strong JWT secret
2. Set up SSL/TLS (reverse proxy)
3. Configure backups
4. Set up monitoring
5. Review security settings
6. Load test

---

## 📚 ADDITIONAL RESOURCES

- **Full Documentation:** See `docs/` folder
- **Phase 4 Report:** `docs/PHASE-4-FINAL-COMPLETION.md`
- **Phase 5 Requirements:** `docs/PHASE-5-REQUIREMENTS.md`
- **Implementation Tracker:** `docs/PHASE-5-6-IMPLEMENTATION-TRACKER.md`
- **Final Report:** `docs/FINAL-IMPLEMENTATION-REPORT.md`

---

## 🆘 SUPPORT

**Issues:**
- Check logs: `docker-compose logs`
- Review documentation
- Verify configuration

**Contact:**
- Project Team: Vajra Core Development
- Organization: NTRO

---

**Happy Auditing! 🛡️**
