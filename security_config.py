"""
TrustLink Security Configuration Module
Centralized security settings, headers, and middleware
"""
import os
import secrets
from functools import wraps
from flask import request, jsonify, session
from datetime import datetime, timedelta
import hashlib
import re


class SecurityConfig:
    """Security configuration and constants"""
    
    # Secret key management
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or secrets.token_hex(32)
    
    # Session configuration
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # Rate limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_STORAGE_URL = 'memory://'
    
    # API rate limits
    API_RATE_LIMITS = {
        'scan': '100 per hour',
        'batch_scan': '10 per hour',
        'feedback': '20 per hour',
        'retrain': '5 per day',
        'default': '200 per hour'
    }
    
    # Password policy
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGIT = True
    PASSWORD_REQUIRE_SPECIAL = False
    
    # Input validation
    MAX_URL_LENGTH = 2048
    MAX_BATCH_SIZE = 100
    ALLOWED_URL_SCHEMES = ['http', 'https', 'ftp']
    
    # CSRF Protection
    CSRF_ENABLED = True
    CSRF_TIME_LIMIT = 3600  # 1 hour
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        ),
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
    }


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = {}
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = datetime.now()
    
    def is_allowed(self, key, limit_per_hour=100):
        """Check if request is within rate limit"""
        now = datetime.now()
        
        # Periodic cleanup
        if (now - self.last_cleanup).total_seconds() > self.cleanup_interval:
            self._cleanup()
        
        # Get or create request log
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests (older than 1 hour)
        cutoff = now - timedelta(hours=1)
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > cutoff]
        
        # Check limit
        if len(self.requests[key]) >= limit_per_hour:
            return False
        
        # Log this request
        self.requests[key].append(now)
        return True
    
    def _cleanup(self):
        """Remove expired entries"""
        cutoff = datetime.now() - timedelta(hours=2)
        for key in list(self.requests.keys()):
            self.requests[key] = [req_time for req_time in self.requests[key] if req_time > cutoff]
            if not self.requests[key]:
                del self.requests[key]
        self.last_cleanup = datetime.now()


class InputValidator:
    """Input validation and sanitization"""
    
    @staticmethod
    def validate_url(url, max_length=2048):
        """Validate URL format and length"""
        if not url or not isinstance(url, str):
            raise ValueError("URL must be a non-empty string")
        
        url = url.strip()
        
        if len(url) > max_length:
            raise ValueError(f"URL exceeds maximum length of {max_length}")
        
        # Basic URL pattern validation
        url_pattern = re.compile(
            r'^(https?|ftp)://'  # protocol
            r'([a-zA-Z0-9.-]+)'  # domain
            r'(:[0-9]+)?'  # optional port
            r'(/.*)?$'  # optional path
        )
        
        if not url.startswith(('http://', 'https://', 'ftp://')):
            url = 'http://' + url
        
        if not url_pattern.match(url):
            raise ValueError("Invalid URL format")
        
        return url
    
    @staticmethod
    def validate_password(password):
        """Validate password against policy"""
        errors = []
        
        if len(password) < SecurityConfig.PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {SecurityConfig.PASSWORD_MIN_LENGTH} characters")
        
        if SecurityConfig.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if SecurityConfig.PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if SecurityConfig.PASSWORD_REQUIRE_DIGIT and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if SecurityConfig.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        if errors:
            raise ValueError("; ".join(errors))
        
        return True
    
    @staticmethod
    def validate_username(username):
        """Validate username format"""
        if not username or not isinstance(username, str):
            raise ValueError("Username must be a non-empty string")
        
        username = username.strip()
        
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        
        if len(username) > 50:
            raise ValueError("Username must be less than 50 characters")
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise ValueError("Username can only contain letters, numbers, hyphens, and underscores")
        
        return username
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email or not isinstance(email, str):
            raise ValueError("Email must be a non-empty string")
        
        email = email.strip().lower()
        
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        if not email_pattern.match(email):
            raise ValueError("Invalid email format")
        
        return email
    
    @staticmethod
    def sanitize_string(text, max_length=1000):
        """Sanitize user input string"""
        if not isinstance(text, str):
            return str(text)
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Limit length
        text = text[:max_length]
        
        # Strip whitespace
        text = text.strip()
        
        return text


def apply_security_headers(response):
    """Apply security headers to response"""
    for header, value in SecurityConfig.SECURITY_HEADERS.items():
        response.headers[header] = value
    return response


