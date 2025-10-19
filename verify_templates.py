#!/usr/bin/env python3
"""
Verify meal plan templates are available for sync
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def verify_templates():
    """Verify templates exist in database"""
    print("Checking meal plan templates in database...")
    
    try:
        # Get template meals (where user_id is NULL)
        result = supabase.table('meal_plans').select('*').is_('user_id', 'null').execute()
        
        if result.data:
            print(f"Found {len(result.data)} template meals")
            
            # Group by template
            templates = {}
            for meal in result.data:
                week = meal.get('week', '')
                if week.startswith('template_'):
                    template_name = week.replace('template_', '').replace('_', ' ').title()
                    if template_name not in templates:
                        templates[template_name] = []
                    templates[template_name].append(meal)
            
            print("\nAvailable templates:")
            for template_name, meals in templates.items():
                print(f"  - {template_name}: {len(meals)} meals")
                
                # Show sample meals
                for meal in meals[:3]:
                    print(f"    * {meal['day']} {meal['meal_time']}: {meal['recipe_name']}")
                if len(meals) > 3:
                    print(f"    ... and {len(meals) - 3} more meals")
            
            return len(templates) > 0
        else:
            print("No templates found in database")
            return False
            
    except Exception as e:
        print(f"Error checking templates: {e}")
        return False

def main():
    print("=== MEAL PLAN SYNC VERIFICATION ===")
    
    if verify_templates():
        print("\nSUCCESS: Templates are ready for sync!")
        print("\nNext steps:")
        print("1. Start user app (mealplan)")
        print("2. Navigate to Home page")
        print("3. Click 'Browse Templates' button")
        print("4. Select and apply a template")
        print("5. Templates will sync from admin to user app")
    else:
        print("\nERROR: No templates found")
        print("Run: python create_templates.py to create sample templates")

if __name__ == '__main__':
    main()