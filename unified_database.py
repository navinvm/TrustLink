"""
Unified Database Configuration
Automatically uses the right database for each platform:
- Railway: PostgreSQL (with DATABASE_URL)
- Vercel: Remote PostgreSQL connection to Railway
- Local: SQLite
"""
import os


def get_database():
    """
    Get the appropriate database instance based on environment
    
    Returns:
        Database instance (SQLite, PostgreSQL, or in-memory)
    """
    # Check if PostgreSQL connection is available
    database_url = os.environ.get('DATABASE_URL')
    
    if database_url:
        # Use PostgreSQL for Railway or Vercel connecting to Railway
        print("🐘 Using PostgreSQL database (Railway)")
        try:
            from railway_database import RailwayDatabase
            return RailwayDatabase()
        except ImportError as e:
            print(f"⚠️ Failed to import PostgreSQL driver: {e}")
            print("⚠️ Install psycopg2-binary: pip install psycopg2-binary")
            raise
    else:
        # Use SQLite for local development
        print("💾 Using SQLite database (Local)")
        from database import Database
        return Database()


# Create a singleton database instance
_db_instance = None

def init_database():
    """Initialize database singleton"""
    global _db_instance
    if _db_instance is None:
        try:
            _db_instance = get_database()
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            _db_instance = None
    return _db_instance


def get_db():
    """Get database instance"""
    if _db_instance is None:
        return init_database()
    return _db_instance
