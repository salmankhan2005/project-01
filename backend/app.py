from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt
import jwt
import datetime
import os
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import re
from bson import ObjectId
from functools import wraps

load_dotenv()

app = Flask(__name__)

# Security configurations
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(32))
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# CORS with security
CORS(app, 
     origins=os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(','),
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE'])

# Rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

@app.before_request
def security_headers():
    # Block requests with suspicious patterns
    user_agent = request.headers.get('User-Agent', '')
    if not user_agent or len(user_agent) < 10:
        return jsonify({'error': 'Invalid request'}), 400
    
    # Block common bot patterns
    bot_patterns = ['bot', 'crawler', 'spider', 'scraper', 'wget', 'curl']
    if any(pattern in user_agent.lower() for pattern in bot_patterns):
        return jsonify({'error': 'Access denied'}), 403

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI'))
db = client.mealpal
users_collection = db.users

JWT_SECRET = os.getenv('JWT_SECRET')

def generate_token(user_id):
    payload = {
        'user_id': str(user_id),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    return len(password) >= 8 and any(c.isdigit() for c in password) and any(c.isalpha() for c in password)

def sanitize_input(data):
    if isinstance(data, str):
        return data.strip()[:500]  # Limit length
    return data

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        user_id = verify_token(token[7:])
        if not user_id:
            return jsonify({'error': 'Invalid token'}), 401
        
        request.user_id = user_id
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    email = sanitize_input(data['email']).lower()
    password = sanitize_input(data['password'])
    name = sanitize_input(data.get('name', ''))
    
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if not validate_password(password):
        return jsonify({'error': 'Password must be at least 8 characters with letters and numbers'}), 400
    
    # Check if user exists
    if users_collection.find_one({'email': email}):
        return jsonify({'error': 'User already exists'}), 400
    
    # Hash password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Create user with profile
    user_data = {
        'email': email,
        'password': hashed_password,
        'profile': {
            'name': name,
            'phone': '',
            'bio': '',
            'dietary_preferences': []
        },
        'created_at': datetime.datetime.utcnow()
    }
    
    result = users_collection.insert_one(user_data)
    token = generate_token(result.inserted_id)
    
    return jsonify({
        'message': 'User created successfully',
        'token': token,
        'user': {
            'id': str(result.inserted_id),
            'email': email,
            'name': name,
            'profile': user_data['profile']
        }
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400
    
    email = data['email'].lower()
    password = data['password']
    
    # Find user
    user = users_collection.find_one({'email': email})
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check password
    if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = generate_token(user['_id'])
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': str(user['_id']),
            'email': user['email'],
            'name': user.get('name', '')
        }
    }), 200

@app.route('/api/auth/verify', methods=['GET'])
def verify():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'No token provided'}), 401
    
    if token.startswith('Bearer '):
        token = token[7:]
    
    user_id = verify_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    
    from bson import ObjectId
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'user': {
            'id': str(user['_id']),
            'email': user['email'],
            'name': user.get('name', ''),
            'profile': user.get('profile', {})
        }
    }), 200

@app.route('/api/profile', methods=['GET'])
def get_profile():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    user_id = verify_token(token[7:])
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    
    from bson import ObjectId
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.get('profile', {})), 200

@app.route('/api/profile', methods=['PUT'])
def update_profile():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    user_id = verify_token(token[7:])
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    from bson import ObjectId
    users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'profile': data}}
    )
    
    return jsonify({'message': 'Profile updated successfully'}), 200

@app.route('/api/auth/change-password', methods=['PUT'])
def change_password():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    user_id = verify_token(token[7:])
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    
    data = request.get_json()
    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Current and new password required'}), 400
    
    from bson import ObjectId
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Verify current password
    if not bcrypt.checkpw(data['current_password'].encode('utf-8'), user['password']):
        return jsonify({'error': 'Current password is incorrect'}), 400
    
    # Hash new password
    new_hashed_password = bcrypt.hashpw(data['new_password'].encode('utf-8'), bcrypt.gensalt())
    
    # Update password
    users_collection.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': {'password': new_hashed_password}}
    )
    
    return jsonify({'message': 'Password changed successfully'}), 200

# Client management endpoints
clients_collection = db.clients

@app.route('/api/clients', methods=['GET'])
def get_clients():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    user_id = verify_token(token[7:])
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    
    clients = list(clients_collection.find({'nutritionist_id': user_id}))
    for client in clients:
        client['_id'] = str(client['_id'])
    
    return jsonify(clients), 200

@app.route('/api/clients', methods=['POST'])
def add_client():
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    user_id = verify_token(token[7:])
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    
    data = request.get_json()
    if not data or not data.get('name') or not data.get('email'):
        return jsonify({'error': 'Name and email required'}), 400
    
    client_data = {
        'nutritionist_id': user_id,
        'name': data['name'],
        'email': data['email'],
        'plan': data.get('plan', ''),
        'status': 'Active',
        'created_at': datetime.datetime.utcnow(),
        'last_updated': datetime.datetime.utcnow()
    }
    
    result = clients_collection.insert_one(client_data)
    client_data['_id'] = str(result.inserted_id)
    
    return jsonify(client_data), 201

@app.route('/api/clients/<client_id>', methods=['DELETE'])
def delete_client(client_id):
    token = request.headers.get('Authorization')
    if not token or not token.startswith('Bearer '):
        return jsonify({'error': 'No token provided'}), 401
    
    user_id = verify_token(token[7:])
    if not user_id:
        return jsonify({'error': 'Invalid token'}), 401
    
    from bson import ObjectId
    result = clients_collection.delete_one({
        '_id': ObjectId(client_id),
        'nutritionist_id': user_id
    })
    
    if result.deleted_count == 0:
        return jsonify({'error': 'Client not found'}), 404
    
    return jsonify({'message': 'Client deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)