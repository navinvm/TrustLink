"""
WSGI Entry Point for TrustLink
Provides better error handling and worker crash prevention
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

def application(environ, start_response):
    """WSGI application with error handling"""
    try:
        from app import app
        return app(environ, start_response)
    except Exception as e:
        # Log the error
        print(f"❌ WSGI Application Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        
        # Return 500 error
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [b'Application failed to start. Check logs for details.']

# For gunicorn
if __name__ == "__main__":
    print("⚠️  This file should be run via gunicorn, not directly")
    print("Usage: gunicorn wsgi:application --config gunicorn_config.py")
