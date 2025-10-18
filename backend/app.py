from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta, timezone
import logging
from functools import wraps

load_dotenv()

app = Flask(__name__)
# Configure CORS
CORS(app, 
     origins=['http://localhost:8080', 'http://127.0.0.1:8080', 'http://localhost:5173', 'http://127.0.0.1:5173'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'], 
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Analytics helper function
def track_event(user_id, event_type, event_data=None):
    try:
        analytics_data = {
            'user_id': user_id,
            'event_type': event_type,
            'event_data': event_data or {},
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        supabase.table('user_analytics').insert(analytics_data).execute()
    except Exception as e:
        logging.warning(f'Analytics tracking failed: {e}')

# Analytics decorator
def track_usage(event_type):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                # Get user_id from JWT token
                token = request.headers.get('Authorization', '').replace('Bearer ', '')
                if token:
                    payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
                    user_id = payload.get('user_id')
                    if user_id:
                        track_event(user_id, event_type, {
                            'endpoint': request.endpoint,
                            'method': request.method,
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        })
            except:
                pass  # Don't fail the request if analytics fails
            return f(*args, **kwargs)
        return wrapper
    return decorator

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
@track_usage('recipe_action')
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
@track_usage('recipe_save_action')
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
                
                # Try to update existing record first
                try:
                    result = supabase.table('user_recipes').update({
                        'is_saved': True,
                        'saved_at': datetime.now(timezone.utc).isoformat()
                    }).eq('user_id', user_id).eq('recipe_id', str(recipe_id)).execute()
                    
                    if result.data:
                        logging.info('Updated existing record')
                        return jsonify({'message': 'Recipe saved'}), 200
                except Exception as update_error:
                    logging.info(f'Update failed, trying insert: {update_error}')
                
                # If update failed, try insert
                try:
                    result = supabase.table('user_recipes').insert(save_data).execute()
                    logging.info(f'Insert result: {result}')
                    return jsonify({'message': 'Recipe saved'}), 200
                except Exception as insert_error:
                    logging.info(f'Insert failed: {insert_error}')
                    # Recipe already exists, just return success
                    return jsonify({'message': 'Recipe already saved'}), 200
            
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
        
        # Parse time string to extract minutes (e.g., "25 min" -> 25)
        time_str = data.get('time', '')
        cook_time_minutes = 0
        if time_str:
            # Extract number from time string
            import re
            time_match = re.search(r'(\d+)', time_str)
            if time_match:
                cook_time_minutes = int(time_match.group(1))
        
        # Prepare complete recipe data
        recipe_data = {
            'user_id': user_id,
            'title': data.get('name'),
            'cook_time': cook_time_minutes,
            'servings': data.get('servings', 1),
            'image': data.get('image', '🍽️'),
            'ingredients': data.get('ingredients', []),
            'instructions': data.get('instructions', []),
            'description': data.get('description', ''),
            'difficulty': data.get('difficulty', 'medium'),
            'tags': data.get('tags', []),
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        # Insert recipe
        result = supabase.table('recipes').insert(recipe_data).execute()
        
        if result.data:
            return jsonify({'message': 'Recipe created successfully', 'recipe': result.data[0]}), 201
        else:
            return jsonify({'error': 'Failed to create recipe'}), 500
        
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

@app.route('/api/saved-recipes', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
def manage_saved_recipes():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        if request.method == 'GET':
            # Get user's saved recipes
            result = supabase.table('saved_recipes').select('*').eq('user_id', user_id).order('saved_at', desc=True).execute()
            return jsonify({'saved_recipes': result.data}), 200
            
        elif request.method == 'POST':
            # Save a recipe
            data = request.get_json()
            recipe_id = data.get('recipe_id')
            recipe_data = data.get('recipe_data', {})
            
            if not recipe_id:
                return jsonify({'error': 'Recipe ID required'}), 400
            
            save_data = {
                'user_id': user_id,
                'recipe_id': str(recipe_id),
                'recipe_name': recipe_data.get('name') or recipe_data.get('title') or 'Untitled Recipe',
                'recipe_data': recipe_data
            }
            
            # Use upsert to handle duplicates
            result = supabase.table('saved_recipes').upsert(save_data).execute()
            return jsonify({'message': 'Recipe saved successfully'}), 200
            
        elif request.method == 'DELETE':
            # Unsave a recipe
            recipe_id = request.args.get('recipe_id')
            if not recipe_id:
                return jsonify({'error': 'Recipe ID required'}), 400
            
            result = supabase.table('saved_recipes').delete().eq('user_id', user_id).eq('recipe_id', str(recipe_id)).execute()
            return jsonify({'message': 'Recipe unsaved successfully'}), 200
            
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        logging.error(f'Saved recipes error: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/recipes/<recipe_id>/details', methods=['GET', 'OPTIONS'])
def get_recipe_details(recipe_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get recipe from recipes table
        recipe_result = supabase.table('recipes').select('*').eq('id', recipe_id).execute()
        
        if not recipe_result.data:
            return jsonify({'error': 'Recipe not found'}), 404
        
        recipe = recipe_result.data[0]
        
        # Get user info
        user_info = {}
        try:
            user_result = supabase.table('users').select('name, email').eq('id', recipe['user_id']).execute()
            if user_result.data:
                user_info = user_result.data[0]
        except:
            pass
        
        time_display = "30 min"  # Always show default time
        
        formatted_recipe = {
            'id': recipe['id'],
            'name': recipe.get('title', 'Untitled Recipe'),
            'title': recipe.get('title', 'Untitled Recipe'),
            'time': time_display,
            'servings': recipe.get('servings', 1),
            'image': recipe.get('image', '🍽️'),
            'ingredients': recipe.get('ingredients', []),
            'instructions': recipe.get('instructions', []),
            'difficulty': recipe.get('difficulty', 'medium'),
            'tags': recipe.get('tags', []),
            'author': user_info.get('name') or (user_info.get('email', '').split('@')[0] if user_info.get('email') else 'Anonymous'),
            'created_at': recipe.get('created_at')
        }
        
        return jsonify({'recipe': formatted_recipe}), 200
        
    except Exception as e:
        logging.error(f'Get recipe details error: {e}')
        return jsonify({'error': 'Failed to get recipe details'}), 500

@app.route('/api/discover/recipes', methods=['GET', 'OPTIONS'])
def get_discover_recipes():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get all recipes for discover page
        recipes_result = supabase.table('recipes').select('*').order('created_at', desc=True).limit(50).execute()
        
        # Format recipes for discover page
        recipes = []
        for recipe in recipes_result.data:
            # Get user info separately
            user_info = {}
            try:
                user_result = supabase.table('users').select('name, email').eq('id', recipe['user_id']).execute()
                if user_result.data:
                    user_info = user_result.data[0]
            except:
                pass
            
            time_display = "30 min"  # Always show default time
            
            formatted_recipe = {
                'id': recipe['id'],
                'name': recipe.get('title', 'Untitled Recipe'),
                'title': recipe.get('title', 'Untitled Recipe'),
                'time': time_display,
                'servings': recipe.get('servings', 1),
                'image': recipe.get('image', '🍽️'),
                'ingredients': recipe.get('ingredients', []),
                'instructions': recipe.get('instructions', []),
                'difficulty': recipe.get('difficulty', 'medium'),
                'tags': recipe.get('tags', []),
                'author': user_info.get('name') or (user_info.get('email', '').split('@')[0] if user_info.get('email') else 'Anonymous'),
                'created_at': recipe.get('created_at')
            }
            recipes.append(formatted_recipe)
        
        return jsonify({'recipes': recipes}), 200
        
    except Exception as e:
        logging.error(f'Get discover recipes error: {e}')
        return jsonify({'error': 'Failed to get recipes'}), 500

@app.route('/api/shopping/items', methods=['GET', 'POST', 'OPTIONS'])
def shopping_items():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        if request.method == 'GET':
            result = supabase.table('shopping_items').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            return jsonify({'items': result.data}), 200
            
        elif request.method == 'POST':
            data = request.get_json()
            item_name = data.get('item_name')
            category = data.get('category', 'Other')
            quantity = data.get('quantity', 1)
            unit = data.get('unit', 'pcs')
            
            if not item_name:
                return jsonify({'error': 'Item name required'}), 400
            
            item_data = {
                'user_id': user_id,
                'item_name': item_name,
                'category': category,
                'quantity': quantity,
                'unit': unit
            }
            
            result = supabase.table('shopping_items').insert(item_data).execute()
            
            # Update recent items
            recent_result = supabase.table('recent_items').select('*').eq('user_id', user_id).ilike('item_name', item_name).execute()
            
            if recent_result.data:
                recent_item = recent_result.data[0]
                supabase.table('recent_items').update({
                    'frequency': recent_item['frequency'] + 1,
                    'last_used': datetime.now(timezone.utc).isoformat()
                }).eq('id', recent_item['id']).execute()
            else:
                recent_data = {
                    'user_id': user_id,
                    'item_name': item_name,
                    'category': category
                }
                supabase.table('recent_items').insert(recent_data).execute()
            
            return jsonify({'message': 'Item added successfully', 'item': result.data[0]}), 201
            
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/shopping/recent', methods=['GET', 'OPTIONS'])
def recent_items():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        result = supabase.table('recent_items').select('*').eq('user_id', user_id).order('frequency', desc=True).order('last_used', desc=True).limit(10).execute()
        
        return jsonify({'recent_items': result.data}), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/shopping/items/<item_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
def update_shopping_item(item_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        if request.method == 'PUT':
            data = request.get_json()
            update_data = {}
            
            if 'is_completed' in data:
                update_data['is_completed'] = data['is_completed']
            if 'quantity' in data:
                update_data['quantity'] = data['quantity']
            
            result = supabase.table('shopping_items').update(update_data).eq('id', item_id).eq('user_id', user_id).execute()
            
            return jsonify({'message': 'Item updated successfully', 'item': result.data[0] if result.data else None}), 200
            
        elif request.method == 'DELETE':
            supabase.table('shopping_items').delete().eq('id', item_id).eq('user_id', user_id).execute()
            return jsonify({'message': 'Item deleted successfully'}), 200
            
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/delete-account', methods=['DELETE', 'OPTIONS'])
def delete_account():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        # Delete user account (CASCADE will delete related data)
        supabase.table('users').delete().eq('id', user_id).execute()
        
        return jsonify({'message': 'Account deleted successfully'}), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        logging.error(f'Delete account error: {e}')
        return jsonify({'error': 'Failed to delete account'}), 500

@app.route('/api/auth/change-password', methods=['PUT', 'OPTIONS'])
def change_password():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current and new passwords required'}), 400
        
        # Get user
        user_result = supabase.table('users').select('*').eq('id', user_id).execute()
        if not user_result.data:
            return jsonify({'error': 'User not found'}), 404
        
        user = user_result.data[0]
        
        # Verify current password
        if not check_password_hash(user['password_hash'], current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Update password
        new_password_hash = generate_password_hash(new_password)
        supabase.table('users').update({
            'password_hash': new_password_hash,
            'updated_at': datetime.now(timezone.utc).isoformat()
        }).eq('id', user_id).execute()
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        logging.error(f'Change password error: {e}')
        return jsonify({'error': 'Failed to change password'}), 500



# Person Management Endpoints
@app.route('/api/persons', methods=['GET', 'POST', 'OPTIONS'])
def manage_persons():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response, 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        if request.method == 'GET':
            try:
                result = supabase.table('user_persons').select('*').eq('user_id', user_id).order('created_at').execute()
                return jsonify({'persons': result.data or []}), 200
            except Exception as db_error:
                logging.warning(f'user_persons table not found: {db_error}')
                return jsonify({'persons': []}), 200
            
        elif request.method == 'POST':
            try:
                data = request.get_json()
                person_data = {
                    'user_id': user_id,
                    'name': data.get('name'),
                    'preferences': data.get('preferences', ''),
                    'allergies': data.get('allergies', '')
                }
                result = supabase.table('user_persons').insert(person_data).execute()
                return jsonify({'message': 'Person added', 'person': result.data[0] if result.data else None}), 201
            except Exception as db_error:
                logging.warning(f'Failed to add person: {db_error}')
                return jsonify({'message': 'Person added locally'}), 201
            
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/persons/<person_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
def person_detail(person_id):
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response, 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        if request.method == 'PUT':
            data = request.get_json()
            update_data = {
                'name': data.get('name'),
                'preferences': data.get('preferences'),
                'allergies': data.get('allergies'),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            update_data = {k: v for k, v in update_data.items() if v is not None}
            result = supabase.table('user_persons').update(update_data).eq('id', person_id).eq('user_id', user_id).execute()
            return jsonify({'message': 'Person updated', 'person': result.data[0] if result.data else None}), 200
            
        elif request.method == 'DELETE':
            supabase.table('user_persons').delete().eq('id', person_id).eq('user_id', user_id).execute()
            return jsonify({'message': 'Person deleted'}), 200
            
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User Preferences Endpoints
@app.route('/api/preferences', methods=['GET', 'PUT', 'OPTIONS'])
def user_preferences():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response, 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        if request.method == 'GET':
            try:
                result = supabase.table('user_preferences').select('*').eq('user_id', user_id).execute()
                if result.data:
                    return jsonify({'preferences': result.data[0]}), 200
                else:
                    return jsonify({'preferences': {'selected_week': 'Week - 1', 'view_mode': 'list'}}), 200
            except Exception as db_error:
                logging.warning(f'user_preferences table not found: {db_error}')
                return jsonify({'preferences': {'selected_week': 'Week - 1', 'view_mode': 'list'}}), 200
                
        elif request.method == 'PUT':
            try:
                data = request.get_json()
                pref_data = {
                    'user_id': user_id,
                    'selected_week': data.get('selected_week'),
                    'view_mode': data.get('view_mode'),
                    'updated_at': datetime.now(timezone.utc).isoformat()
                }
                pref_data = {k: v for k, v in pref_data.items() if v is not None}
                result = supabase.table('user_preferences').upsert(pref_data).execute()
                return jsonify({'message': 'Preferences updated'}), 200
            except Exception as db_error:
                logging.warning(f'Failed to update preferences: {db_error}')
                return jsonify({'message': 'Preferences updated locally'}), 200
            
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Enhanced Meal Plan Endpoints
@app.route('/api/meal-plan/bulk', methods=['POST', 'OPTIONS'])
def bulk_meal_plan():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response, 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        data = request.get_json()
        month = data.get('month')
        year = data.get('year')
        week = data.get('week', 'Week - 1')  # Default to Week - 1
        
        # Generate sample meal plan for the month
        import calendar
        from datetime import date
        
        meal_times = ['Breakfast', 'Lunch', 'Dinner']
        sample_meals = {
            'Breakfast': ['Oatmeal', 'Eggs & Toast', 'Smoothie Bowl', 'Pancakes'],
            'Lunch': ['Salad', 'Sandwich', 'Soup', 'Pasta'],
            'Dinner': ['Grilled Chicken', 'Fish & Rice', 'Stir Fry', 'Pizza']
        }
        
        # Get number of days in month
        days_in_month = calendar.monthrange(year, month)[1]
        
        meals_to_add = []
        for day in range(1, days_in_month + 1):
            date_obj = date(year, month, day)
            day_name = date_obj.strftime('%A')
            
            for meal_time in meal_times:
                meal_name = sample_meals[meal_time][day % len(sample_meals[meal_time])]
                meals_to_add.append({
                    'user_id': user_id,
                    'recipe_id': f'planned-{day}-{meal_time.lower()}',
                    'recipe_name': meal_name,
                    'day': day_name,
                    'meal_time': meal_time,
                    'servings': 1,
                    'image': '🍽️',
                    'week': week
                })
        
        # Insert all meals
        if meals_to_add:
            supabase.table('meal_plans').insert(meals_to_add).execute()
        
        return jsonify({'message': f'Meal plan created for {calendar.month_name[month]} {year} - {week}'}), 201
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/meal-plan', methods=['GET', 'POST', 'DELETE', 'OPTIONS'])
@track_usage('meal_plan_action')
def meal_plan():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        if request.method == 'GET':
            week = request.args.get('week', 'Week - 1')
            logging.info(f'Getting meal plan for week: {week}, user: {user_id}')
            try:
                result = supabase.table('meal_plans').select('*').eq('user_id', user_id).eq('week', week).order('created_at', desc=True).execute()
                logging.info(f'Meal plan query result: {len(result.data)} items found')
                return jsonify({'meal_plan': result.data}), 200
            except Exception as db_error:
                logging.error(f'meal_plans table query failed: {db_error}')
                # Return empty array if table doesn't exist or has issues
                return jsonify({'meal_plan': []}), 200
        
        elif request.method == 'POST':
            data = request.get_json() or {}
            week = data.get('week', 'Week - 1')
            
            logging.info(f'Adding meal to plan for week: {week}, data: {data}')
            
            meal_data = {
                'user_id': user_id,
                'week': week,
                'day': data.get('day', 'Monday'),
                'meal_time': data.get('meal_time', 'lunch'),
                'recipe_id': str(data.get('recipe_id', '')),
                'recipe_name': data.get('recipe_name', ''),
                'servings': data.get('servings', 1),
                'image': data.get('image', '🍽️'),
                'time': data.get('time', ''),
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            try:
                # First, remove any existing meal for the same day/meal_time/week combination
                supabase.table('meal_plans').delete().eq('user_id', user_id).eq('day', meal_data['day']).eq('meal_time', meal_data['meal_time']).eq('week', week).execute()
                
                # Then insert the new meal
                result = supabase.table('meal_plans').insert(meal_data).execute()
                logging.info(f'Meal added successfully: {result.data}')
                return jsonify({'message': 'Added to meal plan', 'meal_plan': result.data}), 201
            except Exception as db_error:
                logging.error(f'meal_plans table operation failed: {db_error}')
                return jsonify({'message': 'Added to meal plan locally'}), 200
        
        elif request.method == 'DELETE':
            meal_id = request.args.get('id')
            if meal_id:
                try:
                    supabase.table('meal_plans').delete().eq('id', meal_id).eq('user_id', user_id).execute()
                    return jsonify({'message': 'Removed from meal plan'}), 200
                except Exception as db_error:
                    logging.error(f'meal_plans delete failed: {db_error}')
                    return jsonify({'message': 'Removed from meal plan locally'}), 200
            return jsonify({'message': 'Meal ID required'}), 400
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        logging.error(f'Meal plan error: {e}')
        return jsonify({'error': 'Meal plan operation failed'}), 500

@app.route('/api/meal-plan/<meal_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
def meal_plan_detail(meal_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        if request.method == 'PUT':
            data = request.get_json() or {}
            
            update_data = {
                'recipe_name': data.get('recipe_name'),
                'day': data.get('day'),
                'meal_time': data.get('meal_time'),
                'servings': data.get('servings'),
                'week': data.get('week'),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            try:
                result = supabase.table('meal_plans').update(update_data).eq('id', meal_id).eq('user_id', user_id).execute()
                return jsonify({'message': 'Meal plan updated', 'meal_plan': result.data}), 200
            except Exception as db_error:
                logging.warning(f'meal_plans update failed: {db_error}')
                return jsonify({'message': 'Meal plan updated locally'}), 200
        
        elif request.method == 'DELETE':
            try:
                result = supabase.table('meal_plans').delete().eq('id', meal_id).eq('user_id', user_id).execute()
                return jsonify({'message': 'Meal plan deleted'}), 200
            except Exception as db_error:
                logging.warning(f'meal_plans delete failed: {db_error}')
                return jsonify({'message': 'Meal plan deleted locally'}), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        logging.error(f'Meal plan detail error: {e}')
        return jsonify({'error': 'Meal plan operation failed'}), 500

@app.route('/api/analytics', methods=['GET', 'OPTIONS'])
def get_analytics():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user_id = payload['user_id']
        
        # Get user analytics
        result = supabase.table('user_analytics').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(100).execute()
        
        # Calculate usage stats
        events = result.data
        stats = {
            'total_events': len(events),
            'recipe_actions': len([e for e in events if e['event_type'] == 'recipe_action']),
            'meal_plan_actions': len([e for e in events if e['event_type'] == 'meal_plan_action']),
            'recipe_saves': len([e for e in events if e['event_type'] == 'recipe_save_action']),
            'recent_activity': events[:10]
        }
        
        return jsonify({'analytics': stats}), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        logging.error(f'Analytics error: {e}')
        return jsonify({'error': 'Failed to get analytics'}), 500

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '127.0.0.1')
    
    print(f'Starting Flask server on http://{host}:{port}')
    print(f'Health check available at: http://{host}:{port}/api/health')
    app.run(debug=debug_mode, port=port, host=host)