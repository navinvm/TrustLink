# 🔌 TrustLink API Guide

Complete guide for integrating TrustLink API into your applications.

---

## 🔐 Authentication

All API requests require an API key passed in the `X-API-Key` header.

### Getting an API Key:
1. Register at http://localhost:5000/register
2. Login to your account
3. Navigate to http://localhost:5000/api-keys
4. Click "Generate API Key"
5. Copy your key (shown only once!)

---

## 📡 Endpoints

### Base URL
```
http://localhost:5000
```

---

### 1. Single URL Scan

**Endpoint:** `POST /api/v1/scan`

**Headers:**
```
Content-Type: application/json
X-API-Key: YOUR_API_KEY
```

**Request Body:**
```json
{
  "url": "http://example.com"
}
```

**Response:**
```json
{
  "status": "success",
  "url": "http://example.com",
  "prediction": "Safe",
  "confidence": 92.45,
  "risk_level": "low",
  "details": {
    "domain": "example.com",
    "path_length": 0,
    "has_ip_address": false,
    "suspicious_tld": false,
    "login_keywords_detected": false,
    "url_length": 19,
    "is_https": false,
    "num_subdomains": 0,
    "domain_age_days": 9125,
    "has_valid_ssl": false
  }
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/api/v1/scan \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"url": "http://example.com"}'
```

**Python Example:**
```python
import requests

API_KEY = "your_api_key_here"
url = "http://localhost:5000/api/v1/scan"

response = requests.post(
    url,
    headers={
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    },
    json={"url": "http://example.com"}
)

result = response.json()
print(f"Prediction: {result['prediction']}")
print(f"Confidence: {result['confidence']}%")
```

**JavaScript Example:**
```javascript
const API_KEY = 'your_api_key_here';

fetch('http://localhost:5000/api/v1/scan', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': API_KEY
  },
  body: JSON.stringify({
    url: 'http://example.com'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Prediction:', data.prediction);
  console.log('Confidence:', data.confidence);
});
```

---

### 2. Batch URL Scan

**Endpoint:** `POST /api/v1/batch-scan`

**Headers:**
```
Content-Type: application/json
X-API-Key: YOUR_API_KEY
```

**Request Body:**
```json
{
  "urls": [
    "http://example.com",
    "http://suspicious-site.tk",
    "http://192.168.1.1/admin"
  ]
}
```

**Limits:**
- Maximum 100 URLs per request
- Each URL processed independently
- Failed URLs return error in results array

**Response:**
```json
{
  "status": "success",
  "total": 3,
  "results": [
    {
      "url": "http://example.com",
      "prediction": "Safe",
      "confidence": 92.45,
      "risk_level": "low",
      "status": "success"
    },
    {
      "url": "http://suspicious-site.tk",
      "prediction": "Phishing",
      "confidence": 87.21,
      "risk_level": "high",
      "status": "success"
    },
    {
      "url": "http://192.168.1.1/admin",
      "prediction": "Phishing",
      "confidence": 78.33,
      "risk_level": "medium",
      "status": "success"
    }
  ]
}
```

**Python Example:**
```python
import requests

API_KEY = "your_api_key_here"
url = "http://localhost:5000/api/v1/batch-scan"

urls_to_scan = [
    "http://google.com",
    "http://phishing-site.tk",
    "http://bank-verify.xyz"
]

response = requests.post(
    url,
    headers={
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    },
    json={"urls": urls_to_scan}
)

result = response.json()
for item in result['results']:
    print(f"{item['url']}: {item['prediction']} ({item['confidence']}%)")
```

---

### 3. Get User Statistics

**Endpoint:** `GET /api/v1/stats`

**Headers:**
```
X-API-Key: YOUR_API_KEY
```

**Response:**
```json
{
  "status": "success",
  "statistics": {
    "total_scans": 42,
    "safe_count": 28,
    "phishing_count": 14,
    "avg_confidence": 85.7
  },
  "recent_scans": [
    {
      "id": 42,
      "url": "http://example.com",
      "prediction": "Safe",
      "confidence": 92.45,
      "risk_level": "low",
      "scanned_at": "2026-02-05 15:30:22",
      "ip_address": "127.0.0.1"
    }
    // ... up to 10 most recent scans
  ]
}
```

**cURL Example:**
```bash
curl http://localhost:5000/api/v1/stats \
  -H "X-API-Key: YOUR_API_KEY"
```

---

### 4. Health Check

**Endpoint:** `GET /health`

