"""
TrustLink CDN Configuration
Enables CDN support for static assets to improve global performance
"""
import os
from flask import url_for as flask_url_for


class CDNConfig:
    """CDN configuration and helpers"""
    
    def __init__(self):
        self.enabled = os.environ.get('USE_CDN', 'false').lower() == 'true'
        self.cdn_url = os.environ.get('CDN_URL', '')
        
        if self.enabled and not self.cdn_url:
            print("[CDN] Warning: CDN enabled but CDN_URL not set. Falling back to local assets.")
            self.enabled = False
        
        if self.enabled:
            print(f"[CDN] Enabled with URL: {self.cdn_url}")
    
    def url_for(self, endpoint, **values):
        """
        Enhanced url_for that supports CDN for static files
        
        Usage:
            cdn.url_for('static', filename='css/style.css')
        """
        if endpoint == 'static' and self.enabled:
            # Use CDN for static files
            filename = values.get('filename', '')
            return f"{self.cdn_url}/{filename}"
        
        # Fall back to Flask's url_for
        return flask_url_for(endpoint, **values)
    
    def get_asset_url(self, path):
        """
        Get full URL for an asset
        
        Args:
            path: Path relative to static folder (e.g., 'css/style.css')
        
        Returns:
            Full URL to asset (CDN or local)
        """
        if self.enabled:
            return f"{self.cdn_url}/{path}"
        return flask_url_for('static', filename=path)


# Global CDN instance
cdn = CDNConfig()


def init_cdn_support(app):
    """
    Initialize CDN support for Flask app
    
    Usage:
        from cdn_config import init_cdn_support
        init_cdn_support(app)
    """
    
    # Make CDN available in templates
    @app.context_processor
    def inject_cdn():
        return {
            'cdn': cdn,
            'cdn_url_for': cdn.url_for,
            'asset_url': cdn.get_asset_url
        }
    
    print("[CDN] Template integration enabled")


def generate_cdn_headers():
    """
    Generate recommended headers for CDN caching
    
    Returns:
        dict: Headers to set on static file responses
    """
    return {
        'Cache-Control': 'public, max-age=31536000, immutable',  # 1 year
        'X-Content-Type-Options': 'nosniff',
        'Access-Control-Allow-Origin': '*',  # Allow cross-origin requests for CDN
    }


def get_cache_busting_url(filename, version=None):
    """
    Generate cache-busting URL for static files
    
    Args:
        filename: Static file path
        version: Optional version string (defaults to file mtime or app version)
    
    Returns:
        URL with version parameter for cache busting
    """
    if version is None:
        # Use file modification time as version
        try:
            import os.path
            static_path = os.path.join('static', filename)
            if os.path.exists(static_path):
                version = str(int(os.path.getmtime(static_path)))
            else:
                version = '1'
        except:
            version = '1'
    
    base_url = cdn.get_asset_url(filename)
    return f"{base_url}?v={version}"
