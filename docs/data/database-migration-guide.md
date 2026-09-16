# Database Migration Guide - Vajra Core

**Phase 0.5 Foundation - SQLite to PostgreSQL Migration**

---

## Overview

Vajra Core supports both SQLite (development) and PostgreSQL (production) databases through SQLAlchemy abstraction and Alembic migrations.

## Current Status

- **Development**: SQLite (`./data/sih26155.db`)
- **Production**: PostgreSQL (Docker container)
- **Migration Tool**: Alembic 1.13.1
- **ORM**: SQLAlchemy 2.0.23

---

## Database Modes

### Mode 1: SQLite (Current Default)

**Configuration** (.env):
```bash
USE_POSTGRES=false
DATABASE_URL=sqlite:///./data/sih26155.db
```

**Pros**:
- No Docker required
- Simple setup
- Good for development
- Automatic table creation

**Cons**:
- Single-writer
- No concurrent access
- Not production-ready

---

### Mode 2: PostgreSQL (Production-Ready)

**Configuration** (.env):
```bash
USE_POSTGRES=true
DATABASE_URL=postgresql://vajra:vajra_dev_password@localhost:5432/vajra_core
```

**Prerequisites**:
1. Docker Desktop running
2. PostgreSQL container started:
   ```powershell
   docker compose up -d postgres
   ```

**Pros**:
- Multi-user support
- ACID guarantees
- Concurrent access
- Production-grade
- Better performance at scale

**Cons**:
- Requires Docker
- More complex setup

---

## Alembic Setup

### Directory Structure

```
backend/
├── alembic/
│   ├── versions/
│   │   └── a281c81fb595_initial_schema_phase_0_5_foundation.py
│   ├── env.py          # Environment configuration
│   ├── README          # Alembic documentation
│   └── script.py.mako  # Migration template
├── alembic.ini         # Alembic configuration
└── app/
    └── database/
        └── models.py   # SQLAlchemy models
```

### Configuration Files

**alembic.ini**: Base configuration
- Script location
- Database URL (overridden by env.py)
- Logging configuration

**alembic/env.py**: Runtime configuration
- Imports Base metadata from models
- Reads DATABASE_URL from environment
- Configures online/offline modes

---

## Migration Commands

### Check Current Version

```powershell
cd backend
alembic current
```

### View Migration History

```powershell
alembic history --verbose
```

### Create New Migration

**Auto-generate** (recommended):
```powershell
alembic revision --autogenerate -m "Description of changes"
```

**Manual**:
```powershell
alembic revision -m "Description of changes"
```

### Apply Migrations

**Upgrade to latest**:
```powershell
alembic upgrade head
```

**Upgrade to specific revision**:
```powershell
alembic upgrade a281c81fb595
```

**Upgrade one version**:
```powershell
alembic upgrade +1
```

### Rollback Migrations

**Downgrade one version**:
```powershell
alembic downgrade -1
```

**Downgrade to specific revision**:
```powershell
alembic downgrade a281c81fb595
```

**Downgrade to base (remove all)**:
```powershell
alembic downgrade base
```

### Show SQL (Dry Run)

```powershell
alembic upgrade head --sql
```

---

## Migration Workflow

### 1. Development with SQLite

```powershell
# Start application (creates tables automatically)
cd backend
python -m uvicorn app.main:app --reload
```

Tables are created by `init_db()` in `app/database/database.py`.

### 2. Switching to PostgreSQL

**Step 1: Start PostgreSQL**
```powershell
docker compose up -d postgres
```

**Step 2: Verify Connection**
```powershell
docker exec vajra-postgres psql -U vajra -d vajra_core -c "SELECT version();"
```

**Step 3: Update Environment**

Edit `.env`:
```bash
USE_POSTGRES=true
DATABASE_URL=postgresql://vajra:vajra_dev_password@localhost:5432/vajra_core
```

**Step 4: Run Migrations**
```powershell
cd backend
alembic upgrade head
```

**Step 5: Verify Tables**
```powershell
docker exec vajra-postgres psql -U vajra -d vajra_core -c "\dt"
```

Should show: configurations, audits, findings, learned_mappings, compliance_rules

**Step 6: Start Application**
```powershell
python -m uvicorn app.main:app --reload
```

---

## Data Migration

### Migrating Existing Data from SQLite to PostgreSQL

**Step 1: Export SQLite Data**

```python
# backend/scripts/export_sqlite_data.py
import json
from app.database.database import SessionLocal
from app.database.models import Configuration, Audit, Finding, LearnedMapping

def export_data():
    db = SessionLocal()
    
    # Export configurations
    configs = db.query(Configuration).all()
    with open('data/export/configurations.json', 'w') as f:
        json.dump([{
            'config_id': c.config_id,
            'filename': c.filename,
            'original_filename': c.original_filename,
            'file_type': c.file_type,
            'status': c.status,
            'vendor': c.vendor,
            'vendor_confidence': c.vendor_confidence,
            'storage_path': c.storage_path,
            'sanitized_path': c.sanitized_path,
            'created_at': c.created_at.isoformat() if c.created_at else None
        } for c in configs], f, indent=2)
    
    print(f"Exported {len(configs)} configurations")
    
    # Export audits, findings, mappings similarly...
    
    db.close()

if __name__ == '__main__':
    export_data()
```

