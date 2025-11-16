from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta, timezone
import logging
import hashlib
import secrets
import sys
sys.path.append('.')
try:
    from admin_recipe_sync import sync_recipe_to_discover, notify_meal_plan_apps
except ImportError:
    def sync_recipe_to_discover(*args, **kwargs): pass
    def notify_meal_plan_apps(*args, **kwargs): pass

try:
    from meal_plan_sync import sync_meal_plan_to_users
except ImportError:
    def sync_meal_plan_to_users(*args, **kwargs): pass

load_dotenv()

app = Flask(__name__)
CORS(app, origins='*', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'], allow_headers=['Content-Type', 'Authorization'])

# Configure logging
logging.basicConfig(level=logging.INFO)

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
JWT_SECRET = os.getenv('ADMIN_JWT_SECRET', 'admin-jwt-secret-key')

if not all([SUPABASE_URL, SUPABASE_KEY]):
    logging.error('Missing required environment variables')
    raise ValueError('Missing required environment variables')

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    logging.error(f'Failed to create Supabase client: {e}')
    raise

def get_admin_permissions(role):
    """Get permissions for admin role"""
    try:
        result = supabase.table('admin_role_permissions').select('admin_permissions(name)').eq('role', role).execute()
        return [item['admin_permissions']['name'] for item in result.data]
    except:
        return []

def verify_admin_token(token):
    """Verify admin JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.route('/api/admin/health', methods=['GET'])
def admin_health_check():
    return jsonify({'status': 'ok', 'message': 'Admin backend is running'}), 200

@app.route('/api/admin/auth/login', methods=['POST', 'OPTIONS'])
def admin_login():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Find admin user
        admin_result = supabase.table('admin_users').select('*').eq('email', email).eq('is_active', True).execute()
        
        if not admin_result.data:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        admin = admin_result.data[0]
        
        # Verify password
        if not check_password_hash(admin['password_hash'], password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Get permissions
        permissions = get_admin_permissions(admin['role'])
        
        # Generate token
        token = jwt.encode({
            'admin_id': admin['id'],
            'email': admin['email'],
            'role': admin['role'],
            'permissions': permissions,
            'exp': datetime.now(timezone.utc) + timedelta(hours=8)
        }, JWT_SECRET, algorithm='HS256')
        
        # Create session
        session_token = secrets.token_urlsafe(32)
        session_data = {
            'admin_id': admin['id'],
            'token_hash': hashlib.sha256(session_token.encode()).hexdigest(),
            'expires_at': (datetime.now(timezone.utc) + timedelta(hours=8)).isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')
        }
        supabase.table('admin_sessions').insert(session_data).execute()
        
        # Update last login
        supabase.table('admin_users').update({
            'last_login': datetime.now(timezone.utc).isoformat()
        }).eq('id', admin['id']).execute()
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'admin': {
                'id': admin['id'],
                'email': admin['email'],
                'name': admin['name'],
                'role': admin['role'],
                'permissions': permissions
            }
        }), 200
        
    except Exception as e:
        logging.error(f'Admin login error: {e}')
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/admin/auth/verify', methods=['GET', 'OPTIONS'])
def verify_admin_token_endpoint():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        payload = verify_admin_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401
        
        # Get full admin data
        admin_result = supabase.table('admin_users').select('*').eq('id', payload['admin_id']).eq('is_active', True).execute()
        if admin_result.data:
            admin = admin_result.data[0]
            permissions = get_admin_permissions(admin['role'])
            return jsonify({
                'admin': {
                    'id': admin['id'],
                    'email': admin['email'],
                    'name': admin['name'],
                    'role': admin['role'],
                    'permissions': permissions
                }
            }), 200
        
        return jsonify({'error': 'Admin not found'}), 404
        
    except Exception as e:
        logging.error(f'Token verification error: {e}')
        return jsonify({'error': 'Token verification failed'}), 401

@app.route('/api/admin/auth/logout', methods=['POST', 'OPTIONS'])
def admin_logout():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if token:
            payload = verify_admin_token(token)
            if payload:
                # Delete session
                supabase.table('admin_sessions').delete().eq('admin_id', payload['admin_id']).execute()
        
        return jsonify({'message': 'Logged out successfully'}), 200
        
    except Exception as e:
        logging.error(f'Logout error: {e}')
        return jsonify({'error': 'Logout failed'}), 500

# Recipe Management Endpoints
@app.route('/api/admin/recipes', methods=['GET', 'POST', 'OPTIONS'])
def admin_recipes():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        payload = verify_admin_token(token)
        
        if not payload:
            return jsonify({'error': 'Unauthorized'}), 401
        
        if request.method == 'GET':
            # Get all admin recipes
            result = supabase.table('admin_recipes').select('*').order('created_at', desc=True).execute()
            return jsonify({'recipes': result.data}), 200
            
        elif request.method == 'POST':
            # Create new recipe
            data = request.get_json()
            
            if not data.get('title'):
                return jsonify({'error': 'Recipe title is required'}), 400
            
            recipe_data = {
                'title': data.get('title'),
                'description': data.get('description', ''),
                'ingredients': data.get('ingredients', []),
                'instructions': data.get('instructions', []),
                'cook_time': data.get('cook_time', 30),
                'servings': data.get('servings', 1),
                'difficulty': data.get('difficulty', 'medium'),
                'category': data.get('category', 'Main'),
                'image': data.get('image', '🍽️'),
                'author': data.get('author', 'Admin'),
                'status': data.get('status', 'published'),

                'created_by': payload['admin_id'],
                'created_at': datetime.now(timezone.utc).isoformat(),
                'is_admin_recipe': True
            }
            
            # Insert recipe
            result = supabase.table('admin_recipes').insert(recipe_data).execute()
            
            if result.data:
                recipe = result.data[0]
                try:
                    # Sync to discover page
                    sync_recipe_to_discover(recipe, 'create')
                    # Notify meal plan apps
                    notify_meal_plan_apps(recipe, 'create')
                    logging.info(f'Recipe {recipe["title"]} synced successfully')
                except Exception as sync_error:
                    logging.error(f'Sync failed: {sync_error}')
                
                return jsonify({
                    'message': 'Recipe created and synced successfully',
                    'recipe': recipe
                }), 201
        
    except Exception as e:
        logging.error(f'Admin recipes error: {e}')
        return jsonify({'error': 'Recipe operation failed'}), 500

@app.route('/api/admin/recipes/<recipe_id>', methods=['PUT', 'DELETE', 'OPTIONS'])
def admin_recipe_detail(recipe_id):
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        payload = verify_admin_token(token)
        
        if not payload:
            return jsonify({'error': 'Unauthorized'}), 401
        
        if request.method == 'PUT':
            # Update recipe
            data = request.get_json()
            
            update_data = {
                'title': data.get('title'),
                'description': data.get('description'),
                'ingredients': data.get('ingredients'),
                'instructions': data.get('instructions'),
                'cook_time': data.get('cook_time'),
                'servings': data.get('servings'),
                'difficulty': data.get('difficulty'),
                'category': data.get('category'),
                'image': data.get('image'),
                'author': data.get('author'),
                'status': data.get('status'),

                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            result = supabase.table('admin_recipes').update(update_data).eq('id', recipe_id).execute()
            
            if result.data:
                recipe = result.data[0]
                try:
                    # Sync to discover page
                    sync_recipe_to_discover(recipe, 'update')
                    # Notify meal plan apps
                    notify_meal_plan_apps(recipe, 'update')
                    logging.info(f'Recipe {recipe["title"]} updated and synced')
                except Exception as sync_error:
                    logging.error(f'Update sync failed: {sync_error}')
                
                return jsonify({
                    'message': 'Recipe updated and synced successfully',
                    'recipe': recipe
                }), 200
        
        elif request.method == 'DELETE':
            # Get recipe before deletion for sync
            recipe_result = supabase.table('admin_recipes').select('*').eq('id', recipe_id).execute()
            
            if recipe_result.data:
                recipe = recipe_result.data[0]
                
                # Delete recipe
                supabase.table('admin_recipes').delete().eq('id', recipe_id).execute()
                
                # Sync deletion to discover page
                sync_recipe_to_discover(recipe, 'delete')
                # Notify meal plan apps
                notify_meal_plan_apps(recipe, 'delete')
                
                return jsonify({'message': 'Recipe deleted and synced successfully'}), 200
            else:
                return jsonify({'error': 'Recipe not found'}), 404
        
    except Exception as e:
        logging.error(f'Admin recipe detail error: {e}')
        return jsonify({'error': 'Recipe operation failed'}), 500

@app.route('/api/admin/users', methods=['GET', 'OPTIONS'])
def get_admin_users():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        payload = verify_admin_token(token)
        
        if not payload:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Check permissions
        if 'admin_management' not in payload.get('permissions', []):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        # Get admin users
        result = supabase.table('admin_users').select('id, email, name, role, is_active, created_at, last_login').execute()
        
        return jsonify({'admins': result.data}), 200
        
    except Exception as e:
        logging.error(f'Get admin users error: {e}')
        return jsonify({'error': 'Failed to get admin users'}), 500

@app.route('/api/admin/users', methods=['POST'])
def create_admin_user():
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        payload = verify_admin_token(token)
        
        if not payload:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Check permissions
        if 'admin_management' not in payload.get('permissions', []):
            return jsonify({'error': 'Insufficient permissions'}), 403
        
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        role = data.get('role')
        
        if not all([email, password, name, role]):
            return jsonify({'error': 'All fields required'}), 400
        
        if role not in ['super_admin', 'sub_admin', 'marketing_admin']:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Check if admin exists
        existing = supabase.table('admin_users').select('*').eq('email', email).execute()
        if existing.data:
            return jsonify({'error': 'Admin already exists'}), 409
        
        # Create admin
        admin_data = {
            'email': email,
            'password_hash': generate_password_hash(password),
            'name': name,
            'role': role,
            'created_by': payload['admin_id']
        }
        
        result = supabase.table('admin_users').insert(admin_data).execute()
        
        if result.data:
            admin = result.data[0]
            return jsonify({
                'message': 'Admin created successfully',
                'admin': {
                    'id': admin['id'],
                    'email': admin['email'],
                    'name': admin['name'],
                    'role': admin['role']
                }
            }), 201
        
    except Exception as e:
        logging.error(f'Create admin error: {e}')
        return jsonify({'error': 'Failed to create admin'}), 500

# Recipe sync endpoints for meal plan apps
@app.route('/api/admin/recipes/sync', methods=['GET', 'OPTIONS'])
def get_recipe_notifications():
    """Get recipe change notifications for meal plan apps"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get recent notifications
        result = supabase.table('recipe_notifications').select('*').order('timestamp', desc=True).limit(50).execute()
        return jsonify({'notifications': result.data}), 200
        
    except Exception as e:
        logging.error(f'Get notifications error: {e}')
        return jsonify({'error': 'Failed to get notifications'}), 500

@app.route('/api/admin/recipes/discover', methods=['GET', 'OPTIONS'])
def get_discover_recipes():
    """Get all admin recipes for discover page"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # Get admin recipes
        result = supabase.table('admin_recipes').select('*').order('created_at', desc=True).execute()
        
        # Format for discover page
        recipes = []
        for recipe in result.data:
            formatted_recipe = {
                'id': recipe['id'],
                'name': recipe['title'],
                'title': recipe['title'],
                'time': f"{recipe.get('cook_time', 30)} min",
                'servings': recipe.get('servings', 1),
                'image': recipe.get('image', '🍽️'),
                'ingredients': recipe.get('ingredients', []),
                'instructions': recipe.get('instructions', []),
                'difficulty': recipe.get('difficulty', 'medium'),
                'category': recipe.get('category', 'Main'),
                'author': recipe.get('author', 'Admin'),
                'created_at': recipe.get('created_at')
            }
            recipes.append(formatted_recipe)
        
        return jsonify({'recipes': recipes}), 200
        
    except Exception as e:
        logging.error(f'Get discover recipes error: {e}')
        return jsonify({'error': 'Failed to get discover recipes'}), 500

# Admin Meal Plan Management Endpoints
@app.route('/api/admin/meal-plans', methods=['GET', 'POST', 'OPTIONS'])
def admin_meal_plans():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        payload = verify_admin_token(token)
        
        if not payload:
            return jsonify({'error': 'Unauthorized'}), 401
        
        if request.method == 'GET':
            # Get all admin meal plans
            result = supabase.table('admin_meal_plans').select('*').order('created_at', desc=True).execute()
            return jsonify({'meal_plans': result.data}), 200
            
        elif request.method == 'POST':
            # Create new meal plan
            data = request.get_json()
            
            if not data.get('name'):
                return jsonify({'error': 'Meal plan name is required'}), 400
            
            meal_plan_data = {
                'name': data.get('name'),
                'description': data.get('description', ''),
                'week_start': data.get('week_start'),
                'meals': data.get('meals', {}),
                'created_by': payload['admin_id'],
                'status': data.get('status', 'active'),
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Insert meal plan
            result = supabase.table('admin_meal_plans').insert(meal_plan_data).execute()
            
            if result.data:
                meal_plan = result.data[0]
                try:
                    # Sync to user apps
                    sync_meal_plan_to_users(meal_plan, 'create')
                    logging.info(f'Meal plan {meal_plan["name"]} synced to user apps')
                except Exception as sync_error:
                    logging.error(f'Meal plan sync failed: {sync_error}')
                
                return jsonify({
                    'message': 'Meal plan created and synced successfully',
                    'meal_plan': meal_plan
                }), 201
        
    except Exception as e:
        logging.error(f'Admin meal plans error: {e}')
        return jsonify({'error': 'Meal plan operation failed'}), 500

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('ADMIN_PORT', 5001))  # Use different port for admin
    host = os.getenv('HOST', '127.0.0.1')
    
    print(f'Starting Admin Flask server on http://{host}:{port}')
    print(f'Health check available at: http://{host}:{port}/api/admin/health')
    print(f'Recipe management available at: http://{host}:{port}/api/admin/recipes')
    app.run(debug=debug_mode, port=port, host=host)