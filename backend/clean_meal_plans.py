#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# SQL to remove the unique constraint that might be causing issues
fix_sql = """
-- Drop the problematic unique index if it exists
DROP INDEX IF EXISTS idx_meal_plans_unique_week_slot;

-- Recreate without the unique constraint
CREATE INDEX IF NOT EXISTS idx_meal_plans_week_user ON meal_plans(user_id, week);
"""

print("Run this SQL in your Supabase SQL Editor to fix week filtering:")
print("=" * 60)
print(fix_sql)
print("=" * 60)