**Step 2: Import to PostgreSQL**

```python
# backend/scripts/import_to_postgres.py
import json
from datetime import datetime
from app.database.database import SessionLocal
from app.database.models import Configuration

def import_data():
    db = SessionLocal()
    
    # Import configurations
    with open('data/export/configurations.json', 'r') as f:
        configs = json.load(f)
    
    for config_data in configs:
        config = Configuration(
            config_id=config_data['config_id'],
            filename=config_data['filename'],
            original_filename=config_data['original_filename'],
            file_type=config_data['file_type'],
            status=config_data['status'],
            vendor=config_data['vendor'],
            vendor_confidence=config_data['vendor_confidence'],
            storage_path=config_data['storage_path'],
            sanitized_path=config_data['sanitized_path'],
            created_at=datetime.fromisoformat(config_data['created_at']) if config_data['created_at'] else None
        )
        db.add(config)
    
    db.commit()
    print(f"Imported {len(configs)} configurations")
    
    db.close()

if __name__ == '__main__':
    import_data()
```

---

## Schema Changes

### Adding a New Column

**Step 1: Update Model**

Edit `backend/app/database/models.py`:
```python
class Configuration(Base):
    # ... existing columns ...
    file_hash = Column(String(64), nullable=True)  # New column
```

**Step 2: Generate Migration**
```powershell
alembic revision --autogenerate -m "Add file_hash to configurations"
```

**Step 3: Review Generated Migration**

Check `backend/alembic/versions/xxxx_add_file_hash.py`

**Step 4: Apply Migration**
```powershell
alembic upgrade head
```

### Adding a New Table

**Step 1: Create Model**

```python
class FrameworkVersion(Base):
    __tablename__ = "framework_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    framework_name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    source_url = Column(String(500), nullable=True)
    retrieved_at = Column(DateTime, default=datetime.utcnow)
```

**Step 2: Generate Migration**
```powershell
alembic revision --autogenerate -m "Add framework_versions table"
```

**Step 3: Apply Migration**
```powershell
alembic upgrade head
```

---

## Troubleshooting

### Migration Out of Sync

**Symptoms**:
```
Target database is not up to date.
```

**Solution**:
```powershell
# Check current version
alembic current

# Check history
alembic history

# Stamp database to specific version
alembic stamp head
```

### Table Already Exists

**Symptoms**:
```
relation "configurations" already exists
```

**Solution**:

**Option 1: Stamp as migrated**
```powershell
# Mark migration as already applied
alembic stamp head
```

**Option 2: Fresh start**
```powershell
# Drop all tables (PostgreSQL)
docker exec vajra-postgres psql -U vajra -d vajra_core -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Run migrations
alembic upgrade head
```

### Cannot Connect to PostgreSQL

**Symptoms**:
```
could not connect to server: Connection refused
```

**Check**:
```powershell
# Is PostgreSQL running?
docker compose ps postgres

# Check logs
docker compose logs postgres

# Test connection
docker exec vajra-postgres psql -U vajra -d vajra_core -c "SELECT 1;"
```

### Alembic Cannot Import Models

**Symptoms**:
```
ModuleNotFoundError: No module named 'app'
```

**Solution**:

Ensure you're running from `backend/` directory:
```powershell
cd backend
alembic upgrade head
```

---

## Best Practices

### 1. Always Review Auto-generated Migrations

Auto-generate detects changes but may not capture intent:
```powershell
alembic revision --autogenerate -m "Add feature"
# Review the generated file before applying
```

### 2. Test Migrations on Development First

```powershell
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Test upgrade again
alembic upgrade head
```

### 3. Use Descriptive Migration Messages

**Good**:
```powershell
alembic revision -m "Add file_hash for provenance tracking"
```

**Bad**:
```powershell
alembic revision -m "Update"
```

### 4. Never Modify Applied Migrations

Once a migration is applied to production, create a new migration instead of modifying the old one.

### 5. Backup Before Major Migrations

```powershell
# PostgreSQL backup
docker exec vajra-postgres pg_dump -U vajra vajra_core > backup_before_migration.sql
```

---

## Future Enhancements

### Planned Schema Additions (Phase 0 onward)

1. **Users & Authentication**
   - users table
   - roles table
   - user_roles table

2. **Organizations & Multi-tenancy**
   - organizations table
   - organization_users table

3. **Devices**
   - devices table
   - device_configurations table (versioning)

4. **Framework Integration**
   - frameworks table
   - framework_versions table
   - framework_controls table
   - control_mappings table

5. **Enhanced Audit Trail**
   - audit_logs table (system events)
   - user_actions table

6. **Configuration Versioning**
   - configuration_history table
   - configuration_diffs table

---

## References

- Alembic Documentation: https://alembic.sqlalchemy.org/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- PostgreSQL Documentation: https://www.postgresql.org/docs/

---

**Document Version**: 0.5.0  
**Last Updated**: 2026-09-16  
**Status**: Phase 0.5 Foundation
