# 🧪 TrustLink Testing Guide

## Quick Start Testing (5 Minutes)

### Test 1: Start the Application
```bash
# Run the startup script
.\start_with_api_key.ps1

# Wait for this message:
# ✓ Learning system enabled
```

**Expected:** Application starts on http://localhost:5000

---

### Test 2: Web Interface Test

1. **Open browser:** http://localhost:5000
2. **Register account:**
   - Click "Register"
   - Username: testuser
   - Email: test@example.com
   - Password: password123
3. **Expected:** Redirected to dashboard

---

### Test 3: Basic URL Scanning

**Scan these URLs to test:**

1. **Safe URL:**
   ```
   http://www.google.com
   ```
   Expected: "Safe" prediction, medium-high confidence

2. **Google Test Malware:**
   ```
   http://testsafebrowsing.appspot.com/s/malware.html
   ```
   Expected: "Phishing" or "Safe" (ML prediction) + external validation shows THREAT

3. **Google Test Phishing:**
   ```
   http://testsafebrowsing.appspot.com/s/phishing.html
   ```
   Expected: External validation confirms PHISHING

---

### Test 4: External Validation

1. **Login to TrustLink**
2. **Go to API Keys page:** http://localhost:5000/api-keys
3. **Create new API key**
4. **Copy the key**
5. **Test validation:**

**Using PowerShell:**
```powershell
$apiKey = "your-trustlink-api-key-here"
$headers = @{
    "X-API-Key" = $apiKey
    "Content-Type" = "application/json"
}

$body = @{
    url = "http://testsafebrowsing.appspot.com/s/malware.html"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/v1/validate-external" -Method Post -Headers $headers -Body $body
```

**Expected Response:**
```json
{
  "status": "success",
  "validation": {
    "is_threat": true,
    "confidence": 0.92,
    "consensus": "threat",
    "sources": [...]
  }
}
```

---

### Test 5: Check Training Data

**Using PowerShell:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/v1/training-stats" -Headers @{"X-API-Key"=$apiKey}
```

**Expected:**
```json
{
  "status": "success",
  "total_available": 5,
  "pending_feedback": 0,
  "by_source": [...]
}
```

---

## Complete Testing Checklist

### ✅ Frontend Tests

- [ ] Homepage loads
- [ ] Registration works
- [ ] Login works
- [ ] Dashboard displays statistics
- [ ] URL scanning works (anonymous)
- [ ] URL scanning works (logged in)
- [ ] Scan history displays
- [ ] Analytics page loads with charts
- [ ] API keys page works
- [ ] Logout works

### ✅ ML Prediction Tests

- [ ] Scan safe URL (google.com) → Returns "Safe"
- [ ] Scan suspicious URL → Returns prediction with confidence
- [ ] Prediction completes in < 2 seconds
- [ ] Results show risk level (low/medium/high)
- [ ] Advanced features work (DNS, SSL, etc.)

### ✅ Learning System Tests

- [ ] External validation API works
- [ ] Google Safe Browsing validates correctly
- [ ] VirusTotal validates correctly
- [ ] PhishTank validates correctly
- [ ] Results cached (second request faster)
- [ ] Training data accumulated
- [ ] Training stats endpoint works

### ✅ API Tests

- [ ] Health endpoint: GET /health
- [ ] Predict endpoint: POST /predict
- [ ] External validation: POST /api/v1/validate-external
- [ ] Training stats: GET /api/v1/training-stats
- [ ] Model history: GET /api/v1/model-history
- [ ] Feedback submission: POST /api/v1/feedback

### ✅ Database Tests

- [ ] Users table working
- [ ] Scan history saved
- [ ] API keys generated
- [ ] Training data stored
- [ ] External validations cached
- [ ] Analytics data updated

### ✅ Security Tests

- [ ] API requires authentication
- [ ] Passwords hashed (not plain text)
- [ ] API keys hashed in database
- [ ] Invalid API key rejected
- [ ] SQL injection protected

---

## Performance Testing

### Test Response Times

**Create test script:** `test_performance.py`

```python
import requests
import time

BASE_URL = "http://localhost:5000"

