"""
Unified Database Configuration
Automatically uses PostgreSQL if available, otherwise SQLite for local dev.
Supports: Vercel Postgres (POSTGRES_URL), Railway (DATABASE_URL), Local (SQLite)
"""
import os


def get_database_url():
    """Get the PostgreSQL URL from any known environment variable"""
    url = (
        os.environ.get('DATABASE_URL') or
        os.environ.get('POSTGRES_URL') or
        os.environ.get('POSTGRES_PRISMA_URL') or
        os.environ.get('POSTGRES_URL_NON_POOLING')
    )
    # psycopg2 requires postgresql:// not postgres://
    if url and url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    return url


def get_database():
    """
    Get the appropriate database instance based on environment.
    Returns PostgreSQL if any postgres URL is found, otherwise SQLite.
    """
    database_url = get_database_url()

    if database_url:
        print("🐘 Using PostgreSQL database")
        try:
            from railway_database import RailwayDatabase
            return RailwayDatabase()
        except ImportError as e:
            print(f"⚠️ Failed to import PostgreSQL driver: {e}")
            print("⚠️ Install psycopg2-binary: pip install psycopg2-binary")
            raise
    else:
        print("💾 Using SQLite database (Local)")
        from database import Database
        return Database()


# Singleton database instance
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
