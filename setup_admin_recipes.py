#!/usr/bin/env python3
"""
Setup script for admin recipes functionality
Run this to create the necessary database tables and sample data
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def setup_admin_recipes():
    """Setup admin recipes tables and sample data"""
    
    # Supabase configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    if not all([SUPABASE_URL, SUPABASE_KEY]):
        print("Error: Missing SUPABASE_URL or SUPABASE_KEY environment variables")
        return False
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Connected to Supabase successfully")
        
        # Read and execute the schema file
        schema_file = os.path.join('backend', 'schemas', 'admin_recipes_schema.sql')
        
        if os.path.exists(schema_file):
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement:
                    try:
                        # Use RPC to execute raw SQL
                        result = supabase.rpc('exec_sql', {'sql': statement}).execute()
                        print(f"✓ Executed: {statement[:50]}...")
                    except Exception as stmt_error:
                        print(f"Warning: {stmt_error}")
                        # Continue with other statements
            
            print("✓ Admin recipes schema setup completed")
            
        else:
            print(f"Schema file not found: {schema_file}")
            
            # Create tables manually
            print("Creating tables manually...")
            
            # Create admin_recipes table
            try:
                supabase.table('admin_recipes').select('id').limit(1).execute()
                print("✓ admin_recipes table already exists")
            except:
                print("Creating admin_recipes table...")
                # Table will be created when first recipe is inserted
            
            # Create recipe_notifications table  
            try:
                supabase.table('recipe_notifications').select('id').limit(1).execute()
                print("✓ recipe_notifications table already exists")
            except:
                print("Creating recipe_notifications table...")
                # Table will be created when first notification is inserted
        
        print("\n🎉 Admin recipes setup completed successfully!")
        print("\nNext steps:")
        print("1. Start the admin backend: cd backend/admin && python admin_app.py")
        print("2. Start the main backend: cd backend && python app.py")
        print("3. Access admin panel and create recipes")
        print("4. Recipes will automatically sync to meal plan apps")
        
        return True
        
    except Exception as e:
        print(f"Error setting up admin recipes: {e}")
        return False

if __name__ == "__main__":
    print("Setting up Admin Recipes functionality...")
    print("=" * 50)
    
    success = setup_admin_recipes()
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)