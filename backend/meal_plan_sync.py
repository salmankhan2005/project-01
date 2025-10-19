"""
Meal Plan Synchronization Service
Handles syncing meal plans from admin to user apps
"""

from supabase import create_client, Client
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timezone
import json

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def sync_meal_plan_to_users(meal_plan_data, action='create'):
    """
    Sync meal plan changes to all user apps
    
    Args:
        meal_plan_data: The meal plan data to sync
        action: 'create', 'update', or 'delete'
    """
    try:
        # Create notification for meal plan apps
        notification_data = {
            'type': 'meal_plan_update',
            'action': action,
            'meal_plan_id': meal_plan_data.get('id'),
            'meal_plan_data': meal_plan_data,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'status': 'pending'
        }
        
        # Insert notification
        supabase.table('meal_plan_notifications').insert(notification_data).execute()
        
        logging.info(f'Meal plan {action} notification created for plan ID: {meal_plan_data.get("id")}')
        
        # If it's an active meal plan, also sync to user meal plans
        if meal_plan_data.get('status') == 'active' and action in ['create', 'update']:
            sync_to_user_meal_plans(meal_plan_data)
            
    except Exception as e:
        logging.error(f'Failed to sync meal plan: {e}')

def sync_to_user_meal_plans(admin_meal_plan):
    """
    Sync admin meal plan to individual user meal plans
    """
    try:
        # Get all active users
        users_result = supabase.table('users').select('id').execute()
        
        if not users_result.data:
            return
            
        # Parse meals from admin meal plan
        meals = admin_meal_plan.get('meals', {})
        
        # Create meal plan entries for each user
        for user in users_result.data:
            user_id = user['id']
            
            # Create meal plan entries for each day/meal combination
            for day, day_meals in meals.items():
                if isinstance(day_meals, dict):
                    for meal_time, meal_data in day_meals.items():
                        if meal_data and meal_data.get('recipe_name'):
                            meal_plan_entry = {
                                'user_id': user_id,
                                'week_name': admin_meal_plan.get('name', 'Admin Plan'),
                                'meal_type': meal_time,
                                'recipe_id': f"admin_{admin_meal_plan.get('id')}_{day}_{meal_time}",
                                'recipe_name': meal_data.get('recipe_name'),
                                'recipe_data': meal_data,
                                'planned_date': None,  # Will be set by user
                                'week': 'Week - 1',  # Default week
                                'day': day,
                                'servings': meal_data.get('servings', 1),
                                'image': meal_data.get('image', '🍽️'),
                                'is_admin_generated': True,
                                'admin_meal_plan_id': admin_meal_plan.get('id')
                            }
                            
                            # Use upsert to avoid duplicates
                            supabase.table('meal_plans').upsert(meal_plan_entry).execute()
        
        logging.info(f'Admin meal plan synced to user meal plans: {admin_meal_plan.get("name")}')
        
    except Exception as e:
        logging.error(f'Failed to sync to user meal plans: {e}')

def get_meal_plan_notifications(last_sync_time=None):
    """
    Get meal plan notifications for user apps
    """
    try:
        query = supabase.table('meal_plan_notifications').select('*').order('timestamp', desc=True)
        
        if last_sync_time:
            query = query.gte('timestamp', last_sync_time)
        else:
            query = query.limit(50)
            
        result = query.execute()
        return result.data
        
    except Exception as e:
        logging.error(f'Failed to get notifications: {e}')
        return []

def mark_notification_processed(notification_id):
    """
    Mark a notification as processed
    """
    try:
        supabase.table('meal_plan_notifications').update({
            'status': 'processed',
            'processed_at': datetime.now(timezone.utc).isoformat()
        }).eq('id', notification_id).execute()
        
    except Exception as e:
        logging.error(f'Failed to mark notification as processed: {e}')

def get_admin_meal_plans_for_users():
    """
    Get active admin meal plans formatted for user consumption
    """
    try:
        result = supabase.table('admin_meal_plans').select('*').eq('status', 'active').order('created_at', desc=True).execute()
        
        formatted_plans = []
        for plan in result.data:
            formatted_plan = {
                'id': f"admin_{plan['id']}",
                'name': plan['name'],
                'description': plan.get('description', ''),
                'week_start': plan.get('week_start'),
                'meals': plan.get('meals', {}),
                'created_by': 'Admin',
                'is_admin_plan': True,
                'created_at': plan.get('created_at')
            }
            formatted_plans.append(formatted_plan)
            
        return formatted_plans
        
    except Exception as e:
        logging.error(f'Failed to get admin meal plans: {e}')
        return []

if __name__ == '__main__':
    # Test the sync functionality
    test_meal_plan = {
        'id': 1,
        'name': 'Test Weekly Plan',
        'status': 'active',
        'meals': {
            'Monday': {
                'Breakfast': {
                    'recipe_name': 'Oatmeal with Berries',
                    'servings': 1,
                    'image': '🥣'
                },
                'Lunch': {
                    'recipe_name': 'Grilled Chicken Salad',
                    'servings': 1,
                    'image': '🥗'
                }
            }
        }
    }
    
    sync_meal_plan_to_users(test_meal_plan, 'create')
    print("Test sync completed")