"""
Auto-create admin account on Railway startup if it doesn't exist
Set these environment variables in Railway:
- AUTO_CREATE_ADMIN=true
- ADMIN_USERNAME=admin
- ADMIN_EMAIL=your@email.com
- ADMIN_PASSWORD=your_secure_password
"""
import os
from unified_database import init_database

def auto_create_admin():
    """Automatically create admin if environment variables are set"""
    
    # Only run if AUTO_CREATE_ADMIN is set
    if os.environ.get('AUTO_CREATE_ADMIN') != 'true':
        return
    
    username = os.environ.get('ADMIN_USERNAME', 'admin')
    email = os.environ.get('ADMIN_EMAIL')
    password = os.environ.get('ADMIN_PASSWORD')
    
    if not email or not password:
        print("⚠️  AUTO_CREATE_ADMIN is true but ADMIN_EMAIL or ADMIN_PASSWORD not set")
        return
    
    db = init_database()
    if not db:
        print("❌ Database not available for admin creation")
        return
    
    try:
        # Check if admin already exists
        with db.get_connection() as conn:
            cursor = conn.cursor()
            if os.environ.get('DATABASE_URL'):
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = TRUE")
            else:
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1")
            
            result = cursor.fetchone()
            admin_count = result[0] if result else 0
            
            if admin_count > 0:
                print("✓ Admin account already exists, skipping auto-creation")
                return
        
        # Create admin user directly (already verified + admin)
        print(f"Creating admin user: {username} ({email})")
        if hasattr(db, 'create_admin_user'):
            db.create_admin_user(username, email, password)
        else:
            # Fallback for SQLite
            result = db.create_user(username, email, password)
            if isinstance(result, tuple):
                user_id, _ = result
            else:
                user_id = result

            with db.get_connection() as conn:
                cursor = conn.cursor()
                if os.environ.get('DATABASE_URL'):
                    cursor.execute(
                        'UPDATE users SET is_admin = TRUE, email_verified = TRUE, verification_token = NULL WHERE id = %s',
                        (user_id,)
                    )
                else:
                    cursor.execute(
                        'UPDATE users SET is_admin = 1, email_verified = 1, verification_token = NULL WHERE id = ?',
                        (user_id,)
                    )
        
        print(f"✅ Admin account created successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print("⚠️  Remove AUTO_CREATE_ADMIN environment variable after first run!")
        
    except Exception as e:
        print(f"❌ Error auto-creating admin: {e}")

if __name__ == "__main__":
    auto_create_admin()
