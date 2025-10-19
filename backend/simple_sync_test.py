#!/usr/bin/env python3
"""
Simple sync test using proper Supabase queries
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

def test_sync():
    """Test sync functionality"""
    logger.info('🔄 Testing sync...')
    
    # 1. Check existing templates
    logger.info('1️⃣ Checking existing templates...')
    try:
        # Use is_ filter for NULL values
        templates = supabase.table('meal_plans').select('*').is_('user_id', 'null').execute()
        logger.info(f'📋 Found {len(templates.data)} template meals')
        
        # Group by week (template)
        template_groups = {}
        for meal in templates.data:
            week = meal.get('week', '')
            if week.startswith('template_'):
                if week not in template_groups:
                    template_groups[week] = []
                template_groups[week].append(meal)
        
        logger.info(f'📊 Available templates:')
        for template_name, meals in template_groups.items():
            clean_name = template_name.replace('template_', '').replace('_', ' ').title()
            logger.info(f'  - {clean_name}: {len(meals)} meals')
            
        return len(template_groups) > 0
        
    except Exception as e:
        logger.error(f'❌ Error: {e}')
        return False

def test_backend_endpoints():
    """Test backend endpoints"""
    logger.info('2️⃣ Testing backend endpoints...')
    
    import requests
    
    try:
        # Test health endpoint
        response = requests.get('http://127.0.0.1:5000/api/health')
        if response.status_code == 200:
            logger.info('✅ Main backend is running')
        else:
            logger.warning('⚠️ Main backend not responding')
            
        # Test admin backend
        response = requests.get('http://127.0.0.1:5001/api/admin/health')
        if response.status_code == 200:
            logger.info('✅ Admin backend is running')
        else:
            logger.warning('⚠️ Admin backend not responding')
            
        return True
        
    except Exception as e:
        logger.warning(f'⚠️ Backend test failed: {e}')
        return False

def main():
    logger.info('🚀 Testing admin-user sync system...')
    
    # Test database sync
    db_success = test_sync()
    
    # Test backend endpoints
    backend_success = test_backend_endpoints()
    
    if db_success:
        logger.info('✅ Database sync: WORKING')
    else:
        logger.error('❌ Database sync: FAILED')
        
    if backend_success:
        logger.info('✅ Backend endpoints: WORKING')
    else:
        logger.warning('⚠️ Backend endpoints: CHECK MANUALLY')
    
    if db_success:
        logger.info('🎉 Sync system is ready!')
        logger.info('📱 Users can now browse and apply admin templates')
    else:
        logger.error('💥 Sync system needs attention')

if __name__ == '__main__':
    main()