# TrustLink API Security Configuration Guide

## Overview
This guide explains how to securely configure TrustLink's API endpoints for production use.

## ⚠️ Security Best Practices

### 1. Never Expose Localhost URLs
- **DON'T** use `http://localhost:5000` or `http://127.0.0.1:5000` in production
- **DO** use your actual domain with HTTPS (e.g., `https://trustlink.yourdomain.com`)

### 2. Always Use HTTPS
- Ensure your production server uses SSL/TLS certificates
- Use Let's Encrypt for free SSL certificates
- Never transmit API keys over HTTP

### 3. Environment Variables
Set these environment variables for security:

```bash
# Linux/Mac
export TRUSTLINK_API_URL="https://trustlink.yourdomain.com"
export TRUSTLINK_DOMAIN="trustlink.yourdomain.com"

# Windows PowerShell
$env:TRUSTLINK_API_URL="https://trustlink.yourdomain.com"
$env:TRUSTLINK_DOMAIN="trustlink.yourdomain.com"
```

## Configuration Steps

### Web Application (Flask)

The API documentation will automatically use placeholders. Configure your actual domain:

1. **Update `app.py`** (if needed):
```python
import os

# Get domain from environment variable
DOMAIN = os.getenv('TRUSTLINK_DOMAIN', 'localhost:5000')
PROTOCOL = 'https' if DOMAIN != 'localhost:5000' else 'http'
```

2. **Email Templates**: 
The dashboard URL in email notifications now uses a template variable `{{ dashboard_url }}`. Configure this in your email sending function:

```python
dashboard_url = f"https://{os.getenv('TRUSTLINK_DOMAIN', 'localhost:5000')}/dashboard"
```

### Browser Extension

1. **User Configuration Required**:
   - Users must set their TrustLink server URL in extension settings
   - No default URL is provided for security
   - Go to: Extension Options → API Configuration

2. **Extension Setup**:
   ```
   1. Click the TrustLink extension icon
   2. Click "Settings" ⚙️
   3. Enter your TrustLink server URL (e.g., https://trustlink.yourdomain.com)
   4. Enter your API key (generated from the web app)
   5. Save settings
   ```

### Testing Locally

For local development only:

```bash
# Set environment variable for testing
export TRUSTLINK_API_URL="http://127.0.0.1:5000"

# Run tests
python test_features.py
```

## API Key Management

### Creating API Keys
1. Log into TrustLink web application
2. Navigate to Dashboard → API Keys
3. Click "Generate API Key"
4. **Copy the key immediately** - it won't be shown again
5. Store securely (use a password manager or secrets vault)

### Using API Keys

**Correct Usage:**
```bash
curl -X POST https://trustlink.yourdomain.com/api/v1/scan \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_ACTUAL_API_KEY" \
  -d '{"url": "http://example.com"}'
```

**Never Do This:**
- ❌ Commit API keys to version control (Git)
- ❌ Share API keys in public forums or documentation
- ❌ Use the same API key across multiple applications
- ❌ Store API keys in client-side JavaScript

### Revoking API Keys
If an API key is compromised:
1. Go to Dashboard → API Keys
2. Find the compromised key
3. Click "Revoke"
4. Generate a new key
5. Update all applications using the old key

## Production Deployment Checklist

- [ ] SSL/TLS certificate installed and configured
- [ ] Domain configured with proper DNS records
- [ ] Environment variables set for production domain
- [ ] All API keys generated and stored securely
- [ ] Test API endpoints using HTTPS
- [ ] Browser extension configured with production URL
- [ ] Email notifications configured with production dashboard URL
- [ ] Rate limiting enabled (if applicable)
- [ ] API access logs enabled for monitoring
- [ ] Backup and disaster recovery plan in place

## Firewall and Network Security

### Recommended Firewall Rules
```bash
# Allow HTTPS traffic
sudo ufw allow 443/tcp

# Allow HTTP (redirect to HTTPS)
sudo ufw allow 80/tcp

# Block direct Flask development server port
sudo ufw deny 5000/tcp
```

### Reverse Proxy Configuration (Nginx Example)
```nginx
server {
    listen 443 ssl http2;
    server_name trustlink.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/trustlink.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/trustlink.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name trustlink.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## Monitoring and Logging

### Monitor for Security Issues
- Review API key usage logs regularly
- Set up alerts for unusual activity
- Monitor failed authentication attempts
- Track API rate limit violations

### Recommended Logging
```python
import logging

logging.basicConfig(
    filename='trustlink_api.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Log API requests
@app.before_request
def log_request():
    if request.path.startswith('/api/'):
        logging.info(f"API Request: {request.method} {request.path} from {request.remote_addr}")
```

## Support

For security concerns or questions:
- Review the main README.md
- Check DEPLOYMENT.md for production setup
- Consult API_GUIDE.md for API documentation

---

**Remember:** Security is an ongoing process. Regularly review and update your security practices.
