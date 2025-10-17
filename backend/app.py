from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta, timezone
import logging

load_dotenv()

app = Flask(__name__)
# Restrict CORS to specific origins in production
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:8080').split(',')
CORS(app, origins=allowed_origins, methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'], allow_headers=['Content-Type', 'Authorization'])

# Configure logging
logging.basicConfig(level=logging.INFO)

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
JWT_SECRET = os.getenv('JWT_SECRET')

if not all([SUPABASE_URL, SUPABASE_KEY, JWT_SECRET]):
    logging.error('Missing required environment variables')
    raise ValueError('Missing required environment variables')

try:
    # Create Supabase client without any additional options
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    logging.error(f'Failed to create Supabase client: {e}')
    raise

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
        
        # Validate input
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
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
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        result = supabase.table('users').insert(user_data).execute()
        
        if result.data:
            user = result.data[0]
            token = jwt.encode({
                'user_id': user['id'],
                'email': user['email'],
                'exp': datetime.now(timezone.utc) + timedelta(days=7)
            }, JWT_SECRET, algorithm='HS256')
            
            return jsonify({
                'message': 'User created successfully',
                'token': token,
                'user': {'id': user['id'], 'email': user['email'], 'name': user.get('name')}
            }), 201
        
    except Exception as e:
        logging.error(f'Registration error: {e}')
        return jsonify({'error': 'Registration failed'}), 500

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
            'exp': datetime.now(timezone.utc) + timedelta(days=7)
        }, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {'id': user['id'], 'email': user['email'], 'name': user.get('name')}
        }), 200
        
    except Exception as e:
        logging.error(f'Login error: {e}')
        return jsonify({'error': 'Login failed'}), 500

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
            'updated_at': datetime.now(timezone.utc).isoformat()
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
        logging.error(f'Profile update error: {e}')
        return jsonify({'error': 'Profile update failed'}), 500

