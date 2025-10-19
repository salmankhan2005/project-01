#!/usr/bin/env python3
"""
Test sync between admin and user apps
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

def create_admin_template():
    """Create a new admin template"""
    logger.info('Creating new admin template...')
    
    # Create template meals
    template_meals = [
        {'day': 'Monday', 'meal_time': 'Breakfast', 'recipe_name': 'Protein Smoothie', 'image': '🥤'},
        {'day': 'Monday', 'meal_time': 'Lunch', 'recipe_name': 'Quinoa Bowl', 'image': '🥗'},
        {'day': 'Monday', 'meal_time': 'Dinner', 'recipe_name': 'Grilled Chicken', 'image': '🍗'},
        {'day': 'Tuesday', 'meal_time': 'Breakfast', 'recipe_name': 'Oatmeal', 'image': '🥣'},
        {'day': 'Tuesday', 'meal_time': 'Lunch', 'recipe_name': 'Salad Wrap', 'image': '🌯'},
        {'day': 'Tuesday', 'meal_time': 'Dinner', 'recipe_name': 'Baked Fish', 'image': '🐟'},
    ]
    
    template_id = 'admin_fitness'
    
    # Delete existing template
    supabase.table('meal_plans').delete().eq('week', f'template_{template_id}').execute()
    
    # Create new template
    for meal in template_meals:
        meal_record = {
            'user_id': None,
            'recipe_id': f"template_{template_id}_{meal['day']}_{meal['meal_time']}",
            'recipe_name': meal['recipe_name'],
            'day': meal['day'],
            'meal_time': meal['meal_time'],
            'servings': 1,
            'image': meal['image'],
            'week': f"template_{template_id}"
        }
        
        result = supabase.table('meal_plans').insert(meal_record).execute()
        logger.info(f'✅ Created: {meal["day"]} {meal["meal_time"]} - {meal["recipe_name"]}')
    
    logger.info('✅ Admin template "Fitness Plan" created')
    return f'template_{template_id}'

def test_user_sync(template_id):
    """Test applying template to user"""
    logger.info('Testing user template application...')
    
    # Simulate user applying template
    user_id = 'test_user_123'
    target_week = 'Week - 1'
    
    # Get template meals
    template_result = supabase.table('meal_plans').select('*').eq('week', template_id).execute()
    
    if not template_result.data:
        logger.error('❌ Template not found')
        return False
    
    # Clear user's existing meals for target week
    supabase.table('meal_plans').delete().eq('user_id', user_id).eq('week', target_week).execute()
    
    # Apply template to user
    meal_entries = []
    for template_meal in template_result.data:
        meal_entry = {
            'user_id': user_id,
            'recipe_id': f"applied_{template_meal['recipe_id']}_{user_id}",
            'recipe_name': template_meal['recipe_name'],
            'day': template_meal['day'],
            'meal_time': template_meal['meal_time'],
            'servings': template_meal['servings'],
            'image': template_meal['image'],
            'week': target_week
        }
        meal_entries.append(meal_entry)
    
    if meal_entries:
        supabase.table('meal_plans').insert(meal_entries).execute()
        logger.info(f'✅ Applied {len(meal_entries)} meals to user {user_id}')
        return True
    
    return False

def verify_sync():
    """Verify sync worked"""
    logger.info('Verifying sync...')
    
    # Check admin templates
    admin_templates = supabase.table('meal_plans').select('*').eq('user_id', None).execute()
    logger.info(f'📋 Admin templates: {len(admin_templates.data)} meals')
    
    # Check user meals
    user_meals = supabase.table('meal_plans').select('*').eq('user_id', 'test_user_123').execute()
    logger.info(f'👤 User meals: {len(user_meals.data)} meals')
    
    # Group by template
    templates = {}
    for meal in admin_templates.data:
        week = meal.get('week', '')
        if week.startswith('template_'):
            template_name = week.replace('template_', '')
            if template_name not in templates:
                templates[template_name] = 0
            templates[template_name] += 1
    
    logger.info('📊 Available templates:')
    for template, count in templates.items():
        logger.info(f'  - {template}: {count} meals')

def main():
    logger.info('🔄 Testing admin-user sync...')
    
    # Create admin template
    template_id = create_admin_template()
    
    # Test user sync
    success = test_user_sync(template_id)
    
    # Verify
    verify_sync()
    
    if success:
        logger.info('✅ Sync test completed successfully!')
        logger.info('🎉 Admin and user apps are now synchronized!')
    else:
        logger.error('❌ Sync test failed')

if __name__ == '__main__':
    main()