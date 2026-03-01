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

app = None
init_error = None

try:
    print("🔧 Initializing TrustLink in Vercel serverless mode...")

    # Auto-create admin account if configured (runs on cold start)
    try:
        from create_admin_on_startup import auto_create_admin
        auto_create_admin()
    except Exception as admin_err:
        print(f"⚠️ Admin creation skipped: {admin_err}")

    from app import app as flask_app
    app = flask_app
    print("✓ TrustLink initialized successfully")

except Exception as e:
    print(f"❌ Error importing app: {e}")
    import traceback
    traceback.print_exc()
    init_error = str(e)

    from flask import Flask, jsonify
    app = Flask(__name__)

    @app.route('/')
    @app.route('/<path:path>')
    def error(path=''):
        return jsonify({
            'error': 'Application failed to initialize',
            'message': init_error,
            'help': 'Check Vercel function logs for more information'
        }), 500
