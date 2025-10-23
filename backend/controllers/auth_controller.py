from flask import request, jsonify
from models.user import User
from utils.auth import generate_token

def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        if User.find_by_email(email):
            return jsonify({'error': 'User already exists'}), 409
        
        user = User.create(email, password)
        if not user:
            return jsonify({'error': 'Registration failed'}), 500
        
        token = generate_token({
            'user_id': user['id'],
            'email': user['email']
        })
        
        return jsonify({
            'message': 'User created successfully',
            'token': token,
            'user': {'id': user['id'], 'email': user['email'], 'name': user.get('name')}
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Registration failed'}), 500

def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.find_by_email(email)
        if not user or not User.verify_password(user, password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        User.update_last_login(user['id'])
        
        token = generate_token({
            'user_id': user['id'],
            'email': user['email']
        })
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {'id': user['id'], 'email': user['email'], 'name': user.get('name')}
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500

def verify_token():
    try:
        user_id = request.user['user_id']
        user = User.find_by_id(user_id)
        
        if user:
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
        
        return jsonify({'user': {'id': user_id, 'email': request.user['email']}}), 200
        
    except Exception as e:
        return jsonify({'error': 'Token verification failed'}), 401