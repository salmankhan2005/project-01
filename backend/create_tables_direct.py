#!/usr/bin/env python3
"""
Direct table creation for meal plan sync
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

def create_admin_meal_plans_table():
    """Create admin_meal_plans table using direct insert"""
    logger.info('Creating admin_meal_plans table...')
    
    # Create a sample record to establish the table structure
    sample_plan = {
        'name': 'Sample Plan',
        'description': 'Sample meal plan',
        'week_start': '2024-01-01',
        'status': 'active',
        'created_by': 'admin',
        'meals': {
            'Monday': {
                'Breakfast': {
                    'recipe_name': 'Sample Breakfast',
                    'servings': 1,
                    'image': '🍳'
                }
            }
        }
    }
    
    try:
        result = supabase.table('admin_meal_plans').insert(sample_plan).execute()
        logger.info('admin_meal_plans table created successfully')
        
        # Delete the sample record
        supabase.table('admin_meal_plans').delete().eq('name', 'Sample Plan').execute()
        
    except Exception as e:
        logger.error(f'Failed to create admin_meal_plans table: {e}')

def create_meal_plan_notifications_table():
    """Create meal_plan_notifications table"""
    logger.info('Creating meal_plan_notifications table...')
    
    sample_notification = {
        'type': 'meal_plan_update',
        'action': 'create',
        'meal_plan_id': 1,
        'meal_plan_data': {'test': 'data'},
        'status': 'pending'
    }
    
    try:
        result = supabase.table('meal_plan_notifications').insert(sample_notification).execute()
        logger.info('meal_plan_notifications table created successfully')
        
        # Delete the sample record
        supabase.table('meal_plan_notifications').delete().eq('type', 'meal_plan_update').execute()
        
    except Exception as e:
        logger.error(f'Failed to create meal_plan_notifications table: {e}')

def create_sample_data():
    """Create sample meal plans"""
    logger.info('Creating sample meal plans...')
    
    sample_plans = [
        {
            'name': '7-Day Mediterranean Plan',
            'description': 'Healthy Mediterranean diet with fresh ingredients',
            'week_start': '2024-01-01',
            'status': 'active',
            'created_by': 'admin',
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
        {
            'name': 'Keto Weekly Plan',
            'description': 'Low-carb ketogenic meal plan',
            'week_start': '2024-01-01',
            'status': 'active',
            'created_by': 'admin',
            'meals': {
                'Monday': {
                    'Breakfast': {'recipe_name': 'Keto Scrambled Eggs', 'servings': 1, 'image': '🍳'},
                    'Lunch': {'recipe_name': 'Avocado Chicken Salad', 'servings': 1, 'image': '🥗'},
                    'Dinner': {'recipe_name': 'Grilled Salmon', 'servings': 1, 'image': '🐟'}
                }
            }
        }
    ]
    
    for plan in sample_plans:
        try:
            result = supabase.table('admin_meal_plans').insert(plan).execute()
            logger.info(f'Created sample meal plan: {plan["name"]}')
        except Exception as e:
            logger.error(f'Failed to create meal plan {plan["name"]}: {e}')

def main():
    logger.info('Creating tables and sample data...')
    
    create_admin_meal_plans_table()
    create_meal_plan_notifications_table()
    create_sample_data()
    
    logger.info('Database setup completed!')

if __name__ == '__main__':
    main()