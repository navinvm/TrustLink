"""
TrustLink Monitoring and Metrics
Provides application metrics and health checks for scalability
"""
import os
import time
import psutil
from datetime import datetime
from flask import jsonify
from functools import wraps


class MetricsCollector:
    """Collects and stores application metrics"""
    
    def __init__(self):
        self.metrics = {
            'requests': {
                'total': 0,
                'by_endpoint': {},
                'by_status': {},
            },
            'errors': {
                'total': 0,
                'by_type': {},
            },
            'performance': {
                'response_times': [],
                'avg_response_time': 0,
            },
            'cache': {
                'hits': 0,
                'misses': 0,
            },
            'database': {
                'queries': 0,
                'slow_queries': 0,
            }
        }
        self.start_time = time.time()
    
    def record_request(self, endpoint, status_code, response_time):
        """Record a request metric"""
        self.metrics['requests']['total'] += 1
        
        # By endpoint
        if endpoint not in self.metrics['requests']['by_endpoint']:
            self.metrics['requests']['by_endpoint'][endpoint] = 0
        self.metrics['requests']['by_endpoint'][endpoint] += 1
        
        # By status
        status_group = f"{status_code // 100}xx"
        if status_group not in self.metrics['requests']['by_status']:
            self.metrics['requests']['by_status'][status_group] = 0
        self.metrics['requests']['by_status'][status_group] += 1
        
        # Response time
        self.metrics['performance']['response_times'].append(response_time)
        if len(self.metrics['performance']['response_times']) > 1000:
            self.metrics['performance']['response_times'].pop(0)
        
        # Calculate average
        if self.metrics['performance']['response_times']:
            self.metrics['performance']['avg_response_time'] = sum(
                self.metrics['performance']['response_times']
            ) / len(self.metrics['performance']['response_times'])
    
    def record_error(self, error_type):
        """Record an error metric"""
        self.metrics['errors']['total'] += 1
        if error_type not in self.metrics['errors']['by_type']:
            self.metrics['errors']['by_type'][error_type] = 0
        self.metrics['errors']['by_type'][error_type] += 1
    
    def record_cache_hit(self):
        """Record cache hit"""
        self.metrics['cache']['hits'] += 1
    
    def record_cache_miss(self):
        """Record cache miss"""
        self.metrics['cache']['misses'] += 1
    
    def record_database_query(self, execution_time):
        """Record database query"""
        self.metrics['database']['queries'] += 1
        if execution_time > 0.1:  # Slow query threshold
            self.metrics['database']['slow_queries'] += 1
    
    def get_metrics(self):
        """Get all metrics"""
        uptime = time.time() - self.start_time
        
        # Calculate cache hit rate
        cache_total = self.metrics['cache']['hits'] + self.metrics['cache']['misses']
        cache_hit_rate = (self.metrics['cache']['hits'] / cache_total * 100) if cache_total > 0 else 0
        
        return {
            'uptime_seconds': round(uptime, 2),
            'uptime_formatted': self._format_uptime(uptime),
            'requests': self.metrics['requests'],
            'errors': self.metrics['errors'],
            'performance': {
                'avg_response_time_ms': round(self.metrics['performance']['avg_response_time'] * 1000, 2),
                'requests_per_second': round(self.metrics['requests']['total'] / uptime, 2) if uptime > 0 else 0
            },
            'cache': {
                **self.metrics['cache'],
                'hit_rate_percent': round(cache_hit_rate, 2)
            },
            'database': self.metrics['database']
        }
    
    def _format_uptime(self, seconds):
        """Format uptime in human-readable format"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")
        
        return " ".join(parts)
    
    def reset(self):
        """Reset all metrics"""
        self.__init__()


class HealthChecker:
    """Comprehensive health check system"""
    
    def __init__(self, app=None):
        self.app = app
        self.checks = {}
    
    def register_check(self, name, check_func):
        """Register a health check function"""
        self.checks[name] = check_func
    
    def run_checks(self):
        """Run all health checks"""
        results = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'instance_id': os.environ.get('INSTANCE_ID', 'unknown'),
            'checks': {}
        }
        
        all_healthy = True
        
        for name, check_func in self.checks.items():
            try:
                is_healthy, message = check_func()
                results['checks'][name] = {
                    'status': 'healthy' if is_healthy else 'unhealthy',
                    'message': message
                }
                if not is_healthy:
                    all_healthy = False
            except Exception as e:
                results['checks'][name] = {
                    'status': 'error',
                    'message': str(e)
                }
                all_healthy = False
        
        results['status'] = 'healthy' if all_healthy else 'unhealthy'
        return results
    
    def add_system_checks(self):
        """Add standard system health checks"""
        
        def check_memory():
            """Check memory usage"""
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                return False, f"High memory usage: {memory.percent}%"
            return True, f"Memory usage: {memory.percent}%"
        
        def check_disk():
            """Check disk usage"""
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                return False, f"High disk usage: {disk.percent}%"
            return True, f"Disk usage: {disk.percent}%"
        
        def check_cpu():
            """Check CPU usage"""
            cpu = psutil.cpu_percent(interval=1)
            if cpu > 90:
                return False, f"High CPU usage: {cpu}%"
            return True, f"CPU usage: {cpu}%"
        
        self.register_check('memory', check_memory)
        self.register_check('disk', check_disk)
        self.register_check('cpu', check_cpu)


# Global instances
metrics_collector = MetricsCollector()
health_checker = HealthChecker()


def monitor_endpoint(func):
    """Decorator to monitor endpoint performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            response = func(*args, **kwargs)
            response_time = time.time() - start_time
            
            # Extract status code
            if isinstance(response, tuple):
                status_code = response[1] if len(response) > 1 else 200
            else:
                status_code = getattr(response, 'status_code', 200)
            
            # Record metrics
            endpoint = func.__name__
            metrics_collector.record_request(endpoint, status_code, response_time)
            
            return response
            
        except Exception as e:
            response_time = time.time() - start_time
            metrics_collector.record_request(func.__name__, 500, response_time)
            metrics_collector.record_error(type(e).__name__)
            raise
    
    return wrapper


def setup_monitoring(app):
    """Setup monitoring endpoints for the Flask app"""
    
    @app.route('/metrics')
    def get_metrics():
        """Get application metrics"""
        return jsonify(metrics_collector.get_metrics())
    
    @app.route('/health')
    def health_check():
        """Comprehensive health check endpoint"""
        results = health_checker.run_checks()
        status_code = 200 if results['status'] == 'healthy' else 503
        return jsonify(results), status_code
    
    @app.route('/health/ready')
    def readiness_check():
        """Kubernetes readiness probe"""
        # Check if app can handle requests
        results = health_checker.run_checks()
        if results['status'] == 'healthy':
            return jsonify({'status': 'ready'}), 200
        return jsonify({'status': 'not ready'}), 503
    
    @app.route('/health/live')
    def liveness_check():
        """Kubernetes liveness probe"""
        # Check if app is alive (basic check)
        return jsonify({
            'status': 'alive',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    print("[Monitoring] Endpoints registered: /metrics, /health, /health/ready, /health/live")
