#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Simple SQL to create the table
create_sql = """
DROP TABLE IF EXISTS meal_plans;

CREATE TABLE meal_plans (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    recipe_id VARCHAR(255),
    recipe_name VARCHAR(255),
    day VARCHAR(20),
    meal_time VARCHAR(20),
    servings INTEGER DEFAULT 1,
    image VARCHAR(255) DEFAULT 'meal',
    time VARCHAR(50),
    week VARCHAR(50) DEFAULT 'Week - 1',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_meal_plans_user_id ON meal_plans(user_id);
ALTER TABLE meal_plans DISABLE ROW LEVEL SECURITY;
"""

print("Run this SQL in your Supabase SQL Editor:")
print("=" * 50)
print(create_sql)
print("=" * 50)