def rate_limit_decorator(limit_key='default', per_hour=None):
    """Decorator for rate limiting endpoints"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not SecurityConfig.RATE_LIMIT_ENABLED:
                return f(*args, **kwargs)
            
            # Determine rate limit
            limit = per_hour or int(SecurityConfig.API_RATE_LIMITS.get(limit_key, '100 per hour').split()[0])
            
            # Create unique key for user/IP
            if 'user_id' in session:
                key = f"user:{session['user_id']}:{limit_key}"
            else:
                key = f"ip:{request.remote_addr}:{limit_key}"
            
            # Check rate limit
            if not hasattr(decorated_function, '_rate_limiter'):
                decorated_function._rate_limiter = RateLimiter()
            
            if not decorated_function._rate_limiter.is_allowed(key, limit):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'status': 'error',
                    'retry_after': 3600
                }), 429
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


class CSRFProtection:
    """CSRF token generation and validation"""
    
    @staticmethod
    def generate_token():
        """Generate CSRF token"""
        token = secrets.token_urlsafe(32)
        session['csrf_token'] = token
        session['csrf_token_time'] = datetime.now().isoformat()
        return token
    
    @staticmethod
    def validate_token(token):
        """Validate CSRF token"""
        if not SecurityConfig.CSRF_ENABLED:
            return True
        
        if 'csrf_token' not in session:
            return False
        
        # Check token match
        if not secrets.compare_digest(session['csrf_token'], token):
            return False
        
        # Check token age
        token_time = datetime.fromisoformat(session.get('csrf_token_time', '2000-01-01'))
        age = (datetime.now() - token_time).total_seconds()
        
        if age > SecurityConfig.CSRF_TIME_LIMIT:
            return False
        
        return True


def csrf_protect(f):
    """Decorator for CSRF protection"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # Skip CSRF for API requests with API key
            if request.headers.get('X-API-Key'):
                return f(*args, **kwargs)
            
            token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
            
            if not token or not CSRFProtection.validate_token(token):
                return jsonify({
                    'error': 'CSRF token missing or invalid',
                    'status': 'error'
                }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


class SecurityLogger:
    """Security event logging"""
    
    @staticmethod
    def log_authentication_failure(username, ip_address, reason='invalid_credentials'):
        """Log failed authentication attempt"""
        timestamp = datetime.now().isoformat()
        print(f"[SECURITY] {timestamp} - Authentication failure: {username} from {ip_address} - {reason}")
    
    @staticmethod
    def log_authentication_success(username, ip_address):
        """Log successful authentication"""
        timestamp = datetime.now().isoformat()
        print(f"[SECURITY] {timestamp} - Authentication success: {username} from {ip_address}")
    
    @staticmethod
    def log_api_key_usage(user_id, endpoint, ip_address):
        """Log API key usage"""
        timestamp = datetime.now().isoformat()
        print(f"[API] {timestamp} - API key used by user {user_id} for {endpoint} from {ip_address}")
    
    @staticmethod
    def log_suspicious_activity(description, ip_address, user_id=None):
        """Log suspicious activity"""
        timestamp = datetime.now().isoformat()
        user_info = f"user {user_id}" if user_id else "anonymous"
        print(f"[SECURITY ALERT] {timestamp} - Suspicious activity from {ip_address} ({user_info}): {description}")
    
    @staticmethod
    def log_rate_limit_exceeded(key, endpoint):
        """Log rate limit violations"""
        timestamp = datetime.now().isoformat()
        print(f"[SECURITY] {timestamp} - Rate limit exceeded: {key} on {endpoint}")


def check_password_breach(password_hash):
    """
    Check if password appears in known breaches using k-anonymity
    Uses Have I Been Pwned API
    """
    # SHA-1 hash of password
    sha1_password = hashlib.sha1(password_hash.encode()).hexdigest().upper()
    prefix = sha1_password[:5]
    suffix = sha1_password[5:]
    
    try:
        # Query HIBP API
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        response = requests.get(url, timeout=2)
        
        if response.status_code == 200:
            # Check if hash suffix appears in response
            hashes = response.text.split('\r\n')
            for hash_line in hashes:
                hash_suffix, count = hash_line.split(':')
                if hash_suffix == suffix:
                    return True, int(count)
        
        return False, 0
    except Exception:
        # If API fails, allow password (fail open for availability)
        return False, 0