**No authentication required**

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "vectorizer_loaded": true,
  "advanced_features": true,
  "version": "2.0"
}
```

---

## 📊 Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (invalid URL, missing parameters) |
| 401 | Unauthorized (invalid or missing API key) |
| 500 | Server Error (prediction failed) |

---

## 🎯 Risk Levels

| Level | Confidence Range | Meaning |
|-------|-----------------|---------|
| **low** | 0-50% | Low confidence in prediction |
| **medium** | 51-80% | Moderate confidence |
| **high** | 81-100% | High confidence in prediction |

---

## 📈 Rate Limits

Currently, TrustLink v2.0 does not enforce rate limits, but best practices:

- **Single scan:** Unlimited
- **Batch scan:** Max 100 URLs per request
- **Recommended:** Don't exceed 1000 requests/minute

---

## 🔒 Security Best Practices

### API Key Management:
1. ✅ Store keys in environment variables
2. ✅ Never commit keys to version control
3. ✅ Generate separate keys for each application
4. ✅ Revoke unused keys immediately
5. ✅ Rotate keys periodically

### Example (Python with environment variables):
```python
import os
import requests

API_KEY = os.environ.get('TRUSTLINK_API_KEY')

if not API_KEY:
    raise ValueError("API key not found in environment")

response = requests.post(
    "http://localhost:5000/api/v1/scan",
    headers={"X-API-Key": API_KEY},
    json={"url": "http://example.com"}
)
```

---

## 🐍 Python SDK Example

```python
class TrustLinkClient:
    """Simple SDK for TrustLink API"""
    
    def __init__(self, api_key, base_url="http://localhost:5000"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }
    
    def scan_url(self, url):
        """Scan a single URL"""
        response = requests.post(
            f"{self.base_url}/api/v1/scan",
            headers=self.headers,
            json={"url": url}
        )
        return response.json()
    
    def batch_scan(self, urls):
        """Scan multiple URLs"""
        response = requests.post(
            f"{self.base_url}/api/v1/batch-scan",
            headers=self.headers,
            json={"urls": urls}
        )
        return response.json()
    
    def get_stats(self):
        """Get user statistics"""
        response = requests.get(
            f"{self.base_url}/api/v1/stats",
            headers={"X-API-Key": self.api_key}
        )
        return response.json()

# Usage
client = TrustLinkClient(api_key="your_key_here")
result = client.scan_url("http://example.com")
print(result)
```

---

## 🌐 Integration Examples

### Email Security Filter
```python
def check_email_links(email_content):
    """Extract and check all URLs in email"""
    import re
    
    client = TrustLinkClient(os.environ['TRUSTLINK_API_KEY'])
    
    # Extract URLs
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', email_content)
    
    # Batch scan
    if urls:
        results = client.batch_scan(urls)
        
        # Check for phishing
        phishing_found = any(
            r['prediction'] == 'Phishing' 
            for r in results['results'] 
            if r['status'] == 'success'
        )
        
        return {
            'safe': not phishing_found,
            'scanned_urls': len(urls),
            'results': results
        }
    
    return {'safe': True, 'scanned_urls': 0}
```

### Browser Extension Backend
```python
from flask import Flask, request, jsonify

app = Flask(__name__)
trustlink = TrustLinkClient(os.environ['TRUSTLINK_API_KEY'])

@app.route('/check-url', methods=['POST'])
def check_url():
    """Endpoint for browser extension"""
    url = request.json.get('url')
    result = trustlink.scan_url(url)
    
    return jsonify({
        'is_safe': result['prediction'] == 'Safe',
        'confidence': result['confidence'],
        'should_warn': result['risk_level'] == 'high'
    })
```

### Automated Security Scanner
```python
import csv
from datetime import datetime

def scan_website_links(urls_file, output_file):
    """Scan URLs from CSV and save results"""
    client = TrustLinkClient(os.environ['TRUSTLINK_API_KEY'])
    
    # Read URLs
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f.readlines()]
    
    # Batch scan (100 at a time)
    all_results = []
    for i in range(0, len(urls), 100):
        batch = urls[i:i+100]
        results = client.batch_scan(batch)
        all_results.extend(results['results'])
    
    # Save results
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['url', 'prediction', 'confidence', 'risk_level'])
        writer.writeheader()
        writer.writerows(all_results)
    
    print(f"Scanned {len(all_results)} URLs")
    print(f"Results saved to {output_file}")
```

---

## 🔧 Troubleshooting

### Error: "API key required"
- Ensure `X-API-Key` header is set
- Check key is not expired or revoked

### Error: "Invalid API key"
- Verify key is correct (copy-paste carefully)
- Check key belongs to active account

### Error: "Maximum 100 URLs per batch"
- Split large batches into chunks of 100
- Process sequentially

### Connection refused
- Ensure TrustLink server is running
- Check correct host/port

---

## 📞 Support

For API issues:
1. Check this documentation
2. Verify API key is active at /api-keys
3. Test with health endpoint
4. Review FEATURES_v2.md for details

---

**Happy Building! 🚀**
