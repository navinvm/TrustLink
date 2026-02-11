"""
Gunicorn configuration for TrustLink
Optimized for serverless and container deployments
"""
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8080')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('GUNICORN_WORKERS', '2'))  # Reduced for serverless
worker_class = 'sync'  # Changed from gthread for better stability
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = 'trustlink'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Graceful timeout for workers
graceful_timeout = 30

# Preload app for better memory usage
preload_app = True

# Worker restart on code changes (development only)
reload = os.getenv('FLASK_ENV') == 'development'

# SSL (if needed)
keyfile = None
certfile = None

def on_starting(server):
    """Called just before the master process is initialized."""
    print("🚀 Starting TrustLink server...")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    print("🔄 Reloading workers...")

def when_ready(server):
    """Called just after the server is started."""
    print(f"✅ Server is ready. Listening on {bind}")

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    print(f"⚠️  Worker {worker.pid} was interrupted")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    print(f"❌ Worker {worker.pid} aborted (likely timeout or memory issue)")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    print(f"✓ Worker {worker.pid} spawned")

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    print(f"✓ Worker {worker.pid} initialized")

def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    print(f"⚠️  Worker {worker.pid} exited")

def child_exit(server, worker):
    """Called just after a worker has been reaped."""
    pass

def nworkers_changed(server, new_value, old_value):
    """Called just after num_workers has been changed."""
    print(f"📊 Workers changed from {old_value} to {new_value}")

def on_exit(server):
    """Called just before exiting Gunicorn."""
    print("👋 Shutting down TrustLink server...")
