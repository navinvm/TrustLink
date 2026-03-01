"""
Railway Database Configuration
PostgreSQL database for production deployment
"""
import os
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
import hashlib
import secrets
from datetime import datetime, timedelta


class RailwayDatabase:
    """PostgreSQL Database manager for Railway deployment"""
    
    def __init__(self):
        # Support Vercel Postgres, Railway, and any other PostgreSQL provider
        from unified_database import get_database_url
        self.database_url = get_database_url()

        if not self.database_url:
            raise ValueError("No PostgreSQL URL found. Set DATABASE_URL or POSTGRES_URL in environment variables.")
        
        # Create connection pool
        self.pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,  # min and max connections
            self.database_url
        )
        
        self.init_database()
        print("✓ Railway PostgreSQL database initialized")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = self.pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.pool.putconn(conn)
    
    def init_database(self):
        """Initialize PostgreSQL database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Fix analytics table if it has old schema (metric_name/metric_value)
            cursor.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'analytics' AND column_name = 'metric_name'
            """)
            if cursor.fetchone():
                print("⚠️ Migrating analytics table to new schema...")
                cursor.execute('DROP TABLE analytics')
            
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    email_verified BOOLEAN DEFAULT FALSE,
                    verification_token VARCHAR(255),
                    verification_token_expires TIMESTAMP,
                    is_admin BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Password reset tokens table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS password_reset_tokens (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    token VARCHAR(255) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    used BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # API keys table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    key_hash VARCHAR(255) UNIQUE NOT NULL,
                    key_name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    usage_count INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Scan history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scan_history (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    url TEXT NOT NULL,
                    prediction VARCHAR(50) NOT NULL,
                    confidence REAL NOT NULL,
                    risk_level VARCHAR(50) NOT NULL,
                    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address VARCHAR(50),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Analytics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id SERIAL PRIMARY KEY,
                    date DATE NOT NULL UNIQUE,
                    total_scans INTEGER DEFAULT 0,
                    safe_urls INTEGER DEFAULT 0,
                    phishing_urls INTEGER DEFAULT 0,
                    unique_users INTEGER DEFAULT 0
                )
            ''')
            
            # Whitelist table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS whitelist (
                    id SERIAL PRIMARY KEY,
                    domain VARCHAR(255) UNIQUE NOT NULL,
                    added_by INTEGER,
                    reason TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (added_by) REFERENCES users (id)
                )
            ''')
    
    def _hash_password(self, password):
        """Hash password using PBKDF2 - must match database.py"""
        salt = hashlib.sha256(password.encode()).hexdigest()[:16]
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()

    def _verify_password(self, password, password_hash):
        """Verify password against hash"""
        return self._hash_password(password) == password_hash

    # User management methods
    def create_user(self, username, email, password):
        """Create a new user with email verification"""
        password_hash = self._hash_password(password)
        verification_token = secrets.token_urlsafe(32)
        expires = datetime.now() + timedelta(hours=24)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, verification_token, verification_token_expires)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            ''', (username, email, password_hash, verification_token, expires))
            
            user_id = cursor.fetchone()[0]
            return user_id, verification_token
    
    def get_user_by_username(self, username):
        """Get user by username"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def authenticate_user(self, username, password):
        """Authenticate user and return user data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT * FROM users WHERE username = %s AND is_active = TRUE',
                (username,)
            )
            
            row = cursor.fetchone()
            if not row:
                return None
            
            columns = [desc[0] for desc in cursor.description]
            user = dict(zip(columns, row))
            
            # Verify password
            if not self._verify_password(password, user['password_hash']):
                return None
            
            # Check if email is verified
            if not user.get('email_verified'):
                return {
                    'error': 'email_not_verified',
                    'user_id': user['id'],
                    'email': user['email']
                }
            
            # Update last login
            cursor.execute(
                'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s',
                (user['id'],)
            )
            
            return user
    
    def verify_password(self, username, password):
        """Verify user password"""
        user = self.get_user_by_username(username)
        if not user:
            return False
        return self._verify_password(password, user['password_hash'])
    
    def add_scan_to_history(self, user_id, url, prediction, confidence, risk_level, ip_address=None):
        """Add scan to history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scan_history (user_id, url, prediction, confidence, risk_level, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (user_id, url, prediction, confidence, risk_level, ip_address))
    
    def get_user_history(self, user_id, limit=50):
        """Get user scan history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM scan_history 
                WHERE user_id = %s 
                ORDER BY scanned_at DESC 
                LIMIT %s
            ''', (user_id, limit))
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    # API Key methods
    def create_api_key(self, user_id, key_name):
        """Create a new API key"""
        api_key = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO api_keys (user_id, key_hash, key_name)
                VALUES (%s, %s, %s)
            ''', (user_id, key_hash, key_name))
        
        return api_key
    
    def verify_api_key(self, api_key):
        """Verify API key and return user_id"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id FROM api_keys 
                WHERE key_hash = %s AND is_active = TRUE
            ''', (key_hash,))
            
            row = cursor.fetchone()
            if row:
                # Update last used and usage count
                cursor.execute('''
                    UPDATE api_keys 
                    SET last_used = CURRENT_TIMESTAMP, usage_count = usage_count + 1
                    WHERE key_hash = %s
                ''', (key_hash,))
                return row[0]
            return None
    
    def get_user_api_keys(self, user_id):
        """Get all API keys for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, key_name, created_at, last_used, is_active, usage_count
                FROM api_keys 
                WHERE user_id = %s
                ORDER BY created_at DESC
            ''', (user_id,))
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    # Additional missing methods for Railway compatibility
    
    def validate_api_key(self, api_key):
        """Validate API key and return user_id (alias for verify_api_key)"""
        return self.verify_api_key(api_key)
    
    def revoke_api_key(self, key_id, user_id):
        """Revoke an API key"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE api_keys SET is_active = FALSE WHERE id = %s AND user_id = %s',
                (key_id, user_id)
            )
    
    
    def get_user_scan_history(self, user_id, limit=50, offset=0):
        """Get scan history for a user with pagination"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM scan_history 
                WHERE user_id = %s 
                ORDER BY scanned_at DESC 
                LIMIT %s OFFSET %s
            ''', (user_id, limit, offset))
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def get_user_statistics(self, user_id):
        """Get statistics for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_scans,
                    SUM(CASE WHEN prediction = 'Safe' THEN 1 ELSE 0 END) as safe_count,
                    SUM(CASE WHEN prediction = 'Phishing' THEN 1 ELSE 0 END) as phishing_count,
                    AVG(confidence) as avg_confidence
                FROM scan_history 
                WHERE user_id = %s
            ''', (user_id,))
            
            row = cursor.fetchone()
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
    
    def get_all_scans(self, limit=100, offset=0):
        """Get all scans from all users (admin only)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sh.*, u.username, u.email 
                FROM scan_history sh
                LEFT JOIN users u ON sh.user_id = u.id
                ORDER BY sh.scanned_at DESC 
                LIMIT %s OFFSET %s
            ''', (limit, offset))
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def get_all_users(self, limit=100, offset=0):
        """Get all users (admin only)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, email, created_at, last_login, is_active, email_verified, is_admin
                FROM users 
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s
            ''', (limit, offset))
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    
    def get_system_statistics(self):
        """Get system-wide statistics (admin only)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total users
            cursor.execute('SELECT COUNT(*) as total FROM users')
            total_users = cursor.fetchone()[0]
            
            # Verified users
            cursor.execute('SELECT COUNT(*) as total FROM users WHERE email_verified = TRUE')
            verified_users = cursor.fetchone()[0]
            
            # Total scans
            cursor.execute('SELECT COUNT(*) as total FROM scan_history')
            total_scans = cursor.fetchone()[0]
            
            # Phishing detected
            cursor.execute('SELECT COUNT(*) as total FROM scan_history WHERE prediction = %s', ('Phishing',))
            phishing_scans = cursor.fetchone()[0]
            
            # Safe scans
            cursor.execute('SELECT COUNT(*) as total FROM scan_history WHERE prediction = %s', ('Safe',))
            safe_scans = cursor.fetchone()[0]
            
            # Active API keys
            cursor.execute('SELECT COUNT(*) as total FROM api_keys WHERE is_active = TRUE')
            active_api_keys = cursor.fetchone()[0]
            
            # Scans today
            cursor.execute('''
                SELECT COUNT(*) as total FROM scan_history 
                WHERE DATE(scanned_at) = CURRENT_DATE
            ''')
            scans_today = cursor.fetchone()[0]
            
            # New users this week
            cursor.execute('''
                SELECT COUNT(*) as total FROM users 
                WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
            ''')
            new_users_week = cursor.fetchone()[0]
            
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
    
    def delete_scan_record(self, scan_id, user_id):
        """Delete a single scan record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM scan_history WHERE id = %s AND user_id = %s',
                (scan_id, user_id)
            )
            return cursor.rowcount > 0
    
    def delete_all_user_scans(self, user_id):
        """Delete all scan records for a user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM scan_history WHERE user_id = %s',
                (user_id,)
            )
            return cursor.rowcount
    
    def delete_user_account(self, user_id):
        """Permanently delete a user account and all associated data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Delete all user's data
            cursor.execute('DELETE FROM scan_history WHERE user_id = %s', (user_id,))
            cursor.execute('DELETE FROM api_keys WHERE user_id = %s', (user_id,))
            cursor.execute('DELETE FROM password_reset_tokens WHERE user_id = %s', (user_id,))
            cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
            return cursor.rowcount > 0
    
    def get_user_by_email(self, email):
        """Get user by email"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None

    def create_password_reset_token(self, email):
        """Create password reset token for user"""
        user = self.get_user_by_email(email)
        if not user:
            return None

        token = secrets.token_urlsafe(32)
        expires = datetime.now() + timedelta(hours=1)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO password_reset_tokens (user_id, token, expires_at)
                VALUES (%s, %s, %s)
            ''', (user['id'], token, expires))

        return token, user

    def verify_password_reset_token(self, token):
        """Verify password reset token and return token data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT prt.*, u.id as user_id FROM password_reset_tokens prt
                JOIN users u ON prt.user_id = u.id
                WHERE prt.token = %s AND prt.expires_at > %s AND prt.used = FALSE
            ''', (token, datetime.now()))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None

    def reset_password(self, token, new_password):
        """Reset user password using token"""
        token_data = self.verify_password_reset_token(token)
        if not token_data:
            return False

        new_password_hash = self._hash_password(new_password)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Update password
            cursor.execute(
                'UPDATE users SET password_hash = %s WHERE id = %s',
                (new_password_hash, token_data['user_id'])
            )
            # Mark token as used
            cursor.execute(
                'UPDATE password_reset_tokens SET used = TRUE WHERE token = %s',
                (token,)
            )
        return True

    def verify_email(self, token):
        """Verify user email with token"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM users
                WHERE verification_token = %s
                AND verification_token_expires > %s
                AND email_verified = FALSE
            ''', (token, datetime.now()))
            row = cursor.fetchone()
            if not row:
                raise ValueError("Invalid or expired verification token")
            columns = [desc[0] for desc in cursor.description]
            user = dict(zip(columns, row))
            cursor.execute('''
                UPDATE users
                SET email_verified = TRUE, verification_token = NULL, verification_token_expires = NULL
                WHERE id = %s
            ''', (user['id'],))
            return user

    def resend_verification_email(self, user_id):
        """Generate new verification token for user"""
        verification_token = secrets.token_urlsafe(32)
        expires = datetime.now() + timedelta(hours=24)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users
                SET verification_token = %s, verification_token_expires = %s
                WHERE id = %s AND email_verified = FALSE
            ''', (verification_token, expires, user_id))

        return verification_token

    def create_admin_user(self, username, email, password):
        """Create an admin user with email already verified"""
        password_hash = self._hash_password(password)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, email_verified, is_admin)
                VALUES (%s, %s, %s, TRUE, TRUE)
                RETURNING id
            ''', (username, email, password_hash))
            user_id = cursor.fetchone()[0]
        return user_id

    def add_scan_record(self, user_id, url, prediction, confidence, risk_level, ip_address=None):
        """Add a scan record to history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO scan_history (user_id, url, prediction, confidence, risk_level, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (user_id, url, prediction, confidence, risk_level, ip_address))
            return cursor.fetchone()[0]

    def update_daily_analytics(self, date, scans_delta=1, safe_delta=0, phishing_delta=0):
        """Update daily analytics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO analytics (date, total_scans, safe_urls, phishing_urls)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (date) DO UPDATE SET
                    total_scans = analytics.total_scans + %s,
                    safe_urls = analytics.safe_urls + %s,
                    phishing_urls = analytics.phishing_urls + %s
            ''', (date, scans_delta, safe_delta, phishing_delta,
                  scans_delta, safe_delta, phishing_delta))

    def add_feedback(self, scan_id, user_id, url, original_prediction, correct_label, feedback_type):
        """Add user feedback for incorrect predictions"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    scan_id INTEGER,
                    user_id INTEGER,
                    url TEXT NOT NULL,
                    original_prediction VARCHAR(50) NOT NULL,
                    correct_label VARCHAR(50) NOT NULL,
                    feedback_type VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_processed BOOLEAN DEFAULT FALSE
                )
            ''')
            cursor.execute('''
                INSERT INTO feedback
                (scan_id, user_id, url, original_prediction, correct_label, feedback_type)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (scan_id, user_id, url, original_prediction, correct_label, feedback_type))
            return cursor.fetchone()[0]

    def get_pending_feedback(self, limit=100):
        """Get unprocessed feedback for model training"""
        self._ensure_feedback_table()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM feedback
                WHERE is_processed = FALSE
                ORDER BY created_at ASC
                LIMIT %s
            ''', (limit,))
            rows = cursor.fetchall()
            if not rows:
                return []
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    def mark_feedback_processed(self, feedback_ids):
        """Mark feedback as processed after adding to training data"""
        if not feedback_ids:
            return
        self._ensure_feedback_table()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f'UPDATE feedback SET is_processed = TRUE WHERE id = ANY(%s)',
                (list(feedback_ids),)
            )

    def get_all_feedback(self, only_unprocessed=False):
        """Get all feedback from the database"""
        self._ensure_feedback_table()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if only_unprocessed:
                cursor.execute('''
                    SELECT id, url, original_prediction as predicted_label,
                           CASE WHEN original_prediction = correct_label THEN 1 ELSE 0 END as is_correct,
                           correct_label, feedback_type, created_at
                    FROM feedback WHERE is_processed = FALSE ORDER BY created_at DESC
                ''')
            else:
                cursor.execute('''
                    SELECT id, url, original_prediction as predicted_label,
                           CASE WHEN original_prediction = correct_label THEN 1 ELSE 0 END as is_correct,
                           correct_label, feedback_type, created_at
                    FROM feedback ORDER BY created_at DESC
                ''')
            rows = cursor.fetchall()
            if not rows:
                return []
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    def _ensure_feedback_table(self):
        """Ensure feedback table exists"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    scan_id INTEGER,
                    user_id INTEGER,
                    url TEXT NOT NULL,
                    original_prediction VARCHAR(50) NOT NULL,
                    correct_label VARCHAR(50) NOT NULL,
                    feedback_type VARCHAR(50) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_processed BOOLEAN DEFAULT FALSE
                )
            ''')

    def _ensure_ml_tables(self):
        """Ensure ML-related tables exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS external_validations (
                    id SERIAL PRIMARY KEY,
                    url TEXT NOT NULL,
                    url_hash VARCHAR(64) UNIQUE NOT NULL,
                    is_threat BOOLEAN,
                    confidence REAL,
                    source VARCHAR(100) NOT NULL,
                    threat_type VARCHAR(100),
                    validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS training_data (
                    id SERIAL PRIMARY KEY,
                    url TEXT NOT NULL,
                    label INTEGER NOT NULL,
                    confidence REAL,
                    source VARCHAR(100) NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    used_in_training BOOLEAN DEFAULT FALSE,
                    verified BOOLEAN DEFAULT FALSE
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_versions (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(100) NOT NULL,
                    accuracy REAL,
                    precision_score REAL,
                    recall_score REAL,
                    training_samples INTEGER,
                    trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT FALSE,
                    notes TEXT
                )
            ''')

    def _ensure_whitelist_table(self):
        """Ensure full whitelist table exists with all columns"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS whitelist (
                    id SERIAL PRIMARY KEY,
                    domain VARCHAR(255) UNIQUE NOT NULL,
                    domain_type VARCHAR(50),
                    category VARCHAR(100),
                    description TEXT,
                    added_by INTEGER,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    is_root_pattern BOOLEAN DEFAULT FALSE,
                    verified BOOLEAN DEFAULT FALSE,
                    reason TEXT,
                    FOREIGN KEY (added_by) REFERENCES users (id)
                )
            ''')

    def _ensure_chat_tables(self):
        """Ensure chat history table exists"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    session_id VARCHAR(255) NOT NULL,
                    role VARCHAR(50) NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tokens_used INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')

    def add_external_validation(self, url, is_threat, confidence, source, threat_type=None, metadata=None):
        """Store external validation results"""
        self._ensure_ml_tables()
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO external_validations
                (url, url_hash, is_threat, confidence, source, threat_type, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (url_hash) DO UPDATE SET
                    is_threat = EXCLUDED.is_threat,
                    confidence = EXCLUDED.confidence,
                    source = EXCLUDED.source,
                    threat_type = EXCLUDED.threat_type,
                    validated_at = CURRENT_TIMESTAMP,
                    metadata = EXCLUDED.metadata
                RETURNING id
            ''', (url, url_hash, is_threat, confidence, source, threat_type, str(metadata)))
            return cursor.fetchone()[0]

    def get_external_validation(self, url):
        """Get cached external validation result for URL"""
        self._ensure_ml_tables()
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM external_validations
                WHERE url_hash = %s
                ORDER BY validated_at DESC
                LIMIT 1
            ''', (url_hash,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None

    def add_training_data(self, url, label, confidence, source, verified=False):
        """Add data to training pool"""
        self._ensure_ml_tables()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO training_data (url, label, confidence, source, verified)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            ''', (url, label, confidence, source, verified))
            return cursor.fetchone()[0]

    def get_training_data(self, min_confidence=0.7, verified_only=False, limit=1000):
        """Get training data for model retraining"""
        self._ensure_ml_tables()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = '''SELECT url, label, confidence, source
                       FROM training_data
                       WHERE confidence >= %s AND used_in_training = FALSE'''
            params = [min_confidence]
            if verified_only:
                query += ' AND verified = TRUE'
            query += ' LIMIT %s'
            params.append(limit)
            cursor.execute(query, params)
            rows = cursor.fetchall()
            if not rows:
                return []
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    def mark_training_data_used(self, data_ids):
        """Mark training data as used after retraining"""
        if not data_ids:
            return
        self._ensure_ml_tables()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE training_data SET used_in_training = TRUE WHERE id = ANY(%s)',
                (list(data_ids),)
            )

    def add_model_version(self, version, accuracy, precision, recall, training_samples, notes=None):
        """Record a new model version"""
        self._ensure_ml_tables()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE model_versions SET is_active = FALSE')
            cursor.execute('''
                INSERT INTO model_versions
                (version, accuracy, precision_score, recall_score, training_samples, is_active, notes)
                VALUES (%s, %s, %s, %s, %s, TRUE, %s)
                RETURNING id
            ''', (version, accuracy, precision, recall, training_samples, notes))
            return cursor.fetchone()[0]

    def get_model_history(self, limit=10):
        """Get model training history"""
        self._ensure_ml_tables()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM model_versions
                ORDER BY trained_at DESC
                LIMIT %s
            ''', (limit,))
            rows = cursor.fetchall()
            if not rows:
                return []
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    # ========== Whitelist Management ==========

    def add_whitelist_domain(self, domain, domain_type, category=None, description=None,
                             added_by=None, is_root_pattern=False, verified=False):
        """Add a domain to the custom whitelist"""
        self._ensure_whitelist_table()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO whitelist
                (domain, domain_type, category, description, added_by, is_root_pattern, verified)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (domain, domain_type, category, description, added_by, is_root_pattern, verified))
            return cursor.fetchone()[0]

    def get_whitelist_domains(self, active_only=True, include_root_patterns=True):
        """Get all whitelisted domains"""
        self._ensure_whitelist_table()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = 'SELECT * FROM whitelist WHERE 1=1'
            params = []
            if active_only:
                query += ' AND is_active = TRUE'
            if not include_root_patterns:
                query += ' AND is_root_pattern = FALSE'
            query += ' ORDER BY domain'
            cursor.execute(query, params)
            rows = cursor.fetchall()
            if not rows:
                return []
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    def get_whitelist_domain_by_id(self, whitelist_id):
        """Get a specific whitelist entry by ID"""
        self._ensure_whitelist_table()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM whitelist WHERE id = %s', (whitelist_id,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None

    def update_whitelist_domain(self, whitelist_id, **kwargs):
        """Update a whitelist entry"""
        self._ensure_whitelist_table()
        allowed_fields = ['domain', 'domain_type', 'category', 'description',
                          'is_active', 'is_root_pattern', 'verified']
        updates = []
        values = []
        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = %s")
                values.append(value)
        if not updates:
            return False
        values.append(whitelist_id)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE whitelist SET {', '.join(updates)} WHERE id = %s",
                values
            )
            return cursor.rowcount > 0

    def delete_whitelist_domain(self, whitelist_id):
        """Delete a whitelist entry"""
        self._ensure_whitelist_table()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM whitelist WHERE id = %s', (whitelist_id,))
            return cursor.rowcount > 0

    def deactivate_whitelist_domain(self, whitelist_id):
        """Soft delete - deactivate a whitelist entry"""
        return self.update_whitelist_domain(whitelist_id, is_active=False)

    def search_whitelist(self, search_term):
        """Search whitelist by domain or description"""
        self._ensure_whitelist_table()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM whitelist
                WHERE (domain ILIKE %s OR description ILIKE %s) AND is_active = TRUE
                ORDER BY domain
            ''', (f'%{search_term}%', f'%{search_term}%'))
            rows = cursor.fetchall()
            if not rows:
                return []
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    def get_whitelist_stats(self):
        """Get statistics about the whitelist"""
        self._ensure_whitelist_table()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM whitelist WHERE is_active = TRUE')
            total = cursor.fetchone()[0]
            cursor.execute('''
                SELECT category, COUNT(*) as count
                FROM whitelist
                WHERE is_active = TRUE
                GROUP BY category
                ORDER BY count DESC
            ''')
            by_category = [{'category': r[0], 'count': r[1]} for r in cursor.fetchall()]
            cursor.execute('''
                SELECT
                    SUM(CASE WHEN is_root_pattern = TRUE THEN 1 ELSE 0 END) as root_patterns,
                    SUM(CASE WHEN is_root_pattern = FALSE THEN 1 ELSE 0 END) as exact_domains
                FROM whitelist WHERE is_active = TRUE
            ''')
            row = cursor.fetchone()
            return {
                'total': total,
                'by_category': by_category,
                'root_patterns': row[0] or 0,
                'exact_domains': row[1] or 0
            }

    # ========== Chat History Methods ==========

    def add_chat_message(self, user_id, session_id, role, message, tokens_used=0):
        """Add a chat message to history"""
        self._ensure_chat_tables()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO chat_history (user_id, session_id, role, message, tokens_used)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            ''', (user_id, session_id, role, message, tokens_used))
            return cursor.fetchone()[0]

    def get_chat_history(self, session_id, limit=20):
        """Get chat history for a session"""
        self._ensure_chat_tables()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT role, message, created_at FROM chat_history
                WHERE session_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            ''', (session_id, limit))
            rows = cursor.fetchall()
            if not rows:
                return []
            columns = [desc[0] for desc in cursor.description]
            messages = [dict(zip(columns, row)) for row in rows]
            return list(reversed(messages))

    def get_user_chat_sessions(self, user_id, limit=10):
        """Get recent chat sessions for a user"""
        self._ensure_chat_tables()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT session_id,
                       MIN(created_at) as started_at,
                       MAX(created_at) as last_message_at,
                       COUNT(*) as message_count
                FROM chat_history
                WHERE user_id = %s
                GROUP BY session_id
                ORDER BY last_message_at DESC
                LIMIT %s
            ''', (user_id, limit))
            rows = cursor.fetchall()
            if not rows:
                return []
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]

    def delete_chat_session(self, session_id, user_id):
        """Delete a chat session"""
        self._ensure_chat_tables()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM chat_history WHERE session_id = %s AND user_id = %s',
                (session_id, user_id)
            )
            return cursor.rowcount > 0

    # ========== ML Model Storage in PostgreSQL ==========

    def _ensure_model_table(self):
        """Ensure model storage table exists"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ml_models (
                    id SERIAL PRIMARY KEY,
                    model_name VARCHAR(100) NOT NULL,
                    model_data BYTEA NOT NULL,
                    accuracy REAL,
                    training_samples INTEGER,
                    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')

    def save_model_to_db(self, model_name, model_bytes, accuracy=None, training_samples=None):
        """Save ML model binary to PostgreSQL"""
        self._ensure_model_table()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Deactivate old versions
            cursor.execute(
                'UPDATE ml_models SET is_active = FALSE WHERE model_name = %s',
                (model_name,)
            )
            # Save new version
            cursor.execute('''
                INSERT INTO ml_models (model_name, model_data, accuracy, training_samples, is_active)
                VALUES (%s, %s, %s, %s, TRUE)
                RETURNING id
            ''', (model_name, psycopg2.Binary(model_bytes), accuracy, training_samples))
            return cursor.fetchone()[0]

    def load_model_from_db(self, model_name):
        """Load ML model binary from PostgreSQL"""
        self._ensure_model_table()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT model_data, accuracy, training_samples, saved_at
                FROM ml_models
                WHERE model_name = %s AND is_active = TRUE
                ORDER BY saved_at DESC
                LIMIT 1
            ''', (model_name,))
            row = cursor.fetchone()
            if row:
                return {
                    'model_data': bytes(row[0]),
                    'accuracy': row[1],
                    'training_samples': row[2],
                    'saved_at': row[3]
                }
            return None

    def get_analytics(self, days=30):
        """Get analytics for the last N days"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    DATE(scanned_at) as date,
                    COUNT(*) as total_scans,
                    SUM(CASE WHEN prediction = 'Safe' THEN 1 ELSE 0 END) as safe_urls,
                    SUM(CASE WHEN prediction = 'Phishing' THEN 1 ELSE 0 END) as phishing_urls,
                    COUNT(DISTINCT user_id) as unique_users
                FROM scan_history 
                WHERE scanned_at >= CURRENT_DATE - INTERVAL '%s days'
                GROUP BY DATE(scanned_at)
                ORDER BY date DESC
            ''' % days)
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
