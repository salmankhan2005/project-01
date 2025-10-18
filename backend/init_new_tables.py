#!/usr/bin/env python3
"""
Initialize new database tables for enhanced meal planning features
"""

from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not all([SUPABASE_URL, SUPABASE_KEY]):
    print('Missing required environment variables')
    exit(1)

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Connected to Supabase successfully")
except Exception as e:
    print(f'Failed to create Supabase client: {e}')
    exit(1)

# SQL commands to create tables
sql_commands = [
    # User persons table
    """
    CREATE TABLE IF NOT EXISTS user_persons (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        preferences TEXT,
        allergies TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """,
    
    # User preferences table
    """
    CREATE TABLE IF NOT EXISTS user_preferences (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        selected_week VARCHAR(50) DEFAULT 'Week - 1',
        view_mode VARCHAR(20) DEFAULT 'list',
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        UNIQUE(user_id)
    );
    """,
    
    # Add columns to meal_plans if they don't exist
    """
    ALTER TABLE meal_plans 
    ADD COLUMN IF NOT EXISTS assigned_to UUID REFERENCES user_persons(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS week VARCHAR(50) DEFAULT 'Week - 1';
    """,
    
    # Create indexes
    """
    CREATE INDEX IF NOT EXISTS idx_user_persons_user_id ON user_persons(user_id);
    CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
    """,
    
    # Disable RLS
    """
    ALTER TABLE user_persons DISABLE ROW LEVEL SECURITY;
    ALTER TABLE user_preferences DISABLE ROW LEVEL SECURITY;
    """
]

def execute_sql_commands():
    for i, sql in enumerate(sql_commands):
        try:
            print(f"Executing command {i+1}/{len(sql_commands)}...")
            # Use rpc to execute raw SQL
            result = supabase.rpc('exec_sql', {'sql_query': sql}).execute()
            print(f"✓ Command {i+1} executed successfully")
        except Exception as e:
            print(f"✗ Command {i+1} failed: {e}")
            # Continue with other commands
            continue

if __name__ == "__main__":
    print("Initializing new database tables...")
    execute_sql_commands()
    print("Database initialization completed!")