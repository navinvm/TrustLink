#!/usr/bin/env python3
"""
TrustLink - Quick Model Training
Trains the model immediately with default settings (no prompts)
"""

import os
from dotenv import load_dotenv
from ml_learning import train_model_from_apis
import shutil
from datetime import datetime

# Load environment variables
load_dotenv()

print("=" * 70)
print("🚀 QUICK MODEL TRAINING")
print("=" * 70)
print()

# Get API keys
api_config = {
    'google_api_key': os.environ.get('GOOGLE_SAFE_BROWSING_KEY'),
    'virustotal_api_key': os.environ.get('VIRUSTOTAL_API_KEY'),
}

# Check available APIs
available_apis = []
if api_config['google_api_key']:
    available_apis.append('Google Safe Browsing')
if api_config['virustotal_api_key']:
    available_apis.append('VirusTotal')
available_apis.append('PhishTank')

print(f"📡 Available APIs: {', '.join(available_apis)}")
print(f"⚡ Mode: Parallel processing enabled")
print(f"📊 Dataset: 2000 phishing + 600 safe URLs")
print()

# Backup current model
print("💾 Backing up current model...")
try:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if os.path.exists('models/model.pkl'):
        backup_path = f'models/model_backup_{timestamp}.pkl'
        shutil.copy('models/model.pkl', backup_path)
        print(f"✓ Backup saved to: {backup_path}")
except Exception as e:
    print(f"⚠️  Could not backup model: {e}")

print()
print("=" * 70)
print("🚀 STARTING TRAINING...")
print("=" * 70)
print()

# Train with default settings
try:
    metrics = train_model_from_apis(
        api_config=api_config,
        phishing_limit=2000,  # Collect 2000 phishing URLs
        safe_limit=200        # Use 200 safe domains (600 URLs)
    )
    
    if metrics:
        print()
        print("=" * 70)
        print("✅ TRAINING COMPLETE!")
        print("=" * 70)
        print()
        print(f"📊 New Model Performance:")
        print(f"   Accuracy:  {metrics['accuracy']:.2%}")
        print(f"   Precision: {metrics['precision']:.2%}")
        print(f"   Recall:    {metrics['recall']:.2%}")
        print(f"   Samples:   {metrics['training_samples']:,}")
        print()
        print(f"💡 The new accuracy ({metrics['accuracy']*100:.1f}%) will appear on all pages!")
        print(f"   Restart the application to load the new model.")
    else:
        print()
        print("❌ Training failed - not enough data collected.")

except Exception as e:
    print()
    print(f"❌ Error during training: {e}")
    print("   Your original model is still intact.")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
input("Press Enter to exit...")
