# Windows Encoding Fix - Unicode Characters

## Problem
Server failed to start on Windows with error:
```
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f680' in position 0: character maps to <undefined>
```

## Root Cause
Windows PowerShell and Command Prompt use cp1252 (Windows-1252) encoding by default, which cannot display Unicode emoji characters like 🚀, ✓, ⚠️, etc.

When Python's `print()` function tries to output these characters, it fails because the console cannot encode them.

## Solution Applied
Replaced all emoji characters in print statements with ASCII-safe alternatives:

### Files Modified (10 files):

1. **app/main.py**
   - `🚀` → `[STARTUP]`
   - `✓` → `[STARTUP]`
   - `👋` → `[SHUTDOWN]`

2. **app/services/email_service.py**
   - `⚠️` → `[WARNING]`
   - `✅` → `[SUCCESS]`
   - `❌` → `[ERROR]`

3. **app/llm/cost_tracker_v2.py**
   - `⚠` → `[WARNING]` (2 occurrences)

4. **app/llm/cache_v2.py**
   - `⚠` → `[WARNING]` (3 occurrences)
   - `✓` → `[SUCCESS]` (2 occurrences)

5. **app/findings/engine.py**
   - `⚠️` → `[WARNING]`

6. **app/database/database.py**
   - `✓` → `[SUCCESS]`

7. **app/config/redis_config.py**
   - `✓` → `[SUCCESS]`
   - `⚠` → `[WARNING]`

8. **app/adaptive/embedding_engine.py**
   - `✓` → `[SUCCESS]`

9. **app/adaptive/candidate_mapper.py**
   - `✓` → `[SUCCESS]`

10. **app/database/models.py**
    - Fixed `metadata` → `vendor_metadata` (unrelated, but part of startup fix)

## Benefits of ASCII-Safe Logging

1. **Cross-Platform Compatibility**: Works on Windows, Linux, and macOS
2. **Log File Friendly**: Can be saved to files without encoding issues
3. **Searchable**: Easy to grep/search for `[ERROR]`, `[WARNING]`, etc.
4. **CI/CD Compatible**: Works in automated pipelines and Docker containers
5. **Consistent**: Standardized logging format

## Alternative Solutions (Not Used)

### Option 1: Set UTF-8 Encoding (Not Reliable)
```python
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```
Problems: Doesn't always work, affects all print statements

### Option 2: Environment Variable (Requires User Action)
```bash
$env:PYTHONIOENCODING="utf-8"
```
Problems: Users must set it every time

### Option 3: Use Logger Instead (Overkill for Simple Prints)
```python
import logging
logging.info("Starting application...")
```
Problems: More complex setup, same encoding issues

## Verification
✅ Application loads successfully  
✅ Server starts without errors  
✅ All print statements work on Windows  
✅ No functionality affected  

## Testing

```bash
# Test application import
python -c "from app.main import app; print('[TEST] OK')"

# Start server
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Status
✅ **FIXED** - Application now starts successfully on Windows!
