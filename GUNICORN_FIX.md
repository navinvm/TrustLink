# Gunicorn Worker Boot Failure - Fixed

## Problem
```
File "/usr/local/lib/python3.9/site-packages/gunicorn/arbiter.py", line 241, in handle_chld
gunicorn.errors.HaltServer: <HaltServer 'Worker failed to boot.' 3>
```

## Root Cause
Worker processes were crashing during initialization due to:
1. Too many workers for serverless memory limits
2. Thread-based workers (`gthread`) causing issues
3. No preloading causing repeated initialization errors
4. Poor error visibility during worker crashes

## Solution Applied

### 1. Created Gunicorn Configuration File ✅
**File**: `gunicorn_config.py`

**Key Changes**:
- **Reduced workers**: From 4 to 2 (configurable via `GUNICORN_WORKERS`)
- **Changed worker class**: From `gthread` to `sync` for stability
- **Added preload_app**: True - loads app once, not per worker
- **Better error logging**: Detailed worker lifecycle callbacks
- **Graceful timeouts**: 30s for clean shutdowns

### 2. Created WSGI Entry Point ✅
**File**: `wsgi.py`

**Features**:
- Catches import errors during app initialization
- Provides detailed error messages
- Prevents worker crashes from propagating
- Returns proper 500 errors with diagnostics

### 3. Updated Deployment Configs ✅

#### **Procfile** (Railway/Heroku)
```procfile
web: python init_models.py && gunicorn wsgi:application --config gunicorn_config.py --preload
```

**Changes**:
- Uses `wsgi:application` instead of `app:app`
- Uses config file for all settings
- Added `--preload` flag

#### **Dockerfile**
```dockerfile
CMD ["gunicorn", "wsgi:application", "--config", "gunicorn_config.py", "--preload"]
```

## How It Works Now

### Worker Lifecycle:
```
1. 🚀 Master process starts
2. ✅ App preloaded ONCE (not per worker)
3. ✓ Worker 1 spawned
4. ✓ Worker 1 initialized
5. ✓ Worker 2 spawned
6. ✓ Worker 2 initialized
7. ✅ Server ready
```

### Error Handling:
- If app fails to import → Detailed error in logs
- If worker crashes → Gracefully respawned
- If worker times out → Clean shutdown with logs
- All errors visible in deployment logs

## Configuration Options

### Environment Variables:

```bash
# Number of workers (default: 2)
GUNICORN_WORKERS=2

# Port (default: 8080)
PORT=8080

# Timeout (default: 120s)
GUNICORN_TIMEOUT=120

# Environment
FLASK_ENV=production
```

### Adjust Workers for Your Platform:

**Vercel/Lambda**: 1 worker (single-instance)
**Railway Free**: 2 workers (recommended)
**Railway Pro**: 4 workers
**Docker**: 2-4 workers depending on CPU

## Troubleshooting

### Still Getting Worker Crashes?

1. **Check Memory Usage**:
   - Railway logs will show memory usage
   - Reduce workers if hitting limits
   - Set `GUNICORN_WORKERS=1` for testing

2. **Check Import Errors**:
   ```bash
   # Test locally
   python wsgi.py
   gunicorn wsgi:application --config gunicorn_config.py --check-config
   ```

3. **Enable Debug Mode**:
   ```bash
   # In gunicorn_config.py, temporarily set:
   loglevel = 'debug'
   reload = True
   ```

4. **Check for Circular Imports**:
   ```bash
   python -c "import app; print('OK')"
   ```

### Common Issues & Fixes:

| Issue | Cause | Fix |
|-------|-------|-----|
| Worker timeout | Model loading too slow | Increase timeout or preload |
| Memory limit | Too many workers | Reduce `GUNICORN_WORKERS` |
| Import errors | Missing dependencies | Check requirements.txt |
| File write errors | Read-only filesystem | Already handled by our fixes |

## Verification

### Test Locally:
```bash
# 1. Initialize models
python init_models.py

# 2. Test WSGI
python -c "from wsgi import application; print('WSGI OK')"

# 3. Start with gunicorn
gunicorn wsgi:application --config gunicorn_config.py

# 4. Test in browser
curl http://localhost:8080/health
```

### Expected Logs:
```
🚀 Starting TrustLink server...
✓ File logging enabled
✓ Model and vectorizer loaded successfully
✓ Worker 1234 spawned
✓ Worker 1234 initialized
✓ Worker 5678 spawned
✓ Worker 5678 initialized
✅ Server is ready. Listening on 0.0.0.0:8080
```

## Deployment

### Railway:
```bash
git add .
git commit -m "Fix: Gunicorn config + WSGI entry point for stable workers"
git push
```

Railway will use the updated `Procfile` automatically.

### Docker:
```bash
docker build -t trustlink .
docker run -p 5000:5000 trustlink
```

### Vercel:
Update `vercel.json` if needed, but Vercel uses serverless functions, not gunicorn.

## Files Added/Modified

| File | Status | Purpose |
|------|--------|---------|
| `gunicorn_config.py` | **NEW** | Optimized gunicorn settings |
| `wsgi.py` | **NEW** | Error-safe WSGI entry point |
| `Procfile` | Modified | Uses new config + wsgi |
| `Dockerfile` | Modified | Uses new config + wsgi |

## Why This Works

### Before:
- ❌ 4 workers (too many for serverless)
- ❌ `gthread` worker class (complex, can crash)
- ❌ No preloading (app loaded 4 times)
- ❌ Poor error messages on crash
- ❌ Direct app import (no error handling)

### After:
- ✅ 2 workers (configurable, serverless-friendly)
- ✅ `sync` worker class (simple, stable)
- ✅ Preload enabled (app loaded once)
- ✅ Detailed lifecycle logging
- ✅ WSGI wrapper with error handling

## Performance Impact

- **Startup**: Faster (preload reduces redundant loading)
- **Memory**: Lower (fewer workers, single app instance)
- **Stability**: Higher (better error handling)
- **Debugging**: Easier (detailed logs)

## Next Steps

1. **Commit and deploy** with the new configuration
2. **Monitor logs** for the detailed worker lifecycle messages
3. **Adjust workers** if needed based on platform limits
4. **Test thoroughly** with the health and predict endpoints

---

**Your gunicorn workers should now start successfully! 🎉**

The new configuration is optimized for serverless platforms while maintaining production-ready performance.
