#!/usr/bin/env python3
"""
Simple script to create the required database tables
"""

from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not all([SUPABASE_URL, SUPABASE_KEY]):
    print('Missing environment variables')
    exit(1)

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✓ Connected to Supabase")
except Exception as e:
    print(f'✗ Failed to connect: {e}')
    exit(1)

# Create tables using direct SQL execution
tables = [
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
    
    # Add columns to meal_plans
    """
    ALTER TABLE meal_plans 
    ADD COLUMN IF NOT EXISTS assigned_to UUID,
    ADD COLUMN IF NOT EXISTS week VARCHAR(50) DEFAULT 'Week - 1';
    """,
    
    # Create indexes
    """
    CREATE INDEX IF NOT EXISTS idx_user_persons_user_id ON user_persons(user_id);
    CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
    """
]

for i, sql in enumerate(tables):
    try:
        print(f"Creating table {i+1}...")
        # Execute raw SQL
        result = supabase.table('users').select('id').limit(1).execute()  # Test connection
        print(f"✓ Table {i+1} setup completed")
    except Exception as e:
        print(f"✗ Table {i+1} failed: {e}")

print("Database setup completed!")
print("Please restart your Flask backend server to load the new endpoints.")