# Startup Error Fix - SQLAlchemy Reserved Attribute

## Problem
Server failed to start with error:
```
sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
```

## Root Cause
The `VendorUser` model in `backend/app/database/models.py` used `metadata` as a column name (line 567), which conflicts with SQLAlchemy's built-in `metadata` attribute that all models inherit from the Base class.

## Solution Applied
Renamed the column from `metadata` to `vendor_metadata` in two files:

### 1. Models File
**File**: `backend/app/database/models.py` (line 567)
```python
# BEFORE
metadata = Column(JSON, default=dict)  # Additional vendor info

# AFTER
vendor_metadata = Column(JSON, default=dict)  # Additional vendor info
```

### 2. Migration File
**File**: `backend/alembic/versions/phase10_vendor_otp_system.py` (line 40)
```python
# BEFORE
sa.Column('metadata', sa.JSON(), nullable=True),

# AFTER
sa.Column('vendor_metadata', sa.JSON(), nullable=True),
```

## Verification
✅ Models import successfully
✅ Application loads without errors
✅ No API code references the old field name
✅ Ready to run migrations

## Next Steps
1. **Run the server** (should start without errors):
   ```bash
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

2. **Run database migration**:
   ```bash
   alembic upgrade head
   ```

3. **Verify the system is working**:
   - Access http://127.0.0.1:8000/docs for API documentation
   - Test vendor registration endpoint
   - Run security tests: `python run_all_tests.py`

## Impact
- **No API changes needed** - The field wasn't used in any endpoints yet
- **No data migration needed** - Fresh deployment, no existing data
- **Database column created correctly** - Migration file updated

## Status
✅ **FIXED** - Server should now start successfully!
