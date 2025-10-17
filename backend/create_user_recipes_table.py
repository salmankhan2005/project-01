#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: Missing Supabase credentials in .env file")
    exit(1)

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# SQL to create user_recipes table
create_table_sql = """
CREATE TABLE IF NOT EXISTS user_recipes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    recipe_id UUID REFERENCES recipes(id) ON DELETE CASCADE,
    is_saved BOOLEAN DEFAULT TRUE,
    is_favorite BOOLEAN DEFAULT FALSE,
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    saved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, recipe_id)
);

CREATE INDEX IF NOT EXISTS idx_user_recipes_user_id ON user_recipes(user_id);
CREATE INDEX IF NOT EXISTS idx_user_recipes_recipe_id ON user_recipes(recipe_id);

ALTER TABLE user_recipes DISABLE ROW LEVEL SECURITY;
"""

print("Please run this SQL in your Supabase SQL Editor:")
print("=" * 50)
print(create_table_sql)
print("=" * 50)
print("\nAfter running the SQL, liked recipes will be stored in the database.")

# Test if table exists by trying to query it
try:
    result = supabase.table('user_recipes').select('*').limit(1).execute()
    print("Table already exists and is accessible!")
except Exception as e:
    print(f"Table doesn't exist yet. Please run the SQL above in Supabase dashboard.")