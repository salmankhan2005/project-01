#!/usr/bin/env python3
"""
Check existing table schema
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

def check_meal_plans_structure():
    """Check the structure of meal_plans table"""
    try:
        result = supabase.table('meal_plans').select('*').limit(1).execute()
        if result.data:
            logger.info('✅ meal_plans table structure:')
            for key in result.data[0].keys():
                logger.info(f'  - {key}')
        else:
            logger.info('📋 meal_plans table is empty')
            
        # Try to insert a simple record to see what works
        test_record = {
            'user_id': None,
            'week_name': 'Test Template',
            'recipe_id': 'test_template',
            'recipe_name': 'Test Template',
            'recipe_data': {'test': 'data'}
        }
        
        logger.info('🧪 Testing insert with basic structure...')
        result = supabase.table('meal_plans').insert(test_record).execute()
        
        if result.data:
            logger.info('✅ Basic insert successful')
            # Clean up test record
            supabase.table('meal_plans').delete().eq('recipe_id', 'test_template').execute()
        
    except Exception as e:
        logger.error(f'❌ Error: {e}')

def create_working_templates():
    """Create templates with working structure"""
    logger.info('📝 Creating meal plan templates...')
    
    templates = [
        {
            'user_id': None,
            'week_name': '7-Day Mediterranean Plan',
            'recipe_id': 'admin_mediterranean_plan',
            'recipe_name': '7-Day Mediterranean Plan',
            'recipe_data': {
                'type': 'admin_template',
                'description': 'Healthy Mediterranean diet with fresh ingredients',
                'meals': {
                    'Monday': {
                        'Breakfast': {'name': 'Greek Yogurt with Berries', 'image': '🥣'},
                        'Lunch': {'name': 'Mediterranean Salad', 'image': '🥗'},
                        'Dinner': {'name': 'Grilled Fish with Vegetables', 'image': '🐟'}
                    },
                    'Tuesday': {
                        'Breakfast': {'name': 'Avocado Toast', 'image': '🥑'},
                        'Lunch': {'name': 'Hummus Bowl', 'image': '🍲'},
                        'Dinner': {'name': 'Chicken Souvlaki', 'image': '🍗'}
                    }
                }
            }
        },
        {
            'user_id': None,
            'week_name': 'Keto Weekly Plan',
            'recipe_id': 'admin_keto_plan',
            'recipe_name': 'Keto Weekly Plan',
            'recipe_data': {
                'type': 'admin_template',
                'description': 'Low-carb ketogenic meal plan for weight management',
                'meals': {
                    'Monday': {
                        'Breakfast': {'name': 'Keto Scrambled Eggs', 'image': '🍳'},
                        'Lunch': {'name': 'Avocado Chicken Salad', 'image': '🥗'},
                        'Dinner': {'name': 'Grilled Salmon with Asparagus', 'image': '🐟'}
                    },
                    'Tuesday': {
                        'Breakfast': {'name': 'Bacon and Eggs', 'image': '🥓'},
                        'Lunch': {'name': 'Keto Caesar Salad', 'image': '🥗'},
                        'Dinner': {'name': 'Beef Steak with Butter', 'image': '🥩'}
                    }
                }
            }
        }
    ]
    
    for template in templates:
        try:
            # Check if exists
            existing = supabase.table('meal_plans').select('id').eq('recipe_id', template['recipe_id']).execute()
            
            if not existing.data:
                result = supabase.table('meal_plans').insert(template).execute()
                logger.info(f'✅ Created: {template["recipe_name"]}')
            else:
                logger.info(f'📋 Exists: {template["recipe_name"]}')
                
        except Exception as e:
            logger.error(f'❌ Failed to create {template["recipe_name"]}: {e}')

def main():
    logger.info('🔍 Checking database schema and creating templates...')
    check_meal_plans_structure()
    create_working_templates()
    logger.info('✅ Database setup completed!')

if __name__ == '__main__':
    main()