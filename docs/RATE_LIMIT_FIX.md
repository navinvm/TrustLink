# Rate Limit Fix - TrustLink

## Issue
Users were encountering **HTTP 429 (Rate Limit Exceeded)** errors when scanning URLs through the web interface.

### Error Message
```
Server returned 429: {
  "error": "Rate limit exceeded",
  "retry_after": 3600,
  "status": "error"
}
```

## Root Cause
The rate limiting was set too restrictively at **100 requests per hour** (hardcoded in `app.py` line 900), which was being shared across all users using the same IP address or session.

## Solution Implemented

### 1. **Configurable Rate Limits via Environment Variables**
Changed from hardcoded values to environment-configurable limits:

**Before:**
```python
if not rate_limiter.is_allowed(user_key, limit=100, window=3600):
```

**After:**
```python
rate_limit = int(os.environ.get('RATE_LIMIT_SCAN', 1000))
rate_window = int(os.environ.get('RATE_LIMIT_WINDOW', 3600))
if not rate_limiter.is_allowed(user_key, limit=rate_limit, window=rate_window):
```

### 2. **Increased Default Limits**
Updated default rate limits for better usability:
- **RATE_LIMIT_SCAN**: `100` → `1000` requests/hour
- **RATE_LIMIT_WINDOW**: `3600` seconds (1 hour)
- **RATE_LIMIT_BATCH**: `10` batch scans/hour
- **RATE_LIMIT_FEEDBACK**: `20` feedback submissions/hour  
- **RATE_LIMIT_RETRAIN**: `5` retrain requests/hour

### 3. **Enhanced Error Handling**
Improved frontend error messages with user-friendly feedback:

**JavaScript (vkz-scanner.js):**
```javascript
if (response.status === 429) {
    const retryAfter = errorData.retry_after || 3600;
    const minutes = Math.ceil(retryAfter / 60);
    throw new Error(`Rate limit exceeded. Please try again in ${minutes} minutes.`);
}
```

### 4. **Better Error Response**
Backend now returns more informative rate limit details:
```json
{
  "error": "Rate limit exceeded",
  "status": "error",
  "retry_after": 3600,
  "limit": 1000,
  "window": 3600
}
```

## Configuration

### Environment Variables (.env)
```bash
# Rate Limiting Configuration
RATE_LIMIT_SCAN=1000       # Max scans per user per hour
RATE_LIMIT_WINDOW=3600     # Time window in seconds (1 hour)
RATE_LIMIT_BATCH=10        # Max batch scans per hour
RATE_LIMIT_FEEDBACK=20     # Max feedback submissions per hour
RATE_LIMIT_RETRAIN=5       # Max retrain requests per hour
```

### Customization
To adjust rate limits for your deployment:

1. **Edit `.env` file**:
   ```bash
   RATE_LIMIT_SCAN=5000     # Increase to 5000 scans/hour
   RATE_LIMIT_WINDOW=1800   # Reduce window to 30 minutes
   ```

2. **Restart the application**:
   ```bash
   # Using Python directly
   python app.py
   
   # Or using the batch script
   start_trustlink.bat
   ```

## Testing

### Verify Configuration
```bash
# Check environment variables are loaded
python -c "import os; print('Rate Limit:', os.environ.get('RATE_LIMIT_SCAN', 'NOT SET'))"
```

### Test Scanning
1. Navigate to `/scanner` page
2. Scan multiple URLs in succession
3. Previously would fail after ~5 scans, now allows 1000/hour

## Files Modified

| File | Changes |
|------|---------|
| `app.py` | Made rate limits configurable via environment variables |
| `static/js/vkz-scanner.js` | Added user-friendly rate limit error handling |
| `.env` | Added rate limit configuration variables |
| `.env.example` | Updated with new rate limit settings |

## Benefits

✅ **Flexible Configuration**: Rate limits can be adjusted without code changes  
✅ **Better UX**: Users get clear feedback when rate limited  
✅ **Scalability**: Easy to adjust limits based on server capacity  
✅ **Development Friendly**: Higher default limits for testing  
✅ **Production Ready**: Can be lowered for production if needed  

## Recommendations

### Development Environment
- Keep `RATE_LIMIT_SCAN=1000` for easy testing
- Consider disabling rate limits entirely: `RATE_LIMIT_SCAN=999999`

### Production Environment
Adjust based on your infrastructure:
- **Small deployment**: `RATE_LIMIT_SCAN=500`
- **Medium deployment**: `RATE_LIMIT_SCAN=1000` (default)
- **Large deployment**: `RATE_LIMIT_SCAN=5000+`

### Per-User vs Per-IP
The current implementation uses:
```python
user_key = f"user:{session.get('user_id', request.remote_addr)}"
```

This means:
- **Logged-in users**: Rate limit per user ID
- **Anonymous users**: Rate limit per IP address

## Troubleshooting

### Still Getting 429 Errors?

1. **Check .env is loaded**:
   ```python
   import os
   print(os.environ.get('RATE_LIMIT_SCAN'))
   ```

2. **Clear rate limit cache** (if using Redis):
   ```bash
   redis-cli KEYS "trustlink:ratelimit:*" | xargs redis-cli DEL
   ```

3. **Restart the application** to apply changes

4. **Check logs** for rate limit violations:
   ```bash
   tail -f trustlink.log | grep "rate limit"
   ```

## Related Documentation
- [API Security Configuration](API_SECURITY_CONFIG.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Scalability Guide](SCALABILITY_GUIDE.md)

---

**Fixed:** 2026-02-08  
**Version:** v2.1+  
**Status:** ✅ Resolved
