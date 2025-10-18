#!/usr/bin/env python3
"""
Script to create the first super admin user
Run this script after setting up the database schema
"""

from supabase import create_client, Client
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
import sys

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not all([SUPABASE_URL, SUPABASE_KEY]):
    print('Error: Missing required environment variables')
    sys.exit(1)

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f'Error: Failed to create Supabase client: {e}')
    sys.exit(1)

def create_super_admin():
    print("Creating Super Admin User")
    print("-" * 30)
    
    email = input("Enter super admin email: ").strip()
    if not email:
        print("Error: Email is required")
        return
    
    password = input("Enter super admin password (min 8 chars): ").strip()
    if len(password) < 8:
        print("Error: Password must be at least 8 characters")
        return
    
    name = input("Enter super admin name: ").strip()
    if not name:
        print("Error: Name is required")
        return
    
    try:
        # Check if super admin already exists
        existing = supabase.table('admin_users').select('*').eq('email', email).execute()
        if existing.data:
            print(f"Error: Admin with email {email} already exists")
            return
        
        # Create super admin
        admin_data = {
            'email': email,
            'password_hash': generate_password_hash(password),
            'name': name,
            'role': 'super_admin',
            'is_active': True
        }
        
        result = supabase.table('admin_users').insert(admin_data).execute()
        
        if result.data:
            print(f"\n✅ Super admin created successfully!")
            print(f"Email: {email}")
            print(f"Name: {name}")
            print(f"Role: super_admin")
            print(f"\nYou can now login to the admin panel with these credentials.")
        else:
            print("Error: Failed to create super admin")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    create_super_admin()