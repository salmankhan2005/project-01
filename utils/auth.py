import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify
from config.settings import JWT_SECRET, ADMIN_JWT_SECRET

def verify_token(token, secret=JWT_SECRET):
    try:
        payload = jwt.decode(token, secret, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def generate_token(payload, secret=JWT_SECRET, expires_in_days=7):
    payload['exp'] = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
    return jwt.encode(payload, secret, algorithm='HS256')

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user = payload
        return f(*args, **kwargs)
    return decorated_function

def require_admin_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = verify_token(token, ADMIN_JWT_SECRET)
        if not payload:
            return jsonify({'error': 'Invalid or expired admin token'}), 401
        
        request.admin = payload
        return f(*args, **kwargs)
    return decorated_function