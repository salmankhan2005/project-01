from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print('Checking meal_plans table for templates...')
try:
    # Check all records
    result = supabase.table('meal_plans').select('*').execute()
    print(f'Total records in meal_plans: {len(result.data)}')
    
    # Filter for templates
    template_meals = [meal for meal in result.data if meal.get('user_id') is None]
    print(f'Template meals (user_id is None): {len(template_meals)}')
    
    if template_meals:
        print('Sample template meals:')
        for meal in template_meals[:5]:
            print(f'  Week: {meal.get("week")}, Day: {meal.get("day")}, Meal: {meal.get("meal_time")}, Recipe: {meal.get("recipe_name")}')
    
    # Check for template weeks
    weeks = set([meal.get('week') for meal in result.data if meal.get('week', '').startswith('template_')])
    print(f'Template weeks found: {weeks}')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()