# Test 1: Prediction speed
start = time.time()
response = requests.post(
    f"{BASE_URL}/predict",
    json={"url": "http://test.com"}
)
duration = time.time() - start

print(f"Prediction time: {duration:.2f} seconds")
print(f"Expected: < 2 seconds")
print(f"Result: {'PASS' if duration < 2 else 'FAIL'}")

# Test 2: Cached validation (should be fast)
api_key = "your-api-key"
headers = {"X-API-Key": api_key}

# First request (not cached)
start = time.time()
requests.post(
    f"{BASE_URL}/api/v1/validate-external",
    json={"url": "http://google.com"},
    headers={**headers, "Content-Type": "application/json"}
)
first_time = time.time() - start

# Second request (cached)
start = time.time()
response = requests.post(
    f"{BASE_URL}/api/v1/validate-external",
    json={"url": "http://google.com"},
    headers={**headers, "Content-Type": "application/json"}
)
cached_time = time.time() - start

print(f"\nFirst validation: {first_time:.2f}s")
print(f"Cached validation: {cached_time:.2f}s")
print(f"Speedup: {first_time/cached_time:.1f}x")
```

---

## Model Retraining Test

### Test Learning Pipeline

1. **Scan 10+ URLs** (mix of safe and phishing)
2. **Check training data:**
   ```bash
   GET /api/v1/training-stats
   ```
3. **Trigger retraining:**
   ```powershell
   $body = @{
       min_confidence = 0.7
       verified_only = $false
   } | ConvertTo-Json
   
   Invoke-RestMethod -Uri "http://localhost:5000/api/v1/retrain" `
       -Method Post -Headers $headers -Body $body -ContentType "application/json"
   ```

4. **Check model history:**
   ```bash
   GET /api/v1/model-history
   ```

**Expected:** New model version with metrics

---

## Demo Testing Script

**For your capstone presentation:**

### Demo Flow (5 Minutes)

1. **Start Application** (30 seconds)
   - Run: `start_with_api_key.ps1`
   - Show: "Learning system enabled"

2. **Show Homepage** (30 seconds)
   - Open: http://localhost:5000
   - Scan: http://www.google.com
   - Result: Safe prediction

3. **Show Learning in Action** (2 minutes)
   - Login/Register
   - Scan: http://testsafebrowsing.appspot.com/s/malware.html
   - Show: TrustLink prediction
   - Show: External validation (3 sources)
   - Point out: "System learning from verified data"

4. **Show Dashboard** (1 minute)
   - Navigate to dashboard
   - Show: Total scans, statistics
   - Show: Recent scan history

5. **Show Training Data** (1 minute)
   - Open: Postman or PowerShell
   - Call: GET /api/v1/training-stats
   - Show: Data accumulated
   - Explain: "This data will improve the model"

6. **Trigger Retraining** (30 seconds)
   - Call: POST /api/v1/retrain
   - Show: Success response with metrics
   - Explain: "Model just learned from verified threats"

---

## Automated Test Suite

### Create: `run_all_tests.py`

