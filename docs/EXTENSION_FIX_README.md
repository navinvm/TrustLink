# Browser Extension "Failed to fetch" Fix

## Problem
The browser extension was showing "Scan failed: Failed to fetch" error when trying to scan URLs.

## Root Cause
The Flask backend didn't have CORS (Cross-Origin Resource Sharing) enabled, which prevented the browser extension from making API requests to the server.

## Solution Applied

### 1. Added CORS Support to Flask App
- Installed `flask-cors` package
- Configured CORS to allow requests from browser extensions
- Enabled CORS for `/predict` and `/api/*` endpoints

### 2. Improved Error Handling in Extension
- Added timeout handling (15 seconds)
- Better error messages for common issues
- Helps users diagnose connection problems

## How to Apply the Fix

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install the new `flask-cors>=3.0.10` dependency.

### Step 2: Restart the TrustLink Server
```bash
# Stop the current server (Ctrl+C)
# Then restart it:
python app.py
```

Or if using the batch file:
```bash
start_trustlink.bat
```

### Step 3: Reload the Browser Extension
1. Open Chrome/Edge and go to `chrome://extensions/`
2. Find "TrustLink - Phishing Protection"
3. Click the reload icon (circular arrow)

### Step 4: Test the Extension
1. Click the TrustLink extension icon
2. Enter a URL (e.g., `https://google.com`)
3. Click "Scan URL"
4. You should now see results instead of "Failed to fetch"

## Troubleshooting

### Still Getting "Failed to fetch"?

#### Check 1: Is the server running?
```bash
# The server should show:
# * Running on http://127.0.0.1:5000
```

#### Check 2: Verify extension settings
1. Click extension icon
2. Click "Settings" (gear icon)
3. Check "API URL" is set to: `http://localhost:5000`
4. Save settings if changed

#### Check 3: Check browser console
1. Right-click extension popup → "Inspect"
2. Go to Console tab
3. Look for error messages

### Common Error Messages

| Error | Solution |
|-------|----------|
| "Cannot connect to TrustLink server" | Start the Flask server with `python app.py` |
| "Request timeout" | Server is slow - check server console for errors |
| "API Error (500)" | Server error - check Flask console for stack trace |
| "Invalid API key" | Remove API key in extension settings for local use |

## Technical Details

### CORS Configuration
```python
from flask_cors import CORS

CORS(app, resources={
    r"/predict": {"origins": "*"},
    r"/api/*": {"origins": "*"}
}, supports_credentials=True)
```

### Error Handling Improvements
- 15-second request timeout
- User-friendly error messages
- Network connectivity checks
- Server availability detection

## Production Deployment

For production, restrict CORS origins:

```python
CORS(app, resources={
    r"/predict": {"origins": ["https://yourdomain.com", "chrome-extension://*"]},
    r"/api/*": {"origins": ["https://yourdomain.com", "chrome-extension://*"]}
}, supports_credentials=True)
```

## Files Modified

1. `requirements.txt` - Added flask-cors
2. `app.py` - Added CORS configuration
3. `browser-extension/background.js` - Improved error handling
