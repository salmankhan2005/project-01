# Performance optimizations for Flask backend
import os
from flask import Flask
from werkzeug.middleware.profiler import ProfilerMiddleware

def optimize_flask_app(app: Flask):
    """Apply performance optimizations to Flask app"""
    
    # Enable response compression
    app.config['COMPRESS_MIMETYPES'] = [
        'text/html', 'text/css', 'text/xml', 'application/json',
        'application/javascript', 'text/javascript'
    ]
    
    # Cache control headers
    @app.after_request
    def after_request(response):
        # Cache static assets for 1 year
        if request.endpoint and 'static' in request.endpoint:
            response.cache_control.max_age = 31536000
        # Cache API responses for 5 minutes
        elif request.endpoint and 'api' in request.endpoint:
            response.cache_control.max_age = 300
        
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response
    
    # Enable profiling in development
    if os.getenv('FLASK_ENV') == 'development':
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
    
    return app