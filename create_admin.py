"""
Create Admin User for TrustLink
Run this script to create an admin account in the database
"""
import os
import sys
from unified_database import init_database

def create_admin_user(username, email, password):
    """Create an admin user in the database"""
    
    # Initialize database
    db = init_database()
    
    if db is None:
        print("❌ Database not available")
        return False
    
    try:
        # Create the user
        user_id = db.create_user(username, email, password)
        print(f"✅ User created with ID: {user_id}")
        
        # Make them admin
        if hasattr(db, 'get_connection'):
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if using PostgreSQL or SQLite
                if os.environ.get('DATABASE_URL'):
                    # PostgreSQL
                    cursor.execute(
                        'UPDATE users SET is_admin = TRUE WHERE id = %s',
                        (user_id,)
                    )
                else:
                    # SQLite
                    cursor.execute(
                        'UPDATE users SET is_admin = 1 WHERE id = ?',
                        (user_id,)
                    )
                
                print(f"✅ User '{username}' is now an admin!")
                return True
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("TrustLink Admin User Creation")
    print("=" * 50)
    
    # Get admin details
    if len(sys.argv) == 4:
        username = sys.argv[1]
        email = sys.argv[2]
        password = sys.argv[3]
    else:
        print("\nEnter admin account details:")
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = input("Password: ").strip()
    
    if not username or not email or not password:
        print("❌ All fields are required!")
        sys.exit(1)
    
    # Validate
    if len(password) < 8:
        print("❌ Password must be at least 8 characters!")
        sys.exit(1)
    
    print(f"\nCreating admin user:")
    print(f"  Username: {username}")
    print(f"  Email: {email}")
    print(f"  Admin: Yes")
    
    confirm = input("\nProceed? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Cancelled.")
        sys.exit(0)
    
    # Create the admin
    success = create_admin_user(username, email, password)
    
    if success:
        print("\n" + "=" * 50)
        print("✅ Admin account created successfully!")
        print("=" * 50)
        print(f"\nLogin at: https://your-app.railway.app/login")
        print(f"Username: {username}")
        print(f"Password: {password}")
        print("\n⚠️  Save these credentials securely!")
    else:
        print("\n❌ Failed to create admin account")
        sys.exit(1)
