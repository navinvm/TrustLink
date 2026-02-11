#!/usr/bin/env python3
"""
TrustLink - Train Model from External APIs
Collects verified phishing/safe URLs from external threat intelligence sources
and trains the ML model with real-world data.
"""

import os
from dotenv import load_dotenv
from ml_learning import train_model_from_apis

# Load environment variables from .env file
load_dotenv()

def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║          TrustLink - API-Based Model Training                  ║
╚════════════════════════════════════════════════════════════════╝

This script will:
1. Collect verified phishing URLs from PhishTank (free API)
2. Generate safe URL samples from known legitimate domains
3. Train the ML model with this data
4. Update model metrics automatically

""")
    
    # Get API keys from environment variables (optional)
    api_config = {
        'google_api_key': os.environ.get('GOOGLE_SAFE_BROWSING_KEY'),
        'virustotal_api_key': os.environ.get('VIRUSTOTAL_API_KEY'),
    }
    
    # Check which APIs are available
    available_apis = []
    if api_config['google_api_key']:
        available_apis.append('Google Safe Browsing')
    if api_config['virustotal_api_key']:
        available_apis.append('VirusTotal')
    available_apis.append('PhishTank (Free)')
    
    print(f"📡 Available APIs: {', '.join(available_apis)}\n")
    
    # Ask user for confirmation
    print("⚠️  WARNING: This will replace the current model!")
    print("   The current model will be backed up automatically.\n")
    
    response = input("Continue with training? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("❌ Training cancelled.")
        return
    
    # Get training parameters
    try:
        phishing_limit = int(input("\nHow many phishing URLs to collect? (default 2000): ").strip() or "2000")
        safe_limit = int(input("How many safe domains to use? (default 200): ").strip() or "200")
    except ValueError:
        print("⚠️  Invalid input, using defaults (2000 phishing, 200 safe)")
        phishing_limit = 2000
        safe_limit = 200
    
    print("\n" + "="*70)
    print("🚀 Starting model training...")
    print("="*70 + "\n")
    
    # Backup current model
    import shutil
    from datetime import datetime
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if os.path.exists('models/model.pkl'):
            backup_path = f'models/model_backup_{timestamp}.pkl'
            shutil.copy('models/model.pkl', backup_path)
            print(f"✓ Current model backed up to: {backup_path}\n")
    except Exception as e:
        print(f"⚠️  Could not backup model: {e}\n")
    
    # Train the model
    try:
        metrics = train_model_from_apis(
            api_config=api_config,
            phishing_limit=phishing_limit,
            safe_limit=safe_limit
        )
        
        if metrics:
            print("\n✅ Training completed successfully!")
            print(f"\n📊 New Model Performance:")
            print(f"   Accuracy:  {metrics['accuracy']:.2%}")
            print(f"   Precision: {metrics['precision']:.2%}")
            print(f"   Recall:    {metrics['recall']:.2%}")
            print(f"\n💡 The model is now ready to use!")
            print("   Restart the application to load the new model.")
        else:
            print("\n❌ Training failed - not enough data collected.")
            
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        print("   Your original model is still intact.")
        import traceback
        traceback.print_exc()
    
    # Keep window open
    input("\n\nPress Enter to exit...")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Training cancelled by user.")
        input("\nPress Enter to exit...")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
