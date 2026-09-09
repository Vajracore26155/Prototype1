# Troubleshooting Guide

## Issue: "Failed to run audit. Please try again."

### Symptoms
- When clicking "Run Audit" on the Configurations page, an error dialog appears
- Error message: "Failed to run audit. Please try again."
- Backend returns 500 Internal Server Error

### Root Cause
The database tables were not initialized. The application expected tables to exist but they were missing, causing SQLAlchemy to throw `OperationalError: no such table` errors.

### Solution
Run the database initialization script:

```bash
cd backend
python init_database.py
```

This script will:
1. Create all required database tables
2. Scan the uploads directory for existing configuration files
3. Import any existing files into the database
4. Display a summary of imported files

### When to Run Database Initialization

You need to run the initialization script:

1. **First time setup** - When setting up the project for the first time
2. **After schema changes** - When database models are updated
3. **Database corruption** - If the database file is deleted or corrupted
4. **Starting fresh** - To reset the database and re-import files

### Manual Database Initialization

If you prefer manual initialization:

```python
# Initialize database tables
from app.database import init_db
init_db()

# (Optional) Populate with existing files
from populate_db import populate_database
populate_database()
```

### Verifying the Fix

1. Check that configurations appear in the UI:
   - Navigate to http://localhost:5173/configurations
   - You should see uploaded configurations listed

2. Test running an audit:
   - Click "Run Audit" on any configuration with status "UPLOADED"
   - Should redirect to audit results page
   - Should show compliance score, findings, and risk level

3. Check via API:
   ```bash
   # List configurations
   curl http://localhost:8000/api/configurations
   
   # Run audit (replace CFG-XXXXXX with actual config ID)
   curl -X POST http://localhost:8000/api/audits/CFG-XXXXXX/run
   ```

### Database Location

The SQLite database is located at:
- **Path**: `backend/data/sih26155.db`
- **Relative to**: Backend directory (where the app runs)

⚠️ **Important**: The backend must be run from the `backend/` directory so that relative paths resolve correctly.

### Prevention

To prevent this issue in production:

1. **Add to deployment checklist**: Include database initialization as a deployment step
2. **Environment checks**: Add startup checks to verify database tables exist
3. **Better error messages**: Improve error handling to detect missing tables and provide helpful messages
4. **Database migrations**: Consider using Alembic for proper database migrations

### Related Files

- `backend/init_database.py` - Main initialization script
- `backend/app/database/database.py` - Database connection setup
- `backend/app/database/models.py` - Database table definitions
- `backend/data/sih26155.db` - SQLite database file

## Other Common Issues

### Issue: Frontend shows "No configurations yet"

**Cause**: Database is empty or backend is not running

**Solution**:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check database has data: `python init_database.py`
3. Check API returns data: `curl http://localhost:8000/api/configurations`

### Issue: "Configuration not found" when running audit

**Cause**: Configuration exists in database but files are missing

**Solution**:
1. Verify files exist in `backend/data/uploads/` and `backend/data/sanitized/`
2. Check database paths match actual file locations
3. Re-upload the configuration file if needed

### Issue: Audit fails with parser error

**Cause**: Unsupported vendor or malformed configuration file

**Solution**:
1. Check vendor detection is working: Look at vendor confidence score
2. Verify configuration file format matches vendor (Cisco/Fortinet)
3. Check parser logs for specific error messages
4. Add support for new vendor if needed

### Issue: CORS errors in browser console

**Cause**: Backend CORS settings don't include frontend URL

**Solution**:
1. Check `.env` file has correct `CORS_ORIGINS`
2. Default: `http://localhost:5173,http://localhost:3000`
3. Restart backend after changing `.env`

### Getting Help

If issues persist:

1. Check backend logs for detailed error messages
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Ensure Python 3.11+ is being used
4. Check that all required environment variables are set in `.env`
