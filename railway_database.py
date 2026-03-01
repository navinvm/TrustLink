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
        self.database_url = os.environ.get('DATABASE_URL')
        
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
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
                    metric_name VARCHAR(255) NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    
    # User management methods
    def create_user(self, username, email, password):
        """Create a new user with email verification"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
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
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            if user['password_hash'] != password_hash:
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
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return user['password_hash'] == password_hash
    
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
    
    def add_scan_record(self, user_id, url, prediction, confidence, risk_level, ip_address=None):
        """Add a scan record to history (alias for add_scan_to_history)"""
        return self.add_scan_to_history(user_id, url, prediction, confidence, risk_level, ip_address)
    
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

        new_password_hash = hashlib.sha256(new_password.encode()).hexdigest()

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