@app.route('/api/recipes', methods=['GET', 'POST', 'OPTIONS'])
def recipes():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        if request.method == 'GET':
            # Get user's recipes
            result = supabase.table('recipes').select('*').eq('user_id', user_id).execute()
            return jsonify({'recipes': result.data}), 200
        
        elif request.method == 'POST':
            # Create new recipe
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Handle both 'title' and 'name' fields for compatibility
            title = data.get('title') or data.get('name')
            if not title:
                return jsonify({'error': 'Recipe name is required'}), 400
            
            recipe_data = {
                'user_id': user_id,
                'title': title,
                'description': data.get('description', ''),
                'ingredients': data.get('ingredients', []),
                'instructions': data.get('instructions', []),
                'prep_time': data.get('prep_time'),
                'cook_time': data.get('cook_time'),
                'servings': data.get('servings'),
                'difficulty': data.get('difficulty', 'medium'),
                'tags': data.get('tags', []),
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            try:
                result = supabase.table('recipes').insert(recipe_data).execute()
                
                if result.data:
                    return jsonify({
                        'message': 'Recipe created successfully',
                        'recipe': result.data[0]
                    }), 201
                else:
                    return jsonify({'error': 'Failed to create recipe'}), 500
            except Exception as db_error:
                logging.error(f'Database error creating recipe: {db_error}')
                return jsonify({'error': 'Database error occurred'}), 500
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        logging.error(f'Recipe operation error: {str(e)}')
        logging.error(f'Request data: {request.get_json() if request.method == "POST" else "N/A"}')
        return jsonify({'error': f'Recipe operation failed: {str(e)}'}), 500

@app.route('/api/recipes/<recipe_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
def recipe_detail(recipe_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        if request.method == 'PUT':
            # Update recipe
            data = request.get_json()
            
            update_data = {
                'title': data.get('title'),
                'description': data.get('description'),
                'ingredients': data.get('ingredients'),
                'instructions': data.get('instructions'),
                'prep_time': data.get('prep_time'),
                'cook_time': data.get('cook_time'),
                'servings': data.get('servings'),
                'difficulty': data.get('difficulty'),
                'tags': data.get('tags'),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            result = supabase.table('recipes').update(update_data).eq('id', recipe_id).eq('user_id', user_id).execute()
            
            if result.data:
                return jsonify({
                    'message': 'Recipe updated successfully',
                    'recipe': result.data[0]
                }), 200
        
        elif request.method == 'DELETE':
            # Delete recipe
            result = supabase.table('recipes').delete().eq('id', recipe_id).eq('user_id', user_id).execute()
            
            return jsonify({'message': 'Recipe deleted successfully'}), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        logging.error(f'Recipe detail operation error: {e}')
        return jsonify({'error': 'Recipe operation failed'}), 500

@app.route('/api/recipes/<recipe_id>/access', methods=['POST', 'OPTIONS'])
def track_recipe_access(recipe_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        # Track recipe access
        access_data = {
            'user_id': user_id,
            'recipe_id': recipe_id,
            'accessed_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Use upsert to update accessed_at if record exists
        result = supabase.table('user_recipes').upsert(access_data).execute()
        
        return jsonify({'message': 'Recipe access tracked'}), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        logging.error(f'Recipe access tracking error: {e}')
        return jsonify({'error': 'Failed to track recipe access'}), 500

@app.route('/api/user-recipes', methods=['GET', 'OPTIONS'])
def get_user_saved_recipes():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        try:
            # Get user's saved recipes with recipe details
            result = supabase.table('user_recipes').select('*, recipes(*)').eq('user_id', user_id).eq('is_saved', True).execute()
            return jsonify({'saved_recipes': result.data}), 200
        except Exception as db_error:
            logging.warning(f'user_recipes table not found: {db_error}')
            # Return empty array if table doesn't exist
            return jsonify({'saved_recipes': []}), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        logging.error(f'Get saved recipes error: {e}')
        return jsonify({'saved_recipes': []}), 200

@app.route('/api/recipes/<recipe_id>/save', methods=['POST', 'DELETE', 'OPTIONS'])
def save_recipe(recipe_id):
    logging.info(f'Save recipe endpoint called: {request.method} /api/recipes/{recipe_id}/save')
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        try:
            if request.method == 'POST':
                # Get recipe data from request body if provided
                data = request.get_json() or {}
                logging.info(f'Request data: {data}')
                
                # Save recipe
                recipe_data = data.get('recipe_data', {})
                logging.info(f'Recipe data: {recipe_data}')
                
                save_data = {
                    'user_id': user_id,
                    'recipe_id': str(recipe_id),
                    'recipe_data': recipe_data,
                    'is_saved': True,
                    'saved_at': datetime.now(timezone.utc).isoformat()
                }
                
                # Add recipe_name if column exists
                recipe_name = recipe_data.get('name') or recipe_data.get('title')
                if recipe_name:
                    save_data['recipe_name'] = recipe_name
                
                logging.info(f'Saving data: {save_data}')
                result = supabase.table('user_recipes').upsert(save_data).execute()
                logging.info(f'Save result: {result}')
                return jsonify({'message': 'Recipe saved'}), 200
            
            elif request.method == 'DELETE':
                # Unsave recipe
                result = supabase.table('user_recipes').delete().eq('user_id', user_id).eq('recipe_id', recipe_id).execute()
                return jsonify({'message': 'Recipe unsaved'}), 200
                
        except Exception as db_error:
            logging.error(f'user_recipes table operation failed: {db_error}')
            logging.error(f'Error type: {type(db_error)}')
            # Return success even if table doesn't exist (fallback to localStorage)
            return jsonify({'message': 'Recipe saved locally'}), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        logging.error(f'Save recipe error: {e}')
        return jsonify({'message': 'Recipe saved locally'}), 200

# Recipe endpoints
@app.route('/api/recipes', methods=['GET', 'OPTIONS'])
def get_recipes():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        # Get user's recipes
        result = supabase.table('recipes').select('*').eq('user_id', user_id).execute()
        
        return jsonify({'recipes': result.data}), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        logging.error(f'Get recipes error: {e}')
        return jsonify({'error': 'Failed to get recipes'}), 500

@app.route('/api/recipes', methods=['POST'])
def create_recipe():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Recipe name is required'}), 400
        
        # Prepare recipe data
        recipe_data = {
            'user_id': user_id,
            'name': data.get('name'),
            'time': data.get('time'),
            'servings': data.get('servings'),
            'image': data.get('image'),
            'ingredients': data.get('ingredients'),
            'instructions': data.get('instructions'),
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Insert recipe
        result = supabase.table('recipes').insert(recipe_data).execute()
        
        if result.data:
            return jsonify({'message': 'Recipe created successfully', 'recipe': result.data[0]}), 201
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        logging.error(f'Create recipe error: {e}')
        return jsonify({'error': 'Failed to create recipe'}), 500

@app.route('/api/recipes/<recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        # Check if recipe exists and belongs to user
        check_result = supabase.table('recipes').select('*').eq('id', recipe_id).eq('user_id', user_id).execute()
        
        if not check_result.data:
            return jsonify({'error': 'Recipe not found or unauthorized'}), 404
        
        # Delete recipe
        result = supabase.table('recipes').delete().eq('id', recipe_id).eq('user_id', user_id).execute()
        
        return jsonify({'message': 'Recipe deleted successfully'}), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        logging.error(f'Delete recipe error: {e}')
        return jsonify({'error': 'Failed to delete recipe'}), 500

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '127.0.0.1')
    
    print(f'Starting Flask server on http://{host}:{port}')
    print(f'Health check available at: http://{host}:{port}/api/health')
    app.run(debug=debug_mode, port=port, host=host)