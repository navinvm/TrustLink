"""
TrustLink Error Handlers and Logging
Centralized error handling with proper logging
"""
from flask import jsonify, render_template, request
import logging
import traceback
from datetime import datetime


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trustlink.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('trustlink')


def register_error_handlers(app):
    """Register error handlers for Flask app"""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle 400 Bad Request"""
        logger.warning(f"Bad request from {request.remote_addr}: {request.url}")
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'error': 'Bad request',
                'status': 'error',
                'message': str(error.description) if hasattr(error, 'description') else 'Invalid request'
            }), 400
        
        return render_template('error.html', 
                             error_code=400,
                             error_message='Bad Request',
                             error_description='The request could not be understood by the server.'), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """Handle 401 Unauthorized"""
        logger.warning(f"Unauthorized access attempt from {request.remote_addr}: {request.url}")
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'error': 'Unauthorized',
                'status': 'error',
                'message': 'Authentication required'
            }), 401
        
        return render_template('error.html',
                             error_code=401,
                             error_message='Unauthorized',
                             error_description='Authentication is required to access this resource.'), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """Handle 403 Forbidden"""
        logger.warning(f"Forbidden access attempt from {request.remote_addr}: {request.url}")
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'error': 'Forbidden',
                'status': 'error',
                'message': 'Access denied'
            }), 403
        
        return render_template('error.html',
                             error_code=403,
                             error_message='Forbidden',
                             error_description='You do not have permission to access this resource.'), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 Not Found"""
        logger.info(f"404 error from {request.remote_addr}: {request.url}")
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'error': 'Not found',
                'status': 'error',
                'message': 'The requested resource was not found'
            }), 404
        
        return render_template('error.html',
                             error_code=404,
                             error_message='Not Found',
                             error_description='The requested page could not be found.'), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """Handle 405 Method Not Allowed"""
        logger.warning(f"Method not allowed from {request.remote_addr}: {request.method} {request.url}")
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'error': 'Method not allowed',
                'status': 'error',
                'message': f'The {request.method} method is not allowed for this endpoint'
            }), 405
        
        return render_template('error.html',
                             error_code=405,
                             error_message='Method Not Allowed',
                             error_description=f'The {request.method} method is not allowed for this endpoint.'), 405
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle 429 Too Many Requests"""
        logger.warning(f"Rate limit exceeded from {request.remote_addr}: {request.url}")
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'error': 'Rate limit exceeded',
                'status': 'error',
                'message': 'Too many requests. Please try again later.',
                'retry_after': 3600
            }), 429
        
        return render_template('error.html',
                             error_code=429,
                             error_message='Rate Limit Exceeded',
                             error_description='Too many requests. Please try again in an hour.'), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server Error"""
        logger.error(f"Internal server error from {request.remote_addr}: {request.url}")
        logger.error(f"Error details: {str(error)}")
        logger.error(traceback.format_exc())
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'error': 'Internal server error',
                'status': 'error',
                'message': 'An unexpected error occurred. Please try again later.'
            }), 500
        
        return render_template('error.html',
                             error_code=500,
                             error_message='Internal Server Error',
                             error_description='An unexpected error occurred. Our team has been notified.'), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        """Handle 503 Service Unavailable"""
        logger.error(f"Service unavailable from {request.remote_addr}: {request.url}")
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'error': 'Service unavailable',
                'status': 'error',
                'message': 'The service is temporarily unavailable. Please try again later.'
            }), 503
        
        return render_template('error.html',
                             error_code=503,
                             error_message='Service Unavailable',
                             error_description='The service is temporarily unavailable. Please try again later.'), 503
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle uncaught exceptions"""
        logger.error(f"Uncaught exception from {request.remote_addr}: {request.url}")
        logger.error(f"Exception: {str(error)}")
        logger.error(traceback.format_exc())
        
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({
                'error': 'Internal error',
                'status': 'error',
                'message': 'An unexpected error occurred'
            }), 500
        
        return render_template('error.html',
                             error_code=500,
                             error_message='Internal Error',
                             error_description='An unexpected error occurred. Please try again.'), 500


class AppLogger:
    """Application-specific logging utilities"""
    
    @staticmethod
    def log_scan(user_id, url, prediction, confidence, risk_level):
        """Log URL scan"""
        logger.info(f"Scan - User: {user_id}, URL: {url[:50]}..., "
                   f"Prediction: {prediction}, Confidence: {confidence:.2f}%, Risk: {risk_level}")
    
    @staticmethod
    def log_api_request(endpoint, user_id, ip_address, method='POST'):
        """Log API request"""
        logger.info(f"API {method} {endpoint} - User: {user_id}, IP: {ip_address}")
    
    @staticmethod
    def log_model_retrain(version, accuracy, samples):
        """Log model retraining"""
        logger.info(f"Model retrained - Version: {version}, Accuracy: {accuracy:.4f}, Samples: {samples}")
    
    @staticmethod
    def log_external_validation(url, is_threat, confidence, sources):
        """Log external validation"""
        logger.info(f"External validation - URL: {url[:50]}..., "
                   f"Threat: {is_threat}, Confidence: {confidence:.2f}, Sources: {sources}")
    
    @staticmethod
    def log_error(context, error, user_id=None):
        """Log application error"""
        user_info = f"User: {user_id}" if user_id else "Anonymous"
        logger.error(f"Error in {context} - {user_info}: {str(error)}")
        logger.debug(traceback.format_exc())
    
    @staticmethod
    def log_warning(message, user_id=None):
        """Log warning"""
        user_info = f"User: {user_id}" if user_id else "Anonymous"
        logger.warning(f"{message} - {user_info}")
    
    @staticmethod
    def log_info(message):
        """Log info message"""
        logger.info(message)
