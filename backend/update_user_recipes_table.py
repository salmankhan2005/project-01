#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# SQL to update the table structure
update_sql = """
-- Drop the existing table and recreate with new structure
DROP TABLE IF EXISTS user_recipes;

CREATE TABLE user_recipes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    recipe_id VARCHAR(255) NOT NULL,
    recipe_name VARCHAR(255) NOT NULL,
    recipe_data JSONB,
    is_saved BOOLEAN DEFAULT TRUE,
    is_favorite BOOLEAN DEFAULT FALSE,
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    saved_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, recipe_id)
);

CREATE INDEX idx_user_recipes_user_id ON user_recipes(user_id);
CREATE INDEX idx_user_recipes_recipe_id ON user_recipes(recipe_id);

ALTER TABLE user_recipes DISABLE ROW LEVEL SECURITY;
"""

print("Run this SQL in your Supabase SQL Editor to update the table:")
print("=" * 60)
print(update_sql)
print("=" * 60)