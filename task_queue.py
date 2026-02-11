"""
TrustLink Async Task Queue
Implements background task processing with Celery
Falls back to threading if Celery not available
"""
import os
import json
from datetime import datetime
import threading
import queue
import time

# Try to import Celery
try:
    from celery import Celery
    from celery.result import AsyncResult
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False


class TaskQueue:
    """Async task queue manager with Celery and fallback to threading"""
    
    def __init__(self):
        self.celery_app = None
        self.thread_queue = queue.Queue()
        self.workers = []
        self.is_running = False
        
        # Initialize Celery if available
        if CELERY_AVAILABLE:
            self._init_celery()
        else:
            self._init_thread_workers()
        
        print(f"[TaskQueue] Initialized with backend: {'Celery' if self.celery_enabled else 'Threading'}")
    
    def _init_celery(self):
        """Initialize Celery app"""
        try:
            broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/1')
            result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
            
            self.celery_app = Celery(
                'trustlink',
                broker=broker_url,
                backend=result_backend
            )
            
            self.celery_app.conf.update(
                task_serializer='json',
                accept_content=['json'],
                result_serializer='json',
                timezone='UTC',
                enable_utc=True,
                task_track_started=True,
                task_time_limit=300,  # 5 minutes
                task_soft_time_limit=240,  # 4 minutes
                worker_prefetch_multiplier=4,
                worker_max_tasks_per_child=1000,
            )
            
            # Test connection
            self.celery_app.control.inspect().stats()
            print(f"[TaskQueue] Connected to Celery: {broker_url}")
            
        except Exception as e:
            print(f"[TaskQueue] Celery initialization failed: {e}. Using threading fallback.")
            self.celery_app = None
            self._init_thread_workers()
    
    def _init_thread_workers(self, num_workers=4):
        """Initialize thread-based workers as fallback"""
        self.is_running = True
        
        for i in range(num_workers):
            worker = threading.Thread(
                target=self._worker_thread,
                daemon=True,
                name=f"TaskWorker-{i}"
            )
            worker.start()
            self.workers.append(worker)
        
        print(f"[TaskQueue] Started {num_workers} thread workers")
    
    def _worker_thread(self):
        """Worker thread for processing tasks"""
        while self.is_running:
            try:
                task = self.thread_queue.get(timeout=1)
                if task:
                    func, args, kwargs = task['func'], task['args'], task['kwargs']
                    try:
                        func(*args, **kwargs)
                    except Exception as e:
                        print(f"[TaskQueue] Task error: {e}")
                    finally:
                        self.thread_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[TaskQueue] Worker error: {e}")
    
    @property
    def celery_enabled(self):
        """Check if Celery is available"""
        return self.celery_app is not None
    
    def enqueue(self, func, *args, **kwargs):
        """
        Enqueue a task for background processing
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Task ID (Celery) or None (threading)
        """
        if self.celery_enabled:
            # Use Celery
            task = func.apply_async(args=args, kwargs=kwargs)
            return task.id
        else:
            # Use thread queue
            self.thread_queue.put({
                'func': func,
                'args': args,
                'kwargs': kwargs,
                'queued_at': time.time()
            })
            return None
    
    def get_task_status(self, task_id):
        """Get status of a task by ID (Celery only)"""
        if self.celery_enabled and task_id:
            task = AsyncResult(task_id, app=self.celery_app)
            return {
                'id': task_id,
                'status': task.state,
                'result': task.result if task.ready() else None,
                'successful': task.successful() if task.ready() else False
            }
        return None
    
    def stop(self):
        """Stop the task queue"""
        self.is_running = False
        if self.celery_enabled:
            self.celery_app.control.shutdown()
        print("[TaskQueue] Stopped")


# Global task queue instance
task_queue = TaskQueue()


# Decorator for async tasks
def async_task(func):
    """Decorator to make a function execute asynchronously"""
    if CELERY_AVAILABLE and task_queue.celery_enabled:
        # Return Celery task
        return task_queue.celery_app.task(func)
    else:
        # Return wrapper that enqueues to thread pool
        def wrapper(*args, **kwargs):
            return task_queue.enqueue(func, *args, **kwargs)
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper


# Example async tasks for TrustLink

@async_task
def retrain_model_async(training_data):
    """Asynchronously retrain ML model"""
    print(f"[AsyncTask] Retraining model with {len(training_data)} samples")
    # Import here to avoid circular dependencies
    from ml_learning import MLLearningSystem
    learner = MLLearningSystem()
    result = learner.retrain_model()
    print(f"[AsyncTask] Model retrained successfully")
    return result


@async_task
def batch_scan_async(urls, user_id):
    """Asynchronously scan multiple URLs"""
    print(f"[AsyncTask] Batch scanning {len(urls)} URLs for user {user_id}")
    # Import here to avoid circular dependencies
    from ml_features import MLPhishingDetector
    from database import Database
    
    detector = MLPhishingDetector()
    db = Database()
    results = []
    
    for url in urls:
        try:
            features = detector.extract_features(url)
            prediction, confidence = detector.predict(features)
            
            # Save to database
            db.save_scan(user_id, url, prediction, confidence)
            
            results.append({
                'url': url,
                'prediction': prediction,
                'confidence': confidence
            })
        except Exception as e:
            print(f"[AsyncTask] Error scanning {url}: {e}")
            results.append({
                'url': url,
                'error': str(e)
            })
    
    print(f"[AsyncTask] Batch scan complete: {len(results)} URLs processed")
    return results


@async_task
def send_email_notification_async(recipient, subject, body):
    """Asynchronously send email notification"""
    print(f"[AsyncTask] Sending email to {recipient}")
    try:
        from email_notifier import EmailNotifier
        notifier = EmailNotifier()
        notifier.send_email(recipient, subject, body)
        print(f"[AsyncTask] Email sent successfully")
        return True
    except Exception as e:
        print(f"[AsyncTask] Email send failed: {e}")
        return False


@async_task
def cleanup_old_data_async(days=90):
    """Asynchronously clean up old data"""
    print(f"[AsyncTask] Cleaning up data older than {days} days")
    from database import Database
    from datetime import datetime, timedelta
    
    db = Database()
    cutoff_date = datetime.now() - timedelta(days=days)
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Delete old scan history
        cursor.execute('''
            DELETE FROM scan_history
            WHERE scanned_at < ?
        ''', (cutoff_date.isoformat(),))
        
        deleted_scans = cursor.rowcount
        
        # Delete old external validations
        cursor.execute('''
            DELETE FROM external_validations
            WHERE validated_at < ?
        ''', (cutoff_date.isoformat(),))
        
        deleted_validations = cursor.rowcount
        
        conn.commit()
    
    print(f"[AsyncTask] Cleanup complete: {deleted_scans} scans, {deleted_validations} validations")
    return {
        'deleted_scans': deleted_scans,
        'deleted_validations': deleted_validations
    }


@async_task
def update_whitelist_async(domains):
    """Asynchronously update whitelist"""
    print(f"[AsyncTask] Updating whitelist with {len(domains)} domains")
    from database import Database
    
    db = Database()
    count = 0
    
    for domain in domains:
        try:
            db.add_to_whitelist(domain, is_root_pattern=True)
            count += 1
        except Exception as e:
            print(f"[AsyncTask] Error adding {domain}: {e}")
    
    print(f"[AsyncTask] Whitelist updated: {count} domains added")
    return count
