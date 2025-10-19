#!/usr/bin/env python3
"""
Simple setup using existing tables
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

def test_connection():
    """Test database connection"""
    try:
        result = supabase.table('meal_plans').select('id').limit(1).execute()
        logger.info('✅ Connected to database successfully')
        logger.info(f'Found meal_plans table with {len(result.data)} records')
        return True
    except Exception as e:
        logger.error(f'❌ Database connection failed: {e}')
        return False

def create_sample_admin_meal_plans():
    """Create sample admin meal plans in existing meal_plans table"""
    logger.info('Creating sample admin meal plans...')
    
    # Use existing meal_plans table structure
    sample_plans = [
        {
            'user_id': None,  # Admin plans don't belong to specific users
            'week_name': '7-Day Mediterranean Plan',
            'meal_type': 'template',
            'recipe_id': 'admin_template_1',
            'recipe_name': '7-Day Mediterranean Plan',
            'recipe_data': {
                'description': 'Healthy Mediterranean diet with fresh ingredients',
                'meals': {
                    'Monday': {
                        'Breakfast': {'recipe_name': 'Greek Yogurt with Berries', 'servings': 1, 'image': '🥣'},
                        'Lunch': {'recipe_name': 'Mediterranean Salad', 'servings': 1, 'image': '🥗'},
                        'Dinner': {'recipe_name': 'Grilled Fish with Vegetables', 'servings': 1, 'image': '🐟'}
                    },
                    'Tuesday': {
                        'Breakfast': {'recipe_name': 'Avocado Toast', 'servings': 1, 'image': '🥑'},
                        'Lunch': {'recipe_name': 'Hummus Bowl', 'servings': 1, 'image': '🍲'},
                        'Dinner': {'recipe_name': 'Chicken Souvlaki', 'servings': 1, 'image': '🍗'}
                    }
                }
            },
            'week': 'template'
        },
        {
            'user_id': None,
            'week_name': 'Keto Weekly Plan',
            'meal_type': 'template',
            'recipe_id': 'admin_template_2',
            'recipe_name': 'Keto Weekly Plan',
            'recipe_data': {
                'description': 'Low-carb ketogenic meal plan',
                'meals': {
                    'Monday': {
                        'Breakfast': {'recipe_name': 'Keto Scrambled Eggs', 'servings': 1, 'image': '🍳'},
                        'Lunch': {'recipe_name': 'Avocado Chicken Salad', 'servings': 1, 'image': '🥗'},
                        'Dinner': {'recipe_name': 'Grilled Salmon', 'servings': 1, 'image': '🐟'}
                    }
                }
            },
            'week': 'template'
        }
    ]
    
    for plan in sample_plans:
        try:
            # Check if template already exists
            existing = supabase.table('meal_plans').select('id').eq('recipe_id', plan['recipe_id']).execute()
            
            if not existing.data:
                result = supabase.table('meal_plans').insert(plan).execute()
                logger.info(f'✅ Created template: {plan["recipe_name"]}')
            else:
                logger.info(f'📋 Template already exists: {plan["recipe_name"]}')
                
        except Exception as e:
            logger.error(f'❌ Failed to create template {plan["recipe_name"]}: {e}')

def main():
    logger.info('🚀 Starting simple meal plan setup...')
    
    if not test_connection():
        return
    
    create_sample_admin_meal_plans()
    
    logger.info('✅ Setup completed!')
    logger.info('📱 You can now use the meal plan templates in your apps')

if __name__ == '__main__':
    main()