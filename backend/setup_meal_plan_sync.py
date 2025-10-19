#!/usr/bin/env python3
"""
Setup script for meal plan synchronization
Creates necessary tables and initializes the sync system
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not all([SUPABASE_URL, SUPABASE_KEY]):
    logger.error('Missing required environment variables')
    sys.exit(1)

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info('Connected to Supabase successfully')
except Exception as e:
    logger.error(f'Failed to create Supabase client: {e}')
    sys.exit(1)

def execute_sql_file(filename):
    """Execute SQL commands from a file"""
    try:
        with open(filename, 'r') as file:
            sql_content = file.read()
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement:
                try:
                    # Use RPC to execute raw SQL
                    result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                    logger.info(f'Executed SQL statement successfully')
                except Exception as e:
                    logger.warning(f'SQL statement failed (might be expected): {e}')
                    
    except FileNotFoundError:
        logger.error(f'SQL file not found: {filename}')
    except Exception as e:
        logger.error(f'Error executing SQL file {filename}: {e}')

def create_tables():
    """Create necessary tables for meal plan sync"""
    logger.info('Creating meal plan sync tables...')
    
    # Create meal_plan_notifications table
    try:
        supabase.table('meal_plan_notifications').select('id').limit(1).execute()
        logger.info('meal_plan_notifications table already exists')
    except:
        logger.info('Creating meal_plan_notifications table...')
        # Execute the schema file
        execute_sql_file('schemas/meal_plan_notifications_schema.sql')

def create_sample_admin_meal_plans():
    """Create sample admin meal plans for testing"""
    logger.info('Creating sample admin meal plans...')
    
    sample_plans = [
        {
            'name': '7-Day Mediterranean Plan',
            'description': 'Healthy Mediterranean diet with fresh ingredients and balanced nutrition',
            'week_start': '2024-01-01',
            'status': 'active',
            'created_by': 'admin',
            'meals': {
                'Monday': {
                    'Breakfast': {
                        'recipe_name': 'Greek Yogurt with Berries',
                        'servings': 1,
                        'image': '🥣'
                    },
                    'Lunch': {
                        'recipe_name': 'Mediterranean Salad',
                        'servings': 1,
                        'image': '🥗'
                    },
                    'Dinner': {
                        'recipe_name': 'Grilled Fish with Vegetables',
                        'servings': 1,
                        'image': '🐟'
                    }
                },
                'Tuesday': {
                    'Breakfast': {
                        'recipe_name': 'Avocado Toast',
                        'servings': 1,
                        'image': '🥑'
                    },
                    'Lunch': {
                        'recipe_name': 'Hummus Bowl',
                        'servings': 1,
                        'image': '🍲'
                    },
                    'Dinner': {
                        'recipe_name': 'Chicken Souvlaki',
                        'servings': 1,
                        'image': '🍗'
                    }
                },
                'Wednesday': {
                    'Breakfast': {
                        'recipe_name': 'Mediterranean Omelet',
                        'servings': 1,
                        'image': '🍳'
                    },
                    'Lunch': {
                        'recipe_name': 'Quinoa Tabbouleh',
                        'servings': 1,
                        'image': '🥙'
                    },
                    'Dinner': {
                        'recipe_name': 'Baked Cod with Olives',
                        'servings': 1,
                        'image': '🐟'
                    }
                }
            }
        },
        {
            'name': 'Keto Weekly Plan',
            'description': 'Low-carb ketogenic meal plan for weight management',
            'week_start': '2024-01-01',
            'status': 'active',
            'created_by': 'admin',
            'meals': {
                'Monday': {
                    'Breakfast': {
                        'recipe_name': 'Keto Scrambled Eggs',
                        'servings': 1,
                        'image': '🍳'
                    },
                    'Lunch': {
                        'recipe_name': 'Avocado Chicken Salad',
                        'servings': 1,
                        'image': '🥗'
                    },
                    'Dinner': {
                        'recipe_name': 'Grilled Salmon with Asparagus',
                        'servings': 1,
                        'image': '🐟'
                    }
                },
                'Tuesday': {
                    'Breakfast': {
                        'recipe_name': 'Bacon and Eggs',
                        'servings': 1,
                        'image': '🥓'
                    },
                    'Lunch': {
                        'recipe_name': 'Keto Caesar Salad',
                        'servings': 1,
                        'image': '🥗'
                    },
                    'Dinner': {
                        'recipe_name': 'Beef Steak with Butter',
                        'servings': 1,
                        'image': '🥩'
                    }
                }
            }
        },
        {
            'name': 'Vegetarian Delight',
            'description': 'Plant-based meals rich in nutrients and flavor',
            'week_start': '2024-01-01',
            'status': 'active',
            'created_by': 'admin',
            'meals': {
                'Monday': {
                    'Breakfast': {
                        'recipe_name': 'Overnight Oats with Fruits',
                        'servings': 1,
                        'image': '🥣'
                    },
                    'Lunch': {
                        'recipe_name': 'Veggie Buddha Bowl',
                        'servings': 1,
                        'image': '🥙'
                    },
                    'Dinner': {
                        'recipe_name': 'Lentil Curry',
                        'servings': 1,
                        'image': '🍛'
                    }
                },
                'Tuesday': {
                    'Breakfast': {
                        'recipe_name': 'Smoothie Bowl',
                        'servings': 1,
                        'image': '🥤'
                    },
                    'Lunch': {
                        'recipe_name': 'Quinoa Salad',
                        'servings': 1,
                        'image': '🥗'
                    },
                    'Dinner': {
                        'recipe_name': 'Vegetable Stir Fry',
                        'servings': 1,
                        'image': '🥘'
                    }
                }
            }
        }
    ]
    
    for plan in sample_plans:
        try:
            # Check if plan already exists
            existing = supabase.table('admin_meal_plans').select('id').eq('name', plan['name']).execute()
            
            if not existing.data:
                result = supabase.table('admin_meal_plans').insert(plan).execute()
                logger.info(f'Created sample meal plan: {plan["name"]}')
            else:
                logger.info(f'Sample meal plan already exists: {plan["name"]}')
                
        except Exception as e:
            logger.error(f'Failed to create sample meal plan {plan["name"]}: {e}')

def setup_sync_system():
    """Initialize the meal plan sync system"""
    logger.info('Setting up meal plan sync system...')
    
    try:
        # Import and test the sync service
        from meal_plan_sync import sync_meal_plan_to_users
        logger.info('Meal plan sync service imported successfully')
        
        # Test sync with a sample plan
        test_plan = {
            'id': 999,
            'name': 'Test Sync Plan',
            'status': 'active',
            'meals': {
                'Monday': {
                    'Breakfast': {
                        'recipe_name': 'Test Breakfast',
                        'servings': 1,
                        'image': '🍳'
                    }
                }
            }
        }
        
        sync_meal_plan_to_users(test_plan, 'create')
        logger.info('Sync system test completed successfully')
        
    except Exception as e:
        logger.warning(f'Sync system setup failed: {e}')

def main():
    """Main setup function"""
    logger.info('Starting meal plan sync setup...')
    
    # Create tables
    create_tables()
    
    # Create sample data
    create_sample_admin_meal_plans()
    
    # Setup sync system
    setup_sync_system()
    
    logger.info('Meal plan sync setup completed successfully!')
    logger.info('You can now:')
    logger.info('1. Create meal plans in the admin app')
    logger.info('2. Browse templates in the user app')
    logger.info('3. Apply templates to user meal plans')
    logger.info('4. Sync changes automatically between apps')

if __name__ == '__main__':
    main()