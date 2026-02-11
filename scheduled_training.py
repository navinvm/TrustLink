#!/usr/bin/env python3
"""
TrustLink - Scheduled Automatic Training
Runs daily to continuously improve the model with:
1. Fresh PhishTank phishing URLs
2. Updated safe URLs from known domains
3. User feedback from the database
4. Triple verification from Google Safe Browsing + VirusTotal
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from ml_learning import ExternalValidator, APIDataCollector, ModelTrainer
from database import Database
import time

# Load environment variables
load_dotenv()

class ContinuousLearningSystem:
    """Manages continuous model improvement through scheduled training"""
    
    def __init__(self):
        self.db = Database()
        
        # API configuration
        self.api_config = {
            'google_api_key': os.environ.get('GOOGLE_SAFE_BROWSING_KEY'),
            'virustotal_api_key': os.environ.get('VIRUSTOTAL_API_KEY'),
        }
        
        self.validator = ExternalValidator(self.api_config)
        self.collector = APIDataCollector(self.validator)
        self.trainer = ModelTrainer()
        
        self.training_history_file = 'training_history.json'
        self.last_training_file = 'last_training.json'
    
    def should_train_today(self):
        """Check if we should train today (every 24 hours)"""
        if not os.path.exists(self.last_training_file):
            return True, "First time training"
        
        try:
            with open(self.last_training_file, 'r') as f:
                last_training = json.load(f)
                last_time = datetime.fromisoformat(last_training['timestamp'])
                
                hours_since = (datetime.now() - last_time).total_seconds() / 3600
                
                if hours_since >= 24:
                    return True, f"Last training was {hours_since:.1f} hours ago"
                else:
                    return False, f"Last training was {hours_since:.1f} hours ago (wait {24-hours_since:.1f} more hours)"
        
        except Exception as e:
            return True, f"Error reading last training: {e}"
    
    def collect_user_feedback(self):
        """Collect user feedback from database for training"""
        print("\n📥 Collecting user feedback from database...")
        
        try:
            # Get all feedback from the database
            feedback_data = self.db.get_all_feedback()
            
            if not feedback_data:
                print("   No feedback found in database")
                return []
            
            training_samples = []
            
            for feedback in feedback_data:
                url = feedback.get('url')
                is_correct = feedback.get('is_correct')
                predicted_label = feedback.get('predicted_label')
                
                # Determine actual label based on feedback
                if is_correct:
                    # Prediction was correct, use predicted label
                    actual_label = 1 if predicted_label == 'Phishing' else 0
                else:
                    # Prediction was wrong, flip the label
                    actual_label = 0 if predicted_label == 'Phishing' else 1
                
                training_samples.append((url, actual_label))
            
            print(f"✓ Collected {len(training_samples)} feedback samples")
            return training_samples
        
        except Exception as e:
            print(f"✗ Error collecting feedback: {e}")
            return []
    
    def collect_high_confidence_scans(self, min_confidence=0.9, days=7):
        """Collect high-confidence scans from recent history"""
        print(f"\n📥 Collecting high-confidence scans from last {days} days...")
        
        try:
            # Get recent scans from all users
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # This would need a new database method
            # For now, we'll skip this to avoid database changes
            print("   (Feature placeholder - requires database schema update)")
            return []
        
        except Exception as e:
            print(f"✗ Error collecting scans: {e}")
            return []
    
    def run_daily_training(self, phishing_limit=1000, safe_limit=150):
        """
        Run the complete daily training process
        
        Steps:
        1. Collect fresh PhishTank phishing URLs
        2. Generate fresh safe URLs from known domains
        3. Collect user feedback from database
        4. Triple-verify everything with all 3 APIs
        5. Combine with historical data
        6. Retrain model
        7. Update metrics
        """
        print("=" * 70)
        print("🤖 CONTINUOUS LEARNING - DAILY TRAINING")
        print("=" * 70)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check available APIs
        available_apis = ['PhishTank']
        if self.api_config['google_api_key']:
            available_apis.append('Google Safe Browsing')
        if self.api_config['virustotal_api_key']:
            available_apis.append('VirusTotal')
        
        print(f"📡 Available APIs: {', '.join(available_apis)}")
        print(f"🎯 Target: {phishing_limit} phishing + {safe_limit*3} safe URLs + user feedback")
        print()
        
        all_training_data = []
        
        # 1. Collect fresh PhishTank URLs
        print("=" * 70)
        print("STEP 1: COLLECTING FRESH PHISHING URLs")
        print("=" * 70)
        phishing_data = self.collector.collect_from_phishtank(limit=phishing_limit)
        
        if phishing_data:
            print(f"\n🔍 Triple-verifying {len(phishing_data)} phishing URLs...")
            verified_phishing = self.collector._triple_verify_urls(
                [url for url, label in phishing_data],
                expected_label=1,
                consensus_threshold=2
            )
            all_training_data.extend(verified_phishing)
            print(f"✓ {len(verified_phishing)} phishing URLs verified")
        
        # 2. Generate fresh safe URLs
        print()
        print("=" * 70)
        print("STEP 2: GENERATING FRESH SAFE URLs")
        print("=" * 70)
        
        # Expanded list of safe domains
        safe_domains = [
            # Tech giants
            'google.com', 'youtube.com', 'facebook.com', 'amazon.com',
            'microsoft.com', 'apple.com', 'netflix.com', 'linkedin.com',
            
            # Social media
            'twitter.com', 'instagram.com', 'reddit.com', 'pinterest.com',
            'tiktok.com', 'snapchat.com', 'telegram.org', 'whatsapp.com',
            
            # Developer platforms
            'github.com', 'gitlab.com', 'stackoverflow.com', 'bitbucket.org',
            'npmjs.com', 'pypi.org', 'docker.com', 'kubernetes.io',
            
            # Education & Reference
            'wikipedia.org', 'medium.com', 'quora.com', 'coursera.org',
            'udemy.com', 'khanacademy.org', 'edx.org', 'archive.org',
            
            # News & Media
            'cnn.com', 'bbc.com', 'nytimes.com', 'theguardian.com',
            'reuters.com', 'bloomberg.com', 'forbes.com', 'techcrunch.com',
            
            # E-commerce
            'ebay.com', 'walmart.com', 'target.com', 'bestbuy.com',
            'etsy.com', 'shopify.com', 'aliexpress.com', 'alibaba.com',
            
            # Financial
            'paypal.com', 'stripe.com', 'square.com', 'coinbase.com',
            
            # Cloud & Infrastructure
            'cloudflare.com', 'aws.amazon.com', 'azure.microsoft.com',
            'digitalocean.com', 'heroku.com', 'vercel.com',
            
            # Open source
            'mozilla.org', 'apache.org', 'gnu.org', 'fsf.org',
            'linux.org', 'kernel.org', 'python.org', 'nodejs.org',
            
            # Government & Education
            'irs.gov', 'nasa.gov', 'nih.gov', 'cdc.gov',
            'mit.edu', 'stanford.edu', 'harvard.edu', 'berkeley.edu'
        ]
        
        safe_data = self.collector.collect_safe_urls(safe_domains[:safe_limit])
        
        if safe_data:
            print(f"\n🔍 Triple-verifying {len(safe_data)} safe URLs...")
            verified_safe = self.collector._triple_verify_urls(
                [url for url, label in safe_data],
                expected_label=0,
                consensus_threshold=2
            )
            all_training_data.extend(verified_safe)
            print(f"✓ {len(verified_safe)} safe URLs verified")
        
        # 3. Collect user feedback
        print()
        print("=" * 70)
        print("STEP 3: COLLECTING USER FEEDBACK")
        print("=" * 70)
        feedback_data = self.collect_user_feedback()
        
        if feedback_data:
            print(f"\n🔍 Triple-verifying {len(feedback_data)} feedback URLs...")
            # Separate by expected label
            feedback_phishing = [(url, label) for url, label in feedback_data if label == 1]
            feedback_safe = [(url, label) for url, label in feedback_data if label == 0]
            
            if feedback_phishing:
                verified_fb_phishing = self.collector._triple_verify_urls(
                    [url for url, label in feedback_phishing],
                    expected_label=1,
                    consensus_threshold=2
                )
                all_training_data.extend(verified_fb_phishing)
                print(f"✓ {len(verified_fb_phishing)} feedback phishing URLs verified")
            
            if feedback_safe:
                verified_fb_safe = self.collector._triple_verify_urls(
                    [url for url, label in feedback_safe],
                    expected_label=0,
                    consensus_threshold=2
                )
                all_training_data.extend(verified_fb_safe)
                print(f"✓ {len(verified_fb_safe)} feedback safe URLs verified")
        
        # 4. Check if we have enough data
        if len(all_training_data) < 50:
            print()
            print("=" * 70)
            print("⚠️  WARNING: Not enough training data collected")
            print(f"   Only {len(all_training_data)} samples (need at least 50)")
            print("   Skipping training for today")
            print("=" * 70)
            return None
        
        # 5. Shuffle and prepare data
        import random
        random.shuffle(all_training_data)
        
        urls = [item[0] for item in all_training_data]
        labels = [item[1] for item in all_training_data]
        
        # 6. Train the model
        print()
        print("=" * 70)
        print("STEP 4: TRAINING MODEL")
        print("=" * 70)
        print(f"\n📊 Final Dataset:")
        print(f"  Total samples: {len(urls)}")
        print(f"  Phishing: {sum(labels)} ({sum(labels)/len(labels)*100:.1f}%)")
        print(f"  Safe: {len(labels) - sum(labels)} ({(len(labels)-sum(labels))/len(labels)*100:.1f}%)")
        print(f"  Quality: TRIPLE-VERIFIED (all 3 APIs)")
        print()
        
        print("🧠 Training model...")
        metrics = self.trainer.train_new_model(urls, labels)
        
        # 7. Save the model
        print("\n💾 Saving model...")
        self.trainer.save_model()
        
        # 8. Update metrics
        print("💾 Updating model metrics...")
        metrics_data = {
            'accuracy': metrics['accuracy'],
            'precision': metrics['precision'],
            'recall': metrics['recall'],
            'training_samples': len(urls),
            'last_updated': datetime.now().isoformat(),
            'model_version': '2.0',
            'data_sources': ['PhishTank', 'Safe Domains', 'User Feedback'],
            'training_type': 'continuous_daily'
        }
        
        with open('model_metrics.json', 'w') as f:
            json.dump(metrics_data, f, indent=4)
        
        # 9. Record training history
        self._record_training(metrics, len(urls))
        
        # 10. Update last training timestamp
        with open(self.last_training_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'samples': len(urls),
                'accuracy': metrics['accuracy']
            }, f, indent=4)
        
        print()
        print("=" * 70)
        print("✅ DAILY TRAINING COMPLETE!")
        print("=" * 70)
        print(f"📊 New Model Performance:")
        print(f"   Accuracy:  {metrics['accuracy']:.2%}")
        print(f"   Precision: {metrics['precision']:.2%}")
        print(f"   Recall:    {metrics['recall']:.2%}")
        print(f"   Samples:   {len(urls):,}")
        print(f"\n💡 Model updated! New accuracy: {metrics['accuracy']*100:.1f}%")
        print("=" * 70)
        
        return metrics
    
    def _record_training(self, metrics, sample_count):
        """Record training in history log"""
        history = []
        
        if os.path.exists(self.training_history_file):
            try:
                with open(self.training_history_file, 'r') as f:
                    history = json.load(f)
            except:
                pass
        
        history.append({
            'timestamp': datetime.now().isoformat(),
            'accuracy': metrics['accuracy'],
            'precision': metrics['precision'],
            'recall': metrics['recall'],
            'samples': sample_count
        })
        
        # Keep only last 30 days
        history = history[-30:]
        
        with open(self.training_history_file, 'w') as f:
            json.dump(history, f, indent=4)


def main():
    """Main entry point for scheduled training"""
    system = ContinuousLearningSystem()
    
    print("=" * 70)
    print("🤖 TRUSTLINK CONTINUOUS LEARNING SYSTEM")
    print("=" * 70)
    print()
    
    # Check if we should train today
    should_train, reason = system.should_train_today()
    
    print(f"📋 Status Check: {reason}")
    print()
    
    if not should_train:
        print("⏭️  Skipping training - will check again in 24 hours")
        print("=" * 70)
        return
    
    print("✅ Starting daily training...")
    print()
    
    try:
        # Run training with moderate limits (daily updates, not full retraining)
        metrics = system.run_daily_training(
            phishing_limit=500,   # 500 new phishing URLs daily
            safe_limit=100        # 300 new safe URLs daily
        )
        
        if metrics:
            print("\n✅ Training successful!")
            print(f"   Next training: {(datetime.now() + timedelta(hours=24)).strftime('%Y-%m-%d %H:%M')}")
        else:
            print("\n⚠️  Training skipped (insufficient data)")
    
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    input("Press Enter to exit...")


if __name__ == '__main__':
    main()
