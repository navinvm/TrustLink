# 🚀 TrustLink v2.0 - New Features Documentation

## Overview

TrustLink v2.0 introduces powerful new features including user authentication, API key management, scan history tracking, and advanced ML feature extraction.

---

## 🆕 What's New in v2.0

### 1. **User Authentication System**

#### Features:
- ✅ User registration and login
- ✅ Secure password hashing (SHA-256)
- ✅ Session management with 7-day persistence
- ✅ Protected routes requiring authentication

#### How to Use:
```
1. Visit http://localhost:5000/register
2. Create an account with username, email, and password
3. Login at http://localhost:5000/login
4. Access your personal dashboard
```

#### API Endpoints:
- `GET /register` - Registration page
- `POST /register` - Create new account
- `GET /login` - Login page
- `POST /login` - Authenticate user
- `GET /logout` - End session

---

### 2. **User Dashboard**

#### Features:
- 📊 Personal statistics (total scans, safe/phishing counts, avg confidence)
- 📜 Recent scan history (last 10 scans)
- 🔑 API key management overview
- 🎯 Quick action buttons

#### Access:
```
http://localhost:5000/dashboard
```

#### Statistics Displayed:
- **Total Scans**: Cumulative number of URLs analyzed
- **Safe URLs**: Count of legitimate URLs detected
- **Threats Detected**: Number of phishing URLs found
- **Avg Confidence**: Average confidence score across all scans

---

### 3. **Scan History Tracking**

#### Features:
- 💾 Automatic saving of all URL scans for authenticated users
- 📅 Timestamp tracking
- 🌐 IP address logging
- 📄 Pagination support (50 records per page)

#### Access:
```
http://localhost:5000/history
```

#### Data Stored:
- URL scanned
- Prediction (Safe/Phishing)
- Confidence score
- Risk level (Low/Medium/High)
- Scan timestamp
- IP address

---

### 4. **API Key Management**

#### Features:
- 🔐 Generate unlimited API keys
- 📝 Custom naming for each key
- 📊 Usage tracking (call count, last used)
- ❌ Key revocation capability
- 📖 Built-in API documentation

#### How to Create API Key:
```
1. Login to your account
2. Navigate to http://localhost:5000/api-keys
3. Enter a name for your key (e.g., "Production Server")
4. Click "Generate API Key"
5. Copy the key immediately (shown only once!)
```

#### Using API Keys:

**Single URL Scan:**
```bash
curl -X POST http://localhost:5000/api/v1/scan \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{"url": "http://suspicious-site.com"}'
```

**Batch Scan (up to 100 URLs):**
```bash
curl -X POST http://localhost:5000/api/v1/batch-scan \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY_HERE" \
  -d '{
    "urls": [
      "http://site1.com",
      "http://site2.com",
      "http://site3.com"
    ]
  }'
```

**Get Statistics:**
```bash
curl http://localhost:5000/api/v1/stats \
  -H "X-API-Key: YOUR_API_KEY_HERE"
```

**Python Example:**
```python
import requests

API_KEY = "your_api_key_here"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# Single scan
response = requests.post(
    "http://localhost:5000/api/v1/scan",
    headers=headers,
    json={"url": "http://example.com"}
)
print(response.json())

# Batch scan
response = requests.post(
    "http://localhost:5000/api/v1/batch-scan",
    headers=headers,
    json={
        "urls": [
            "http://site1.com",
            "http://site2.com"
        ]
    }
)
print(response.json())
```

---

### 5. **Advanced ML Feature Extraction**

#### New Features Extracted:
- ✅ **URL Entropy** - Measures randomness/obfuscation
- ✅ **Domain Age** - WHOIS lookup for domain registration date
- ✅ **SSL Certificate Validation** - Checks HTTPS certificate validity
- ✅ **DNS MX Records** - Verifies mail server existence
- ✅ **Subdomain Analysis** - Counts subdomains (suspicious if many)
- ✅ **Character Analysis** - Special character ratios, digit counts
- ✅ **Hex Encoding Detection** - Identifies URL encoding obfuscation
- ✅ **Punycode Detection** - Finds internationalized domain names

#### Installation (Optional):
```bash
pip install dnspython python-whois
```

If these libraries are not installed, TrustLink falls back to basic feature extraction automatically.

#### Features List:
| Feature | Type | Description |
|---------|------|-------------|
| url_length | Numeric | Total URL length |
| domain_length | Numeric | Domain name length |
| path_length | Numeric | Path component length |
| num_dots | Numeric | Count of dots in URL |
| num_subdomains | Numeric | Number of subdomains |
| url_entropy | Numeric | Shannon entropy (randomness) |
| is_https | Boolean | Uses HTTPS protocol |
| has_ip_address | Boolean | IP address in domain |
| has_suspicious_tld | Boolean | Uses risky TLD (.tk, .ml, etc.) |
| domain_age_days | Numeric | Days since domain registration |
| is_new_domain | Boolean | Domain less than 1 year old |
| has_valid_ssl | Boolean | Valid SSL certificate |
| ssl_days_until_expiry | Numeric | Days until SSL expiration |
| has_mx_record | Boolean | Has mail exchange records |
| num_phishing_keywords | Numeric | Count of suspicious keywords |

