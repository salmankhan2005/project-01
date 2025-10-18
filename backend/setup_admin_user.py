from supabase import create_client
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Create admin user
admin_data = {
    'email': 'admin@test.com',
    'password_hash': generate_password_hash('admin123'),
    'name': 'Super Admin',
    'role': 'super_admin',
    'is_active': True
}

try:
    # Check if admin exists
    existing = supabase.table('admin_users').select('*').eq('email', 'admin@test.com').execute()
    if existing.data:
        print("Admin already exists: admin@test.com")
    else:
        result = supabase.table('admin_users').insert(admin_data).execute()
        print("✓ Admin created: admin@test.com / admin123")
        print(f"Admin ID: {result.data[0]['id']}")
except Exception as e:
    print(f"Error: {e}")
    # Try to create the table structure if it doesn't exist
    print("Attempting to create admin_users table...")
    try:
        # This will fail if table doesn't exist, which is expected
        supabase.table('admin_users').insert(admin_data).execute()
        print("✓ Admin created: admin@test.com / admin123")
    except Exception as e2:
        print(f"Table creation failed: {e2}")
        print("Please create the admin_users table in Supabase first")