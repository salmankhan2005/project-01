from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client
import os
from dotenv import load_dotenv
import jwt
import logging

load_dotenv()

app = Flask(__name__)
CORS(app, origins='*', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'], allow_headers=['Content-Type', 'Authorization'])

logging.basicConfig(level=logging.INFO)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
JWT_SECRET = os.getenv('JWT_SECRET')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/meal-plans/admin-templates', methods=['GET', 'OPTIONS'])
def get_admin_meal_plan_templates():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        logging.info('Verifying token...')
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        logging.info(f'Token verified for user: {payload.get("user_id")}')
        
        logging.info('Getting template meals...')
        result = supabase.table('meal_plans').select('*').execute()
        template_meals = [meal for meal in result.data if meal.get('user_id') is None and meal.get('week', '').startswith('template_')]
        logging.info(f'Found {len(template_meals)} template meals')
        
        # Group meals by template
        templates_data = {}
        for meal in template_meals:
            week = meal.get('week', '')
            if week.startswith('template_'):
                template_id = week.replace('template_', '')
                if template_id not in templates_data:
                    templates_data[template_id] = {
                        'meals': {},
                        'name': template_id.replace('_', ' ').title() + ' Plan'
                    }
                
                day = meal.get('day')
                meal_time = meal.get('meal_time')
                
                if day and meal_time:
                    if day not in templates_data[template_id]['meals']:
                        templates_data[template_id]['meals'][day] = {}
                    
                    templates_data[template_id]['meals'][day][meal_time] = {
                        'recipe_name': meal.get('recipe_name'),
                        'servings': meal.get('servings', 1),
                        'image': meal.get('image', '🍽️')
                    }
        
        logging.info(f'Grouped into {len(templates_data)} templates')
        
        # Format templates
        templates = []
        for template_id, data in templates_data.items():
            template = {
                'id': f"template_{template_id}",
                'name': data['name'],
                'description': f"Curated {data['name'].lower()} with balanced nutrition",
                'week_start': '2024-01-01',
                'meals': data['meals'],
                'created_by': 'Admin',
                'is_admin_template': True,
                'created_at': '2024-01-01T00:00:00Z'
            }
            templates.append(template)
        
        logging.info(f'Returning {len(templates)} templates')
        return jsonify({'templates': templates}), 200
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        logging.error(f'Error: {e}')
        import traceback
        logging.error(f'Traceback: {traceback.format_exc()}')
        return jsonify({'error': f'Failed to get templates: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='127.0.0.1')