from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)
CORS(app, origins='*', methods=['GET', 'POST', 'PUT', 'OPTIONS'], allow_headers=['Content-Type', 'Authorization'])

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
JWT_SECRET = os.getenv('JWT_SECRET')

if not all([SUPABASE_URL, SUPABASE_KEY, JWT_SECRET]):
    raise ValueError('Missing required environment variables')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'Flask backend is running'}), 200

@app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Check if user exists
        existing_user = supabase.table('users').select('*').eq('email', email).execute()
        if existing_user.data:
            return jsonify({'error': 'User already exists'}), 409
        
        # Hash password and create user
        hashed_password = generate_password_hash(password)
        user_data = {
            'email': email,
            'password_hash': hashed_password,
            'name': email.split('@')[0],
            'created_at': datetime.utcnow().isoformat()
        }
        
        result = supabase.table('users').insert(user_data).execute()
        
        if result.data:
            user = result.data[0]
            token = jwt.encode({
                'user_id': user['id'],
                'email': user['email'],
                'exp': datetime.utcnow() + timedelta(days=7)
            }, JWT_SECRET, algorithm='HS256')
            
            return jsonify({
                'message': 'User created successfully',
                'token': token,
                'user': {'id': user['id'], 'email': user['email'], 'name': user.get('name')}
            }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Find user
        user_result = supabase.table('users').select('*').eq('email', email).execute()
        
        if not user_result.data:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user = user_result.data[0]
        
        # Verify password
        if not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate token
        token = jwt.encode({
            'user_id': user['id'],
            'email': user['email'],
            'exp': datetime.utcnow() + timedelta(days=7)
        }, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {'id': user['id'], 'email': user['email'], 'name': user.get('name')}
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/verify', methods=['GET', 'OPTIONS'])
def verify_token():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        
        # Get full user data
        user_result = supabase.table('users').select('*').eq('id', payload['user_id']).execute()
        if user_result.data:
            user = user_result.data[0]
            return jsonify({
                'user': {
                    'id': user['id'], 
                    'email': user['email'], 
                    'name': user.get('name'),
                    'phone': user.get('phone'),
                    'location': user.get('location'),
                    'bio': user.get('bio')
                }
            }), 200
        
        return jsonify({'user': {'id': payload['user_id'], 'email': payload['email']}}), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

@app.route('/api/profile/update', methods=['PUT', 'OPTIONS'])
def update_profile():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        data = request.get_json()
        
        # Update user profile
        update_data = {
            'name': data.get('name'),
            'phone': data.get('phone'),
            'location': data.get('location'),
            'bio': data.get('bio'),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        result = supabase.table('users').update(update_data).eq('id', user_id).execute()
        
        if result.data:
            user = result.data[0]
            return jsonify({
                'message': 'Profile updated successfully',
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'name': user.get('name'),
                    'phone': user.get('phone'),
                    'location': user.get('location'),
                    'bio': user.get('bio')
                }
            }), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print('Starting Flask server on http://localhost:5000')
    print('Health check available at: http://localhost:5000/api/health')
    app.run(debug=True, port=5000, host='0.0.0.0')