```python
import requests
import json

BASE_URL = "http://localhost:5000"
passed = 0
failed = 0

def test(name, condition, expected=True):
    global passed, failed
    result = condition == expected
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status}: {name}")
    if result:
        passed += 1
    else:
        failed += 1
    return result

print("=" * 70)
print("🧪 TrustLink Automated Test Suite")
print("=" * 70)

# Test 1: Health Check
print("\n1️⃣  Testing Health Endpoint...")
try:
    response = requests.get(f"{BASE_URL}/health")
    data = response.json()
    test("Health endpoint returns 200", response.status_code == 200)
    test("Model loaded", data.get('model_loaded'))
    test("Learning system enabled", data.get('learning_system'))
except Exception as e:
    test("Health endpoint accessible", False)
    print(f"   Error: {e}")

# Test 2: Homepage
print("\n2️⃣  Testing Homepage...")
try:
    response = requests.get(f"{BASE_URL}/")
    test("Homepage loads", response.status_code == 200)
    test("Homepage contains form", "url" in response.text.lower())
except Exception as e:
    test("Homepage accessible", False)

# Test 3: Prediction
print("\n3️⃣  Testing URL Prediction...")
try:
    response = requests.post(
        f"{BASE_URL}/predict",
        json={"url": "http://google.com"}
    )
    test("Prediction returns 200", response.status_code == 200)
    data = response.json()
    test("Prediction has result", 'prediction' in data)
    test("Prediction has confidence", 'confidence' in data)
except Exception as e:
    test("Prediction works", False)
    print(f"   Error: {e}")

# Test 4: Registration
print("\n4️⃣  Testing User Registration...")
try:
    import random
    username = f"test{random.randint(1000,9999)}"
    response = requests.post(
        f"{BASE_URL}/register",
        data={
            "username": username,
            "email": f"{username}@test.com",
            "password": "test123",
            "confirm_password": "test123"
        },
        allow_redirects=False
    )
    test("Registration works", response.status_code in [200, 302])
except Exception as e:
    test("Registration works", False)

# Summary
print("\n" + "=" * 70)
print(f"📊 Test Results: {passed} passed, {failed} failed")
print("=" * 70)

if failed == 0:
    print("✅ All tests passed! System is ready for deployment.")
else:
    print(f"⚠️  {failed} test(s) failed. Check the errors above.")
```

**Run it:**
```bash
python run_all_tests.py
```

---

## Test Data

### Safe URLs for Testing:
```
http://www.google.com
http://www.github.com
http://www.microsoft.com
http://www.amazon.com
http://www.wikipedia.org
```

### Google Test URLs (Safe to Test):
```
http://testsafebrowsing.appspot.com/s/malware.html (Malware test)
http://testsafebrowsing.appspot.com/s/phishing.html (Phishing test)
http://testsafebrowsing.appspot.com/s/unwanted.html (Unwanted software)
```

### Suspicious Patterns (ML Should Flag):
```
http://paypal-verify.tk/login
http://amazon-security.ml/account
http://192.168.1.1/admin
http://bit.ly/abc123 (URL shortener)
```

---

## Troubleshooting Tests

### If Tests Fail:

**Health check fails:**
- Check if app is running: http://localhost:5000
- Restart: `.\start_with_api_key.ps1`

**Learning system shows false:**
- Check API keys are set in script
- Verify keys are valid in provider dashboards

**External validation fails:**
- Check internet connection
- Verify API keys are active
- Check API rate limits not exceeded

**Predictions too slow:**
- Check if model files exist in `models/` folder
- Restart application
- Check system resources

---

## Final Pre-Deployment Test

### Checklist Before Demo/Deployment:

- [ ] Run `python run_all_tests.py` - all pass
- [ ] Test with 10 different URLs - all work
- [ ] Check dashboard statistics display correctly
- [ ] Verify external validation works (test with Google test URL)
- [ ] Confirm training data accumulating
- [ ] Test retraining endpoint works
- [ ] Check all API endpoints respond
- [ ] Verify error handling (invalid URL, etc.)
- [ ] Test on fresh browser (clear cache)
- [ ] Restart app and retest

---

## Performance Benchmarks

**Expected Performance:**

| Metric | Target | Acceptable |
|--------|--------|------------|
| Prediction time | < 1 second | < 2 seconds |
| Homepage load | < 0.5 seconds | < 1 second |
| External validation (first) | < 30 seconds | < 60 seconds |
| External validation (cached) | < 1 second | < 2 seconds |
| Dashboard load | < 1 second | < 2 seconds |
| Retraining (100 samples) | < 30 seconds | < 60 seconds |

---

## Testing Tips for Capstone Demo

1. **Test everything the night before**
2. **Have backup test URLs ready**
3. **Clear browser cache before demo**
4. **Have Postman collection ready for API demo**
5. **Screenshot good results as backup**
6. **Test on the presentation computer**
7. **Have offline slides explaining what should happen**

---

## Success Criteria

Your system passes if:
✅ All pages load without errors
✅ URL scanning works
✅ External validation returns results from 2+ sources
✅ Training data accumulates
✅ Model retraining completes successfully
✅ Dashboard shows accurate statistics
✅ API endpoints all respond correctly

---

**Ready to test? Start with the Quick Start section above!** 🧪