---

### 6. **System Analytics**

#### Features:
- 📈 30-day trend analysis
- 📊 Daily breakdown of scans
- 📉 Threat rate calculation
- 📉 Interactive charts (Chart.js)

#### Access:
```
http://localhost:5000/analytics
```

#### Metrics Displayed:
- Total scans over time
- Safe vs. Phishing URL trends
- Daily threat rate percentages
- Visual bar charts and line graphs

---

### 7. **Enhanced Prediction Endpoint**

#### Dual Authentication Support:
The `/predict` endpoint now supports both:
1. **Session-based** (for web UI users)
2. **API key-based** (for developers)

#### Automatic History Saving:
- Authenticated requests automatically save to history
- Anonymous requests (web UI without login) still work but don't save history

#### Response Format:
```json
{
  "status": "success",
  "url": "http://example.com",
  "prediction": "Safe",
  "confidence": 87.32,
  "risk_level": "low",
  "details": {
    "domain": "example.com",
    "path_length": 5,
    "has_ip_address": false,
    "suspicious_tld": false,
    "login_keywords_detected": false,
    "url_length": 23,
    "is_https": false,
    "num_subdomains": 0,
    "domain_age_days": 9125,
    "has_valid_ssl": false
  }
}
```

---

## 🗄️ Database Schema

### Tables:
1. **users** - User accounts
2. **api_keys** - API key management
3. **scan_history** - URL scan records
4. **analytics** - Daily aggregated statistics

### Database File:
- Location: `trustlink.db` (SQLite)
- Created automatically on first run
- Portable and zero-configuration

---

## 🔒 Security Features

### Password Security:
- SHA-256 hashing
- No plaintext storage

### API Key Security:
- 32-byte URL-safe tokens
- Hashed storage (SHA-256)
- Revocation support

### Session Security:
- 7-day expiration
- Secure session management
- CSRF protection ready

---

## 📊 API Limits

| Feature | Limit |
|---------|-------|
| Batch Scan | 100 URLs per request |
| API Keys per User | Unlimited |
| Scan History | Unlimited |
| Session Duration | 7 days |

---

## 🚦 Migration from v1.0

### Backward Compatibility:
✅ All v1.0 features still work  
✅ Anonymous scanning still available  
✅ `/predict` endpoint unchanged for basic use  

### New Optional Features:
- User accounts (optional, not required)
- API keys (optional, for programmatic access)
- History tracking (only for authenticated users)

---

## 🐛 Troubleshooting

### Issue: Advanced features not working
**Solution:** Install optional dependencies:
```bash
pip install dnspython python-whois
```

### Issue: Database errors
**Solution:** Delete `trustlink.db` and restart (creates fresh database)

### Issue: Can't login
**Solution:** Ensure session secret key is set in `app.py` (line 15)

### Issue: API key not working
**Solution:** 
- Check header: `X-API-Key: your_key_here`
- Verify key is active (not revoked)
- Ensure key belongs to your user account

---

## 📝 Best Practices

### For Web Users:
1. Create an account to track scan history
2. Use strong passwords
3. Logout when done on shared computers

### For API Users:
1. Generate separate keys for each application
2. Name keys descriptively
3. Revoke unused keys
4. Never commit API keys to version control
5. Use environment variables for keys

### For Developers:
1. Change session secret key in production
2. Use HTTPS in production
3. Implement rate limiting for APIs
4. Backup `trustlink.db` regularly
5. Monitor analytics for unusual patterns

---

## 🎯 Use Cases

### Personal Security:
- Check suspicious emails
- Verify shortened URLs
- Validate social media links

### Enterprise Security:
- Integrate with email filters
- Batch scan website submissions
- Monitor employee-reported URLs
- Generate security reports

### Developer Integration:
- Browser extensions
- Mobile applications
- Email security plugins
- Automated security scanners

---

## 🔄 API Versioning

Current version: **v2.0**

API endpoints are versioned:
- `/api/v1/scan` - Current stable API
- `/api/v1/batch-scan` - Batch scanning
- `/api/v1/stats` - User statistics

---

## 📞 Support

For issues or questions:
1. Check this documentation
2. Review `README.md`
3. Check `QUICKSTART.md` for setup help

---

**Congratulations!** You now have access to a professional-grade phishing detection platform with advanced features! 🎉
