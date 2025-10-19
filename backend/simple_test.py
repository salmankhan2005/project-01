from supabase import create_client
import os
from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta, timezone

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
JWT_SECRET = os.getenv('JWT_SECRET')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create a test token
token = jwt.encode({
    'user_id': 1,
    'email': 'test@example.com',
    'exp': datetime.now(timezone.utc) + timedelta(days=7)
}, JWT_SECRET, algorithm='HS256')

print('Testing template processing...')

try:
    # Get template meals from meal_plans table
    result = supabase.table('meal_plans').select('*').execute()
    template_meals = [meal for meal in result.data if meal.get('user_id') is None and meal.get('week', '').startswith('template_')]
    
    print(f'Found {len(template_meals)} template meals')
    
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
    
    print(f'Grouped into {len(templates_data)} templates')
    
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
        print(f'Template: {template["name"]} - {len(template["meals"])} days')
    
    print(f'Successfully created {len(templates)} templates')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()