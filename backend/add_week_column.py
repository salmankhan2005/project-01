#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# SQL to add the missing week column
add_column_sql = """
ALTER TABLE meal_plans 
ADD COLUMN IF NOT EXISTS week VARCHAR(50) DEFAULT 'Week - 1';
"""

print("Run this SQL in your Supabase SQL Editor:")
print("=" * 50)
print(add_column_sql)
print("=" * 50)