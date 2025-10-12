import hashlib
import hmac
import time
from flask import request, jsonify

class SecurityMiddleware:
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        app.before_request(self.check_request_signature)
        app.before_request(self.check_request_timestamp)
    
    def check_request_signature(self):
        """Verify request signature to prevent tampering"""
        if request.method in ['POST', 'PUT', 'DELETE']:
            signature = request.headers.get('X-Signature')
            if not signature:
                return jsonify({'error': 'Missing signature'}), 400
    
    def check_request_timestamp(self):
        """Check request timestamp to prevent replay attacks"""
        timestamp = request.headers.get('X-Timestamp')
        if timestamp:
            try:
                req_time = int(timestamp)
                current_time = int(time.time())
                if abs(current_time - req_time) > 300:  # 5 minutes
                    return jsonify({'error': 'Request expired'}), 400
            except ValueError:
                return jsonify({'error': 'Invalid timestamp'}), 400

def generate_csrf_token():
    """Generate CSRF token"""
    return hashlib.sha256(str(time.time()).encode()).hexdigest()

def validate_csrf_token(token, session_token):
    """Validate CSRF token"""
    return hmac.compare_digest(token, session_token)