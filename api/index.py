"""
Vercel Serverless Function Handler for TrustLink
Handles initialization gracefully in serverless environment
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Disable background scheduler in serverless
os.environ['AUTO_ML_TRAINING'] = 'false'
os.environ['FLASK_ENV'] = 'production'

# Import the Flask app with detailed error handling
app = None
init_error = None

try:
    print("🔧 Initializing TrustLink in Vercel serverless mode...")
    from app import app as flask_app
    app = flask_app

    # Auto-create admin account if configured
    if os.environ.get('AUTO_CREATE_ADMIN', '').lower() == 'true':
        try:
            import create_admin_on_startup
            create_admin_on_startup.auto_create_admin()
        except Exception as admin_err:
            print(f"⚠️ Admin creation skipped: {admin_err}")

    print("✓ TrustLink initialized successfully")
except Exception as e:
    print(f"❌ Error importing app: {e}")
    import traceback
    traceback.print_exc()
    init_error = str(e)
    
    # Create a minimal error app
    from flask import Flask, jsonify, request as flask_request
    app = Flask(__name__)
    
    @app.route('/')
    @app.route('/<path:path>')
    def error(path=''):
        return jsonify({
            'error': 'Application failed to initialize',
            'message': 'The serverless function encountered an initialization error',
            'details': init_error,
            'help': 'Check Vercel function logs for more information'
        }), 500

# Export the app directly for Vercel (modern format)
# Vercel will automatically detect and use this
