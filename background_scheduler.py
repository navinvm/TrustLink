#!/usr/bin/env python3
"""
TrustLink - Background Scheduler for Online Deployment
Runs continuous learning as a background job when app is online
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
from scheduled_training import ContinuousLearningSystem

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BackgroundTrainingScheduler:
    """Manages background training jobs for online deployment"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.training_system = ContinuousLearningSystem()
        logger.info("Background training scheduler initialized")
    
    def run_training_job(self):
        """Job that runs the daily training"""
        try:
            logger.info("=" * 70)
            logger.info("Starting scheduled training job...")
            logger.info(f"Time: {datetime.now().isoformat()}")
            
            should_train, reason = self.training_system.should_train_today()
            logger.info(f"Training check: {reason}")
            
            if should_train:
                logger.info("Training will proceed")
                metrics = self.training_system.run_daily_training(
                    phishing_limit=500,
                    safe_limit=100
                )
                
                if metrics:
                    logger.info("✅ Training completed successfully!")
                    logger.info(f"New accuracy: {metrics['accuracy']:.2%}")
                else:
                    logger.warning("⚠️ Training skipped (insufficient data)")
            else:
                logger.info("⏭️ Training skipped (not due yet)")
            
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"❌ Training job failed: {e}", exc_info=True)
    
    def start(self):
        """Start the background scheduler"""
        try:
            # Schedule daily training at 2 AM UTC
            self.scheduler.add_job(
                self.run_training_job,
                trigger=CronTrigger(hour=2, minute=0),
                id='daily_training',
                name='Daily Model Training',
                replace_existing=True
            )
            
            self.scheduler.start()
            logger.info("✅ Background scheduler started")
            logger.info("📅 Daily training scheduled for 2:00 AM UTC")
            
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")
            raise
    
    def stop(self):
        """Stop the background scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Background scheduler stopped")
    
    def get_next_run_time(self):
        """Get the next scheduled run time"""
        job = self.scheduler.get_job('daily_training')
        if job:
            return job.next_run_time
        return None


# Global scheduler instance
_scheduler = None


def init_scheduler(app=None):
    """Initialize the background scheduler (call this from app.py)"""
    global _scheduler
    
    if _scheduler is None:
        _scheduler = BackgroundTrainingScheduler()
        _scheduler.start()
        
        # Register shutdown handler if Flask app is provided
        if app:
            import atexit
            atexit.register(lambda: _scheduler.stop())
        
        return _scheduler
    
    return _scheduler


def get_scheduler():
    """Get the global scheduler instance"""
    return _scheduler


if __name__ == '__main__':
    # Standalone mode - runs as a separate process
    import signal
    import sys
    
    scheduler = BackgroundTrainingScheduler()
    scheduler.start()
    
    logger.info("Background scheduler running...")
    logger.info("Press Ctrl+C to stop")
    
    # Keep the script running
    def signal_handler(sig, frame):
        logger.info("\nShutting down scheduler...")
        scheduler.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Keep alive
    try:
        while True:
            import time
            time.sleep(60)
    except KeyboardInterrupt:
        scheduler.stop()
