# 🚀 TrustLink Deployment Guide

Production deployment guide for TrustLink v2.0

---

## ⚠️ Production Checklist

Before deploying to production, ensure you:

### Security
- [ ] Change `app.secret_key` in `app.py` (line 15)
- [ ] Use strong, random secret key (32+ characters)
- [ ] Enable HTTPS/SSL
- [ ] Set secure cookie flags
- [ ] Implement rate limiting
- [ ] Add CSRF protection
- [ ] Sanitize all user inputs
- [ ] Use environment variables for secrets

### Database
- [ ] Backup `trustlink.db` regularly
- [ ] Consider PostgreSQL/MySQL for production
- [ ] Implement database migrations
- [ ] Set up automated backups

### Performance
- [ ] Use production WSGI server (Gunicorn/uWSGI)
- [ ] Enable caching
- [ ] Set up CDN for static files
- [ ] Optimize database queries
- [ ] Monitor resource usage

### Monitoring
- [ ] Set up logging
- [ ] Configure error tracking (Sentry)
- [ ] Monitor API usage
- [ ] Track performance metrics
- [ ] Set up alerts

---

## 🖥️ Deployment Options

### Option 1: Traditional VPS (DigitalOcean, AWS EC2, etc.)

#### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx -y

# Create application user
sudo useradd -m -s /bin/bash trustlink
sudo su - trustlink
```

#### 2. Application Setup
```bash
# Clone/upload your code
cd /home/trustlink
# Upload your TrustLink files here

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

#### 3. Gunicorn Configuration
Create `/home/trustlink/gunicorn_config.py`:
```python
bind = "127.0.0.1:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
errorlog = "/home/trustlink/logs/gunicorn-error.log"
accesslog = "/home/trustlink/logs/gunicorn-access.log"
loglevel = "info"
```

#### 4. Systemd Service
Create `/etc/systemd/system/trustlink.service`:
```ini
[Unit]
Description=TrustLink Phishing Detection Service
After=network.target

[Service]
Type=notify
User=trustlink
Group=trustlink
WorkingDirectory=/home/trustlink
Environment="PATH=/home/trustlink/venv/bin"
ExecStart=/home/trustlink/venv/bin/gunicorn -c gunicorn_config.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable trustlink
sudo systemctl start trustlink
sudo systemctl status trustlink
```

#### 5. Nginx Configuration
Create `/etc/nginx/sites-available/trustlink`:
```nginx
server {
    listen 80;
    server_name trustlink.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/trustlink/static;
        expires 30d;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/trustlink /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 6. SSL with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d trustlink.yourdomain.com
```

---

### Option 2: Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 trustlink && chown -R trustlink:trustlink /app
USER trustlink

# Expose port
EXPOSE 8000

# Run with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "-w", "4", "app:app"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  trustlink:
    build: .
    ports:
      - "8000:8000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./trustlink.db:/app/trustlink.db
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./static:/usr/share/nginx/html/static
    depends_on:
      - trustlink
    restart: unless-stopped
```

Build and run:
```bash
docker-compose up -d
docker-compose logs -f
```

---

### Option 3: Heroku

#### 1. Create Procfile
```
web: gunicorn app:app
```

#### 2. Create runtime.txt
```
python-3.9.16
```

#### 3. Deploy
```bash
heroku login
heroku create trustlink-app
git push heroku main
heroku open
```

---

### Option 4: AWS Elastic Beanstalk

#### 1. Install EB CLI
```bash
pip install awsebcli
```

#### 2. Initialize
```bash
eb init -p python-3.9 trustlink-app
```

#### 3. Create environment
```bash
eb create trustlink-env
```

#### 4. Deploy
```bash
eb deploy
eb open
```

---

## 🔧 Production Configuration

### app.py Changes

Replace development settings:
```python
# Change this line
app.secret_key = 'trustlink_super_secret_key_change_in_production'

# To this (using environment variable)
app.secret_key = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

# Change debug mode
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)  # Set debug=False
```

### Environment Variables
Create `.env` file (don't commit!):
```bash
SECRET_KEY=your-super-secret-key-here-32-chars-minimum
FLASK_ENV=production
DATABASE_URL=sqlite:///trustlink.db
```

Load in app.py:
```python
from dotenv import load_dotenv
load_dotenv()

app.secret_key = os.environ.get('SECRET_KEY')
```

---

## 📊 Monitoring & Logging

### Setup Logging
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('trustlink.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('TrustLink startup')
```

### Monitor with Sentry
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()]
)
```

---

## 🔒 Security Hardening

### Rate Limiting
```bash
pip install Flask-Limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/predict', methods=['POST'])
@limiter.limit("10 per minute")
def predict():
    # ... existing code
```

### CORS (if needed)
```bash
pip install flask-cors
```

```python
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "https://yourdomain.com"}})
```

---

## 📦 Backup Strategy

### Automated Database Backups
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/trustlink"
DB_PATH="/home/trustlink/trustlink.db"

mkdir -p $BACKUP_DIR
sqlite3 $DB_PATH ".backup '$BACKUP_DIR/trustlink_$DATE.db'"

# Keep only last 30 days
find $BACKUP_DIR -name "trustlink_*.db" -mtime +30 -delete

echo "Backup completed: trustlink_$DATE.db"
```

Add to crontab:
```bash
0 2 * * * /home/trustlink/backup.sh
```

---

## 📈 Performance Optimization

### Database Optimization
```sql
-- Add indexes
CREATE INDEX idx_scan_history_user_id ON scan_history(user_id);
CREATE INDEX idx_scan_history_scanned_at ON scan_history(scanned_at);
CREATE INDEX idx_api_keys_user_id ON api_keys(user_id);
```

### Caching
```bash
pip install Flask-Caching
```

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/analytics')
@cache.cached(timeout=300)  # Cache for 5 minutes
def analytics():
    # ... existing code
```

---

## 🔍 Health Checks

### Kubernetes Probes
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

---

## 📞 Support & Maintenance

### Log Monitoring
```bash
# View logs
journalctl -u trustlink -f

# Check Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Database Maintenance
```bash
# Vacuum database
sqlite3 trustlink.db "VACUUM;"

# Check integrity
sqlite3 trustlink.db "PRAGMA integrity_check;"
```

---

## ✅ Post-Deployment Checklist

- [ ] Application accessible via domain
- [ ] HTTPS working correctly
- [ ] User registration/login functional
- [ ] API endpoints responding
- [ ] Database backups running
- [ ] Logs being written
- [ ] Monitoring alerts configured
- [ ] Performance acceptable
- [ ] Security headers configured
- [ ] Rate limiting active

---

**Your TrustLink deployment is ready! 🎉**
