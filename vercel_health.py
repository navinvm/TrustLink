"""
Vercel Health Check Endpoint
Simple endpoint to verify deployment is working
"""
from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/health')
@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'platform': 'vercel',
        'database': 'connected' if os.environ.get('DATABASE_URL') else 'not configured',
        'environment': os.environ.get('FLASK_ENV', 'development')
    })

@app.route('/')
def index():
    """Root endpoint"""
    return jsonify({
        'service': 'TrustLink API',
        'version': '2.0',
        'platform': 'vercel',
        'endpoints': {
            'health': '/health',
            'predict': '/predict',
            'api': '/api/*'
        }
    })
