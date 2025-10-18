#!/usr/bin/env python3

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    # Drop the problematic unique constraint
    result = supabase.rpc('exec_sql', {
        'sql': 'DROP INDEX IF EXISTS idx_meal_plans_unique_week_slot;'
    }).execute()
    print("✅ Dropped unique constraint successfully")
    
    # Verify the constraint is gone
    check_result = supabase.rpc('exec_sql', {
        'sql': """
        SELECT indexname 
        FROM pg_indexes 
        WHERE tablename = 'meal_plans' 
        AND indexname = 'idx_meal_plans_unique_week_slot';
        """
    }).execute()
    
    if not check_result.data:
        print("✅ Constraint successfully removed")
    else:
        print("❌ Constraint still exists")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTry running this SQL manually in Supabase:")
    print("DROP INDEX IF EXISTS idx_meal_plans_unique_week_slot;")