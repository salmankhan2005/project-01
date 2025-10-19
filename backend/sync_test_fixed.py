#!/usr/bin/env python3
"""
Test sync between admin and user apps - Fixed version
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_or_create_test_user():
    """Get or create a test user"""
    try:
        # Try to get existing users
        users = supabase.table('users').select('id').limit(1).execute()
        if users.data:
            user_id = users.data[0]['id']
            logger.info(f'Using existing user: {user_id}')
            return user_id
    except:
        pass
    
    # Generate a valid UUID for test user
    test_user_id = str(uuid.uuid4())
    logger.info(f'Using test user ID: {test_user_id}')
    return test_user_id

def test_sync_flow():
    """Test complete sync flow"""
    logger.info('🔄 Testing complete sync flow...')
    
    # 1. Create admin template
    logger.info('1️⃣ Creating admin template...')
    template_meals = [
        {'day': 'Monday', 'meal_time': 'Breakfast', 'recipe_name': 'Power Smoothie', 'image': '🥤'},
        {'day': 'Monday', 'meal_time': 'Lunch', 'recipe_name': 'Protein Bowl', 'image': '🥗'},
        {'day': 'Tuesday', 'meal_time': 'Breakfast', 'recipe_name': 'Energy Oats', 'image': '🥣'},
    ]
    
    template_id = 'admin_sync_test'
    
    # Clear existing
    supabase.table('meal_plans').delete().eq('week', f'template_{template_id}').execute()
    
    # Create template
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
        supabase.table('meal_plans').insert(meal_record).execute()
    
    logger.info(f'✅ Created template with {len(template_meals)} meals')
    
    # 2. Test template retrieval (simulate user app)
    logger.info('2️⃣ Testing template retrieval...')
    templates = supabase.table('meal_plans').select('*').eq('user_id', None).execute()
    
    # Group by template
    template_groups = {}
    for meal in templates.data:
        week = meal.get('week', '')
        if week.startswith('template_'):
            if week not in template_groups:
                template_groups[week] = []
            template_groups[week].append(meal)
    
    logger.info(f'📋 Found {len(template_groups)} templates:')
    for template_name, meals in template_groups.items():
        logger.info(f'  - {template_name}: {len(meals)} meals')
    
    # 3. Test template application (simulate user applying)
    logger.info('3️⃣ Testing template application...')
    user_id = get_or_create_test_user()
    target_week = 'Week - 1'
    
    # Get our test template
    test_template = template_groups.get(f'template_{template_id}', [])
    
    if test_template:
        # Apply to user
        meal_entries = []
        for template_meal in test_template:
            meal_entry = {
                'user_id': user_id,
                'recipe_id': f"applied_{template_meal['recipe_id']}",
                'recipe_name': template_meal['recipe_name'],
                'day': template_meal['day'],
                'meal_time': template_meal['meal_time'],
                'servings': 1,
                'image': template_meal['image'],
                'week': target_week
            }
            meal_entries.append(meal_entry)
        
        # Insert user meals
        if meal_entries:
            supabase.table('meal_plans').insert(meal_entries).execute()
            logger.info(f'✅ Applied {len(meal_entries)} meals to user')
    
    # 4. Verify sync
    logger.info('4️⃣ Verifying sync...')
    user_meals = supabase.table('meal_plans').select('*').eq('user_id', user_id).eq('week', target_week).execute()
    logger.info(f'👤 User now has {len(user_meals.data)} meals for {target_week}')
    
    for meal in user_meals.data:
        logger.info(f'  - {meal["day"]} {meal["meal_time"]}: {meal["recipe_name"]}')
    
    return len(user_meals.data) > 0

def main():
    logger.info('🚀 Starting admin-user sync test...')
    
    success = test_sync_flow()
    
    if success:
        logger.info('✅ Sync test PASSED!')
        logger.info('🎉 Admin and user apps are synchronized!')
    else:
        logger.error('❌ Sync test FAILED!')

if __name__ == '__main__':
    main()