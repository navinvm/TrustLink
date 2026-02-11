"""
TrustLink Database Connection Pool
Implements connection pooling for scalability
"""
import sqlite3
import threading
import queue
import time
from contextlib import contextmanager


class DatabaseConnectionPool:
    """Thread-safe database connection pool"""
    
    def __init__(self, database_path, pool_size=10, max_overflow=5, timeout=30):
        """
        Initialize connection pool
        
        Args:
            database_path: Path to SQLite database
            pool_size: Number of connections to maintain
            max_overflow: Additional connections allowed beyond pool_size
            timeout: Timeout for getting connection from pool
        """
        self.database_path = database_path
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.timeout = timeout
        
        self._pool = queue.Queue(maxsize=pool_size + max_overflow)
        self._lock = threading.Lock()
        self._connection_count = 0
        self._active_connections = 0
        
        # Statistics
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'pool_size': pool_size,
            'hits': 0,
            'misses': 0,
            'timeouts': 0
        }
        
        # Pre-create pool connections
        for _ in range(pool_size):
            self._create_connection()
        
        print(f"[DB Pool] Initialized with {pool_size} connections, max_overflow={max_overflow}")
    
    def _create_connection(self):
        """Create a new database connection"""
        conn = sqlite3.connect(
            self.database_path,
            check_same_thread=False,
            timeout=10
        )
        conn.row_factory = sqlite3.Row
        
        # Enable WAL mode for better concurrency
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA synchronous=NORMAL')
        conn.execute('PRAGMA cache_size=-64000')  # 64MB cache
        conn.execute('PRAGMA temp_store=MEMORY')
        
        with self._lock:
            self._connection_count += 1
            self.stats['total_connections'] += 1
        
        self._pool.put(conn)
        return conn
    
    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool
        
        Usage:
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                # Use connection
        """
        try:
            # Try to get connection from pool
            try:
                conn = self._pool.get(timeout=self.timeout)
                self.stats['hits'] += 1
            except queue.Empty:
                # Pool is empty
                with self._lock:
                    if self._connection_count < (self.pool_size + self.max_overflow):
                        # Create overflow connection
                        conn = self._create_overflow_connection()
                        self.stats['misses'] += 1
                    else:
                        # Wait for connection
                        self.stats['timeouts'] += 1
                        raise Exception("Connection pool exhausted. All connections in use.")
            
            with self._lock:
                self._active_connections += 1
                self.stats['active_connections'] = self._active_connections
            
            yield conn
            
        finally:
            # Return connection to pool
            with self._lock:
                self._active_connections -= 1
                self.stats['active_connections'] = self._active_connections
            
            try:
                # Rollback any uncommitted transactions
                conn.rollback()
                self._pool.put_nowait(conn)
            except queue.Full:
                # Pool is full, close overflow connection
                conn.close()
                with self._lock:
                    self._connection_count -= 1
    
    def _create_overflow_connection(self):
        """Create an overflow connection"""
        conn = sqlite3.connect(
            self.database_path,
            check_same_thread=False,
            timeout=10
        )
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA synchronous=NORMAL')
        
        self._connection_count += 1
        return conn
    
    def get_stats(self):
        """Get pool statistics"""
        return {
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow,
            'total_connections': self._connection_count,
            'active_connections': self._active_connections,
            'available_connections': self._pool.qsize(),
            'pool_hits': self.stats['hits'],
            'pool_misses': self.stats['misses'],
            'timeouts': self.stats['timeouts']
        }
    
    def close_all(self):
        """Close all connections in pool"""
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
                with self._lock:
                    self._connection_count -= 1
            except queue.Empty:
                break
        
        print(f"[DB Pool] Closed all connections")
    
    def healthcheck(self):
        """Check pool health"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return True, "Database pool healthy"
        except Exception as e:
            return False, f"Database pool error: {str(e)}"


class DatabasePoolManager:
    """Manages database connection pools for different databases"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.pools = {}
        self._initialized = True
    
    def get_pool(self, database_path, pool_size=10, max_overflow=5):
        """Get or create connection pool for database"""
        if database_path not in self.pools:
            self.pools[database_path] = DatabaseConnectionPool(
                database_path,
                pool_size=pool_size,
                max_overflow=max_overflow
            )
        
        return self.pools[database_path]
    
    def close_all_pools(self):
        """Close all connection pools"""
        for pool in self.pools.values():
            pool.close_all()
        self.pools.clear()
    
    def get_all_stats(self):
        """Get statistics for all pools"""
        return {
            path: pool.get_stats()
            for path, pool in self.pools.items()
        }


# Global pool manager
pool_manager = DatabasePoolManager()
