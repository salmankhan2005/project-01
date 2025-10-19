"""
Admin Recipe Sync Service
Handles recipe synchronization between admin and meal plan apps
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import jwt
from datetime import datetime, timezone
import logging

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
ADMIN_JWT_SECRET = os.getenv('ADMIN_JWT_SECRET', 'admin-jwt-secret-key')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def verify_admin_token(token):
    """Verify admin JWT token"""
    try:
        payload = jwt.decode(token, ADMIN_JWT_SECRET, algorithms=['HS256'])
        return payload
    except:
        return None

def sync_recipe_to_discover(recipe_data, action='create'):
    """
    Sync recipe changes - recipes are already in admin_recipes table
    Just log the action for now
    """
    try:
        logging.info(f"Recipe sync: {action} - {recipe_data.get('title')} (ID: {recipe_data.get('id')})")
        # Recipe is already in admin_recipes table, no additional sync needed
        return True
    except Exception as e:
        logging.error(f"Failed to sync recipe: {e}")
        return False

def notify_meal_plan_apps(recipe_data, action):
    """
    Notify meal plan apps about recipe changes
    This could be extended to use webhooks or real-time subscriptions
    """
    try:
        # Create notification record
        notification = {
            'type': 'recipe_change',
            'action': action,
            'recipe_id': recipe_data.get('id'),
            'recipe_title': recipe_data.get('title'),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'data': recipe_data
        }
        
        # Store notification for meal plan apps to poll
        supabase.table('recipe_notifications').insert(notification).execute()
        logging.info(f"Notification sent for recipe {action}: {recipe_data.get('title')}")
        
    except Exception as e:
        logging.error(f"Failed to send notification: {e}")

# Export functions for use in main admin app
__all__ = ['sync_recipe_to_discover', 'notify_meal_plan_apps', 'verify_admin_token']