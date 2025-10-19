#!/usr/bin/env python3
"""
Create meal plan templates using existing schema
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_meal_plan_templates():
    """Create meal plan templates using existing table structure"""
    logger.info('📝 Creating meal plan templates...')
    
    # Mediterranean Plan
    mediterranean_meals = [
        {'day': 'Monday', 'meal_time': 'Breakfast', 'recipe_name': 'Greek Yogurt with Berries', 'image': '🥣'},
        {'day': 'Monday', 'meal_time': 'Lunch', 'recipe_name': 'Mediterranean Salad', 'image': '🥗'},
        {'day': 'Monday', 'meal_time': 'Dinner', 'recipe_name': 'Grilled Fish with Vegetables', 'image': '🐟'},
        {'day': 'Tuesday', 'meal_time': 'Breakfast', 'recipe_name': 'Avocado Toast', 'image': '🥑'},
        {'day': 'Tuesday', 'meal_time': 'Lunch', 'recipe_name': 'Hummus Bowl', 'image': '🍲'},
        {'day': 'Tuesday', 'meal_time': 'Dinner', 'recipe_name': 'Chicken Souvlaki', 'image': '🍗'},
        {'day': 'Wednesday', 'meal_time': 'Breakfast', 'recipe_name': 'Mediterranean Omelet', 'image': '🍳'},
        {'day': 'Wednesday', 'meal_time': 'Lunch', 'recipe_name': 'Quinoa Tabbouleh', 'image': '🥙'},
        {'day': 'Wednesday', 'meal_time': 'Dinner', 'recipe_name': 'Baked Cod with Olives', 'image': '🐟'},
    ]
    
    # Keto Plan
    keto_meals = [
        {'day': 'Monday', 'meal_time': 'Breakfast', 'recipe_name': 'Keto Scrambled Eggs', 'image': '🍳'},
        {'day': 'Monday', 'meal_time': 'Lunch', 'recipe_name': 'Avocado Chicken Salad', 'image': '🥗'},
        {'day': 'Monday', 'meal_time': 'Dinner', 'recipe_name': 'Grilled Salmon with Asparagus', 'image': '🐟'},
        {'day': 'Tuesday', 'meal_time': 'Breakfast', 'recipe_name': 'Bacon and Eggs', 'image': '🥓'},
        {'day': 'Tuesday', 'meal_time': 'Lunch', 'recipe_name': 'Keto Caesar Salad', 'image': '🥗'},
        {'day': 'Tuesday', 'meal_time': 'Dinner', 'recipe_name': 'Beef Steak with Butter', 'image': '🥩'},
    ]
    
    templates = [
        {
            'name': '7-Day Mediterranean Plan',
            'description': 'Healthy Mediterranean diet with fresh ingredients',
            'template_id': 'admin_mediterranean',
            'meals': mediterranean_meals
        },
        {
            'name': 'Keto Weekly Plan', 
            'description': 'Low-carb ketogenic meal plan for weight management',
            'template_id': 'admin_keto',
            'meals': keto_meals
        }
    ]
    
    for template in templates:
        logger.info(f'Creating template: {template["name"]}')
        
        # Check if template already exists
        existing = supabase.table('meal_plans').select('id').eq('recipe_id', template['template_id']).execute()
        
        if existing.data:
            logger.info(f'📋 Template already exists: {template["name"]}')
            continue
            
        # Create meals for this template
        for meal in template['meals']:
            meal_record = {
                'user_id': None,  # Admin templates don't belong to users
                'recipe_id': f"{template['template_id']}_{meal['day']}_{meal['meal_time']}",
                'recipe_name': meal['recipe_name'],
                'day': meal['day'],
                'meal_time': meal['meal_time'],
                'servings': 1,
                'image': meal['image'],
                'week': f"template_{template['template_id']}"  # Special week identifier for templates
            }
            
            try:
                result = supabase.table('meal_plans').insert(meal_record).execute()
                logger.info(f'  ✅ Added: {meal["day"]} {meal["meal_time"]} - {meal["recipe_name"]}')
            except Exception as e:
                logger.error(f'  ❌ Failed to add meal: {e}')
        
        logger.info(f'✅ Completed template: {template["name"]}')

def list_templates():
    """List all created templates"""
    logger.info('📋 Listing meal plan templates...')
    
    try:
        # Get all template meals (where user_id is None and week starts with 'template_')
        result = supabase.table('meal_plans').select('*').is_('user_id', None).execute()
        
        if result.data:
            templates = {}
            for meal in result.data:
                week = meal.get('week', '')
                if week.startswith('template_'):
                    template_id = week.replace('template_', '')
                    if template_id not in templates:
                        templates[template_id] = []
                    templates[template_id].append(meal)
            
            for template_id, meals in templates.items():
                logger.info(f'📝 Template: {template_id}')
                logger.info(f'   Meals: {len(meals)}')
                for meal in meals[:3]:  # Show first 3 meals
                    logger.info(f'   - {meal["day"]} {meal["meal_time"]}: {meal["recipe_name"]}')
        else:
            logger.info('No templates found')
            
    except Exception as e:
        logger.error(f'❌ Error listing templates: {e}')

def main():
    logger.info('🚀 Setting up meal plan templates...')
    
    create_meal_plan_templates()
    list_templates()
    
    logger.info('✅ Template setup completed!')
    logger.info('📱 Templates are now available for the meal plan apps')

if __name__ == '__main__':
    main()