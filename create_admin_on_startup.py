"""
Auto-create admin account on startup if it doesn't exist.
Set these environment variables in Vercel/Railway:
- AUTO_CREATE_ADMIN=true
- ADMIN_USERNAME=admin  (default: admin)
- ADMIN_EMAIL=your@email.com
- ADMIN_PASSWORD=YourSecurePassword123!
"""
import os


def auto_create_admin():
    """Automatically create admin if environment variables are set"""

    if os.environ.get('AUTO_CREATE_ADMIN', '').lower() != 'true':
        return

    username = os.environ.get('ADMIN_USERNAME', 'admin')
    email = os.environ.get('ADMIN_EMAIL')
    password = os.environ.get('ADMIN_PASSWORD')

    if not email or not password:
        print("⚠️  AUTO_CREATE_ADMIN=true but ADMIN_EMAIL or ADMIN_PASSWORD not set")
        return

    try:
        from unified_database import init_database
        db = init_database()
        if not db:
            print("❌ Database not available for admin creation")
            return

        # Check if a verified admin already exists
        with db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = TRUE AND email_verified = TRUE")
            except Exception:
                cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1 AND email_verified = 1")
            result = cursor.fetchone()
            verified_admin_count = result[0] if result else 0

        if verified_admin_count > 0:
            print("✓ Verified admin account already exists, skipping auto-creation")
            return

        # Fix any existing unverified admin accounts first
        with db.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "UPDATE users SET email_verified = TRUE, is_admin = TRUE, is_active = TRUE WHERE username = %s",
                    (username,)
                )
                fixed = cursor.rowcount
            except Exception:
                cursor.execute(
                    "UPDATE users SET email_verified = 1, is_admin = 1, is_active = 1 WHERE username = ?",
                    (username,)
                )
                fixed = cursor.rowcount

        if fixed > 0:
            print(f"✅ Fixed existing admin account: {username} (set email_verified=TRUE, is_admin=TRUE)")
            return

        # Create admin user (verified + admin from the start)
        if hasattr(db, 'create_admin_user'):
            db.create_admin_user(username, email, password)
        else:
            # Fallback for SQLite
            result = db.create_user(username, email, password)
            user_id = result[0] if isinstance(result, tuple) else result
            with db.get_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(
                        'UPDATE users SET is_admin = TRUE, email_verified = TRUE, verification_token = NULL WHERE id = %s',
                        (user_id,)
                    )
                except Exception:
                    cursor.execute(
                        'UPDATE users SET is_admin = 1, email_verified = 1, verification_token = NULL WHERE id = ?',
                        (user_id,)
                    )

        print(f"✅ Admin account created: {username} ({email})")
        print("⚠️  Set AUTO_CREATE_ADMIN=false after first successful login!")

    except Exception as e:
        print(f"❌ Error creating admin: {e}")


if __name__ == "__main__":
    auto_create_admin()
