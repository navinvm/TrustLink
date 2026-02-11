"""
Database models and utilities for TrustLink
Handles user authentication, scan history, and API keys
"""
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from contextlib import contextmanager


class Database:
    """Database manager for TrustLink"""
    
    def __init__(self, db_path='trustlink.db'):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    email_verified BOOLEAN DEFAULT 0,
                    verification_token TEXT,
                    verification_token_expires TIMESTAMP,
                    is_admin BOOLEAN DEFAULT 0
                )
            ''')
            
            # Password reset tokens table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # API keys table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    key_hash TEXT UNIQUE NOT NULL,
                    key_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    usage_count INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Scan history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    url TEXT NOT NULL,
                    prediction TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    total_scans INTEGER DEFAULT 0,
                    safe_urls INTEGER DEFAULT 0,
                    phishing_urls INTEGER DEFAULT 0,
                    unique_users INTEGER DEFAULT 0,
                    UNIQUE(date)
                )
            ''')
            
            # Feedback table for user corrections
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_id INTEGER,
                    user_id INTEGER,
                    url TEXT NOT NULL,
                    original_prediction TEXT NOT NULL,
                    correct_label TEXT NOT NULL,
                    feedback_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_processed BOOLEAN DEFAULT 0,
                    FOREIGN KEY (scan_id) REFERENCES scan_history (id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # External validation results
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS external_validations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    url_hash TEXT UNIQUE NOT NULL,
                    is_threat BOOLEAN,
                    confidence REAL,
                    source TEXT NOT NULL,
                    threat_type TEXT,
                    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            # Training data pool
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS training_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    label INTEGER NOT NULL,
                    confidence REAL,
                    source TEXT NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    used_in_training BOOLEAN DEFAULT 0,
                    verified BOOLEAN DEFAULT 0
                )
            ''')
            
            # Model training history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT NOT NULL,
                    accuracy REAL,
                    precision_score REAL,
                    recall_score REAL,
                    training_samples INTEGER,
                    trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 0,
                    notes TEXT
                )
            ''')
            
            # Custom whitelist table for dynamic domain management
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS whitelist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT UNIQUE NOT NULL,
                    domain_type TEXT NOT NULL,
                    category TEXT,
                    description TEXT,
                    added_by INTEGER,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    is_root_pattern BOOLEAN DEFAULT 0,
                    verified BOOLEAN DEFAULT 0,
                    FOREIGN KEY (added_by) REFERENCES users (id)
                )
            ''')
            
            # Create index for faster whitelist lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_whitelist_domain 
                ON whitelist(domain, is_active)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_whitelist_pattern 
                ON whitelist(is_root_pattern, is_active)
            ''')
            
            # Chat history table for AI chatbot
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tokens_used INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Create additional performance indexes
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_scan_history_user_date 
                ON scan_history(user_id, scanned_at DESC)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_scan_history_prediction 
                ON scan_history(prediction, scanned_at DESC)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_api_keys_hash 
                ON api_keys(key_hash, is_active)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_external_validations_hash 
                ON external_validations(url_hash, validated_at DESC)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_training_data_used 
                ON training_data(used_in_training, confidence DESC)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_feedback_processed 
                ON feedback(is_processed, created_at DESC)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_chat_history_session 
                ON chat_history(session_id, created_at DESC)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_chat_history_user 
                ON chat_history(user_id, created_at DESC)
            ''')
            
            conn.commit()
    
    # ========== User Management ==========
    
    def create_user(self, username, email, password, is_admin=False):
        """Create a new user with email verification"""
        password_hash = self._hash_password(password)
        verification_token = secrets.token_urlsafe(32)
        expires = datetime.now() + timedelta(hours=24)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO users (username, email, password_hash, verification_token, verification_token_expires, is_admin) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (username, email, password_hash, verification_token, expires, is_admin)
            )
            user_id = cursor.lastrowid
            
        return user_id, verification_token
    
    def create_admin_user(self, username, email, password):
        """Create an admin user with email already verified"""
        password_hash = self._hash_password(password)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO users (username, email, password_hash, email_verified, is_admin) 
                   VALUES (?, ?, ?, 1, 1)''',
                (username, email, password_hash)
            )
            user_id = cursor.lastrowid
            
        return user_id
    
    def authenticate_user(self, username, password):
        """Authenticate user and return user data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM users WHERE username = ? AND is_active = 1',
                (username,)
            )
            user = cursor.fetchone()
            
            self._verify_password(password, user['password_hash'])
            # Update last login
            cursor.execute(
                'UPDATE users SET last_login = ? WHERE id = ?',
                (datetime.now(), user['id'])
            )
            return dict(user)
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            return dict(user)
    
    def get_user_by_email(self, email):
        """Get user by email"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            return dict(user)
    
    # ========== Admin Methods ==========
    
    def get_all_users(self, limit=100, offset=0):
        """Get all users (admin only)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT id, username, email, created_at, last_login, is_active, email_verified, is_admin
                   FROM users 
                   ORDER BY created_at DESC 
                   LIMIT ? OFFSET ?''',
                (limit, offset)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_scans(self, limit=100, offset=0):
        """Get all scans from all users (admin only)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT sh.*, u.username, u.email 
                   FROM scan_history sh
                   LEFT JOIN users u ON sh.user_id = u.id
                   ORDER BY sh.scanned_at DESC 
                   LIMIT ? OFFSET ?''',
                (limit, offset)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_system_statistics(self):
        """Get system-wide statistics (admin only)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total users
            cursor.execute('SELECT COUNT(*) as total FROM users')
            total_users = cursor.fetchone()['total']
            
            # Verified users
            cursor.execute('SELECT COUNT(*) as total FROM users WHERE email_verified = 1')
            verified_users = cursor.fetchone()['total']
            
            # Total scans
            cursor.execute('SELECT COUNT(*) as total FROM scan_history')
            total_scans = cursor.fetchone()['total']
            
            # Phishing detected
            cursor.execute('SELECT COUNT(*) as total FROM scan_history WHERE prediction = "Phishing"')
            phishing_scans = cursor.fetchone()['total']
            
            # Safe scans
            cursor.execute('SELECT COUNT(*) as total FROM scan_history WHERE prediction = "Safe"')
            safe_scans = cursor.fetchone()['total']
            
            # Active API keys
            cursor.execute('SELECT COUNT(*) as total FROM api_keys WHERE is_active = 1')
            active_api_keys = cursor.fetchone()['total']
            
            # Scans today
            cursor.execute(
                '''SELECT COUNT(*) as total FROM scan_history 
                   WHERE DATE(scanned_at) = DATE('now')'''
            )
            scans_today = cursor.fetchone()['total']
            
            # New users this week
            cursor.execute(
                '''SELECT COUNT(*) as total FROM users 
                   WHERE created_at >= datetime('now', '-7 days')'''
            )
            new_users_week = cursor.fetchone()['total']
            
            return {
                'total_users': total_users,
                'verified_users': verified_users,
                'unverified_users': total_users - verified_users,
                'total_scans': total_scans,
                'phishing_scans': phishing_scans,
                'safe_scans': safe_scans,
                'active_api_keys': active_api_keys,
                'scans_today': scans_today,
                'new_users_week': new_users_week
            }
    
    def get_user_details_admin(self, user_id):
        """Get detailed user information (admin only)"""
        user = self.get_user_by_id(user_id)
        stats = self.get_user_statistics(user_id)
        recent_scans = self.get_user_scan_history(user_id, limit=20)
        api_keys = self.get_user_api_keys(user_id)
        
        return {
            'user': user,
            'statistics': stats,
            'recent_scans': recent_scans,
            'api_keys': api_keys
        }
    
    def verify_email(self, token):
        """Verify user email with token"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT * FROM users 
                   WHERE verification_token = ? 
                   AND verification_token_expires > ?
                   AND email_verified = 0''',
                (token, datetime.now())
            )
            user = cursor.fetchone()
            
            cursor.execute(
                '''UPDATE users 
                   SET email_verified = 1, verification_token = NULL, verification_token_expires = NULL 
                   WHERE id = ?''',
                (user['id'],)
            )
            return dict(user)
    
    def resend_verification_email(self, user_id):
        """Generate new verification token for user"""
        verification_token = secrets.token_urlsafe(32)
        expires = datetime.now() + timedelta(hours=24)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''UPDATE users 
                   SET verification_token = ?, verification_token_expires = ? 
                   WHERE id = ? AND email_verified = 0''',
                (verification_token, expires, user_id)
            )
            
            return verification_token
    
    def create_password_reset_token(self, email):
        """Create password reset token for user"""
        user = self.get_user_by_email(email)
        token = secrets.token_urlsafe(32)
        expires = datetime.now() + timedelta(hours=1)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO password_reset_tokens (user_id, token, expires_at)
                   VALUES (?, ?, ?)''',
                (user['id'], token, expires)
            )
        
        return token, user
    
    def verify_password_reset_token(self, token):
        """Verify password reset token and return user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT prt.*, u.* FROM password_reset_tokens prt
                   JOIN users u ON prt.user_id = u.id
                   WHERE prt.token = ? AND prt.expires_at > ? AND prt.used = 0''',
                (token, datetime.now())
            )
            result = cursor.fetchone()
            
            return dict(result)
    
    def reset_password(self, token, new_password):
        """Reset user password using token"""
        token_data = self.verify_password_reset_token(token)
        new_password_hash = self._hash_password(new_password)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Update password
            cursor.execute(
                'UPDATE users SET password_hash = ? WHERE id = ?',
                (new_password_hash, token_data['user_id'])
            )
            
            # Mark token as used
            cursor.execute(
                'UPDATE password_reset_tokens SET used = 1 WHERE token = ?',
                (token,)
            )
            
            return True
    
    # ========== API Key Management ==========
    
    def create_api_key(self, user_id, key_name):
        """Generate a new API key for user"""
        api_key = secrets.token_urlsafe(32)
        key_hash = self._hash_api_key(api_key)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO api_keys (user_id, key_hash, key_name) VALUES (?, ?, ?)',
                (user_id, key_hash, key_name)
            )
            
        return api_key  # Return the plain key only once
    
    def validate_api_key(self, api_key):
        """Validate API key and return user_id"""
        key_hash = self._hash_api_key(api_key)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT user_id FROM api_keys WHERE key_hash = ? AND is_active = 1',
                (key_hash,)
            )
            result = cursor.fetchone()
            
            # Update last used and usage count
            cursor.execute(
                'UPDATE api_keys SET last_used = ?, usage_count = usage_count + 1 WHERE key_hash = ?',
                (datetime.now(), key_hash)
            )
            return result['user_id']
    
    def get_user_api_keys(self, user_id):
        """Get all API keys for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, key_name, created_at, last_used, usage_count, is_active FROM api_keys WHERE user_id = ?',
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def revoke_api_key(self, key_id, user_id):
        """Revoke an API key"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE api_keys SET is_active = 0 WHERE id = ? AND user_id = ?',
                (key_id, user_id)
            )
    
    # ========== Scan History ==========
    
    def add_scan_record(self, user_id, url, prediction, confidence, risk_level, ip_address=None):
        """Add a scan record to history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO scan_history 
                   (user_id, url, prediction, confidence, risk_level, ip_address)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (user_id, url, prediction, confidence, risk_level, ip_address)
            )
            return cursor.lastrowid
    
    def get_user_scan_history(self, user_id, limit=50, offset=0):
        """Get scan history for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT * FROM scan_history 
                   WHERE user_id = ? 
                   ORDER BY scanned_at DESC 
                   LIMIT ? OFFSET ?''',
                (user_id, limit, offset)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_user_statistics(self, user_id):
        """Get statistics for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT 
                    COUNT(*) as total_scans,
                    SUM(CASE WHEN prediction = 'Safe' THEN 1 ELSE 0 END) as safe_count,
                    SUM(CASE WHEN prediction = 'Phishing' THEN 1 ELSE 0 END) as phishing_count,
                    AVG(confidence) as avg_confidence
                   FROM scan_history 
                   WHERE user_id = ?''',
                (user_id,)
            )
            return dict(cursor.fetchone())
    
    def delete_scan_record(self, scan_id, user_id):
        """Delete a single scan record (user must own the scan)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM scan_history WHERE id = ? AND user_id = ?',
                (scan_id, user_id)
            )
            return cursor.rowcount > 0
    
    def delete_all_user_scans(self, user_id):
        """Delete all scan records for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM scan_history WHERE user_id = ?',
                (user_id,)
            )
            return cursor.rowcount
    
    def delete_user_account(self, user_id):
        """Permanently delete a user account and all associated data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Delete all user's scan history first
            cursor.execute('DELETE FROM scan_history WHERE user_id = ?', (user_id,))
            # Delete all user's whitelisted domains
            cursor.execute('DELETE FROM whitelist WHERE user_id = ?', (user_id,))
            # Delete all user's API keys
            cursor.execute('DELETE FROM api_keys WHERE user_id = ?', (user_id,))
            # Finally delete the user account
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            return cursor.rowcount > 0
    
    # ========== Analytics ==========
    
    def update_daily_analytics(self, date, scans_delta=1, safe_delta=0, phishing_delta=0):
        """Update daily analytics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO analytics (date, total_scans, safe_urls, phishing_urls)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(date) DO UPDATE SET
                   total_scans = total_scans + ?,
                   safe_urls = safe_urls + ?,
                   phishing_urls = phishing_urls + ?''',
                (date, scans_delta, safe_delta, phishing_delta,
                 scans_delta, safe_delta, phishing_delta)
            )
    
    def get_analytics(self, days=30):
        """Get analytics for the last N days"""
        start_date = (datetime.now() - timedelta(days=days)).date()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT * FROM analytics 
                   WHERE date >= ? 
                   ORDER BY date DESC''',
                (start_date,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # ========== Helper Methods ==========
    
    def _hash_password(self, password):
        """Hash password using bcrypt-style secure hashing with salt"""
        # Use PBKDF2 for better security than simple SHA-256
        import hashlib
        salt = hashlib.sha256(password.encode()).hexdigest()[:16]
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    
    def _verify_password(self, password, password_hash):
        """Verify password against hash"""
        return self._hash_password(password) == password_hash
    
    def _hash_api_key(self, api_key):
        """Hash API key"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    # ========== Learning System Methods ==========
    
    def add_feedback(self, scan_id, user_id, url, original_prediction, correct_label, feedback_type):
        """Add user feedback for incorrect predictions"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO feedback 
                   (scan_id, user_id, url, original_prediction, correct_label, feedback_type)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (scan_id, user_id, url, original_prediction, correct_label, feedback_type)
            )
            return cursor.lastrowid
    
    def add_external_validation(self, url, is_threat, confidence, source, threat_type=None, metadata=None):
        """Store external validation results"""
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT OR REPLACE INTO external_validations 
                   (url, url_hash, is_threat, confidence, source, threat_type, metadata)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (url, url_hash, is_threat, confidence, source, threat_type, str(metadata))
            )
            return cursor.lastrowid
    
    def get_external_validation(self, url):
        """Get cached external validation result for URL"""
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT * FROM external_validations 
                   WHERE url_hash = ? 
                   ORDER BY validated_at DESC 
                   LIMIT 1''',
                (url_hash,)
            )
            result = cursor.fetchone()
            return dict(result)
    
    def add_training_data(self, url, label, confidence, source, verified=False):
        """Add data to training pool"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO training_data 
                   (url, label, confidence, source, verified)
                   VALUES (?, ?, ?, ?, ?)''',
                (url, label, confidence, source, verified)
            )
            return cursor.lastrowid
    
    # ========== Whitelist Management ==========
    
    def add_whitelist_domain(self, domain, domain_type, category=None, description=None, 
                            added_by=None, is_root_pattern=False, verified=False):
        """Add a domain to the custom whitelist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO whitelist 
                (domain, domain_type, category, description, added_by, is_root_pattern, verified)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (domain, domain_type, category, description, added_by, is_root_pattern, verified)
            )
            return cursor.lastrowid
    
    def get_whitelist_domains(self, active_only=True, include_root_patterns=True):
        """Get all whitelisted domains"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM whitelist WHERE 1=1'
            params = []
            
            if active_only:
                query += ' AND is_active = 1'
            
            if not include_root_patterns:
                query += ' AND is_root_pattern = 0'
            
            query += ' ORDER BY domain'
            
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_whitelist_domain_by_id(self, whitelist_id):
        """Get a specific whitelist entry by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM whitelist WHERE id = ?', (whitelist_id,))
            row = cursor.fetchone()
            return dict(row)
    
    def update_whitelist_domain(self, whitelist_id, **kwargs):
        """Update a whitelist entry"""
        allowed_fields = ['domain', 'domain_type', 'category', 'description', 
                         'is_active', 'is_root_pattern', 'verified']
        
        updates = []
        values = []
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                values.append(value)
        
        values.append(whitelist_id)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = f"UPDATE whitelist SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            return cursor.rowcount > 0
    
    def delete_whitelist_domain(self, whitelist_id):
        """Delete a whitelist entry"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM whitelist WHERE id = ?', (whitelist_id,))
            return cursor.rowcount > 0
    
    def deactivate_whitelist_domain(self, whitelist_id):
        """Soft delete - deactivate a whitelist entry"""
        return self.update_whitelist_domain(whitelist_id, is_active=False)
    
    def search_whitelist(self, search_term):
        """Search whitelist by domain or description"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM whitelist 
                WHERE (domain LIKE ? OR description LIKE ?) AND is_active = 1
                ORDER BY domain
            ''', (f'%{search_term}%', f'%{search_term}%'))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_whitelist_stats(self):
        """Get statistics about the whitelist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total counts
            cursor.execute('SELECT COUNT(*) as total FROM whitelist WHERE is_active = 1')
            total = cursor.fetchone()['total']
            
            # By category
            cursor.execute('''
                SELECT category, COUNT(*) as count 
                FROM whitelist 
                WHERE is_active = 1 
                GROUP BY category 
                ORDER BY count DESC
            ''')
            by_category = [dict(row) for row in cursor.fetchall()]
            
            # Root patterns vs exact domains
            cursor.execute('''
                SELECT 
                    SUM(CASE WHEN is_root_pattern = 1 THEN 1 ELSE 0 END) as root_patterns,
                    SUM(CASE WHEN is_root_pattern = 0 THEN 1 ELSE 0 END) as exact_domains
                FROM whitelist 
                WHERE is_active = 1
            ''')
            patterns = dict(cursor.fetchone())
            
            return {
                'total': total,
                'by_category': by_category,
                'root_patterns': patterns['root_patterns'],
                'exact_domains': patterns['exact_domains']
            }
    
    def get_training_data(self, min_confidence=0.7, verified_only=False, limit=1000):
        """Get training data for model retraining"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = '''SELECT url, label, confidence, source 
                       FROM training_data 
                       WHERE confidence >= ? AND used_in_training = 0'''
            
            if verified_only:
                query += ' AND verified = 1'
            
            query += ' LIMIT ?'
            
            cursor.execute(query, (min_confidence, limit))
            return [dict(row) for row in cursor.fetchall()]
    
    def mark_training_data_used(self, data_ids):
        """Mark training data as used after retraining"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(data_ids))
            cursor.execute(
                f'UPDATE training_data SET used_in_training = 1 WHERE id IN ({placeholders})',
                data_ids
            )
    
    def add_model_version(self, version, accuracy, precision, recall, training_samples, notes=None):
        """Record a new model version"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Deactivate previous models
            cursor.execute('UPDATE model_versions SET is_active = 0')
            
            # Add new version
            cursor.execute(
                '''INSERT INTO model_versions 
                   (version, accuracy, precision_score, recall_score, training_samples, is_active, notes)
                   VALUES (?, ?, ?, ?, ?, 1, ?)''',
                (version, accuracy, precision, recall, training_samples, notes)
            )
            return cursor.lastrowid
    
    def get_model_history(self, limit=10):
        """Get model training history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT * FROM model_versions 
                   ORDER BY trained_at DESC 
                   LIMIT ?''',
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_pending_feedback(self, limit=100):
        """Get unprocessed feedback for model training"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT * FROM feedback 
                   WHERE is_processed = 0 
                   ORDER BY created_at ASC 
                   LIMIT ?''',
                (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def mark_feedback_processed(self, feedback_ids):
        """Mark feedback as processed after adding to training data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(feedback_ids))
            cursor.execute(
                f'UPDATE feedback SET is_processed = 1 WHERE id IN ({placeholders})',
                feedback_ids
            )
    
    def get_all_feedback(self, only_unprocessed=False):
        """
        Get all feedback from the database for continuous learning
        
        Args:
            only_unprocessed: if True, only get feedback that hasn't been used for training
        
        Returns:
            list of feedback dictionaries with url, predicted_label, and is_correct
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if only_unprocessed:
                cursor.execute('''
                    SELECT id, url, original_prediction as predicted_label, 
                           (CASE WHEN original_prediction = correct_label THEN 1 ELSE 0 END) as is_correct,
                           correct_label, feedback_type, created_at
                    FROM feedback
                    WHERE is_processed = 0
                    ORDER BY created_at DESC
                ''')
            else:
                cursor.execute('''
                    SELECT id, url, original_prediction as predicted_label,
                           (CASE WHEN original_prediction = correct_label THEN 1 ELSE 0 END) as is_correct,
                           correct_label, feedback_type, created_at
                    FROM feedback
                    ORDER BY created_at DESC
                ''')
            
            rows = cursor.fetchall()
            
            feedback_list = []
            for row in rows:
                feedback_list.append({
                    'id': row['id'],
                    'url': row['url'],
                    'predicted_label': row['predicted_label'],
                    'is_correct': row['is_correct'],
                    'correct_label': row['correct_label'],
                    'feedback_type': row['feedback_type'],
                    'created_at': row['created_at']
                })
            
            return feedback_list
    
    # ========== Chat History Methods ==========
    
    def add_chat_message(self, user_id, session_id, role, message, tokens_used=0):
        """Add a chat message to history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT INTO chat_history 
                   (user_id, session_id, role, message, tokens_used)
                   VALUES (?, ?, ?, ?, ?)''',
                (user_id, session_id, role, message, tokens_used)
            )
            return cursor.lastrowid
    
    def get_chat_history(self, session_id, limit=20):
        """Get chat history for a session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT role, message, created_at 
                   FROM chat_history 
                   WHERE session_id = ? 
                   ORDER BY created_at DESC 
                   LIMIT ?''',
                (session_id, limit)
            )
            messages = [dict(row) for row in cursor.fetchall()]
            # Reverse to get chronological order
            return list(reversed(messages))
    
    def get_user_chat_sessions(self, user_id, limit=10):
        """Get recent chat sessions for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT session_id, 
                          MIN(created_at) as started_at,
                          MAX(created_at) as last_message_at,
                          COUNT(*) as message_count
                   FROM chat_history 
                   WHERE user_id = ? 
                   GROUP BY session_id
                   ORDER BY last_message_at DESC
                   LIMIT ?''',
                (user_id, limit)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_chat_session(self, session_id, user_id):
        """Delete a chat session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM chat_history WHERE session_id = ? AND user_id = ?',
                (session_id, user_id)
            )
            return cursor.rowcount > 0
