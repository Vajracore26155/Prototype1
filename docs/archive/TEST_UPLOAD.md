# Upload Troubleshooting Guide

## Current Status ✅

Both servers are running:
- **Backend**: http://localhost:8000 ✅
- **Frontend**: http://localhost:5173 ✅

## Upload Flow

### What Should Happen:
1. Select a `.cfg` file on the Upload page
2. Click "Upload" button
3. File is sent to backend at `/api/config/upload`
4. Backend processes the file (masks secrets, detects vendor)
5. Success message appears
6. Auto-redirect to Configurations page after 2 seconds
7. Click "Run Audit" on the configuration
8. View audit results

### Recent Improvements:
- Added detailed error logging in the browser console
- Improved error message display
- Added upload and response logging

## Testing Steps

### 1. Check Browser Console
Open browser developer tools (F12) and:
- Go to the **Console** tab
- Try uploading a file
- Look for these messages:
  ```
  Uploading file: <filename> Size: <size>
  Upload response: {...}
  ```
- If you see errors, they will be detailed here

### 2. Test Backend Directly
You can test if the backend is receiving requests:
```powershell
# Check backend health
curl http://localhost:8000/health

# Check configurations list
curl http://localhost:8000/api/configurations
```

### 3. Check Network Tab
In browser dev tools:
- Go to the **Network** tab
- Try uploading
- Look for the request to `/api/config/upload`
- Check the Status (should be 200)
- Check the Response tab for the actual response

## Common Issues & Solutions

### Issue 1: "Upload failed" message
**Solution**: Check browser console for detailed error message (we just added this)

### Issue 2: CORS errors in console
**Symptoms**: Errors mentioning "blocked by CORS policy"
**Solution**: Backend is configured correctly for localhost:5173, should not occur

### Issue 3: Network error / timeout
**Symptoms**: "Network Error" in console
**Solution**: 
- Verify backend is running: `curl http://localhost:8000/health`
- Restart backend if needed

### Issue 4: File size too large
**Symptoms**: Error about file size
**Solution**: Files must be under 10MB

### Issue 5: Invalid file type
**Symptoms**: Error about unsupported file type
**Solution**: Only .cfg, .conf, .txt, .json files are supported

## What To Do Now

1. **Open your browser to**: http://localhost:5173/upload
2. **Open browser Developer Tools**: Press F12
3. **Go to Console tab**
4. **Try uploading a .cfg file**
5. **Send me the console output** - this will show the exact error

## Backend Logs

The backend server logs show successful uploads:
```
INFO: POST /api/config/upload HTTP/1.1 200 OK
```

This means the backend is working. If frontend shows "Upload failed", it's likely:
- A response parsing issue (now logged to console)
- A network connectivity issue (check console)
- A validation error (check console)

## Quick Test File

You can test with one of these existing files:
- `backend/data/uploads/1251968080d2.cfg`
- `backend/data/uploads/67765b96bbdf.cfg`

Just copy one to your desktop and try uploading it through the web interface.
