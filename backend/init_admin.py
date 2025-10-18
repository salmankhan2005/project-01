from supabase import create_client
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

# Create a simple admin user directly
admin_data = {
    'email': 'admin@test.com',
    'password_hash': generate_password_hash('admin123'),
    'name': 'Admin User',
    'role': 'super_admin',
    'is_active': True
}

try:
    result = supabase.table('admin_users').insert(admin_data).execute()
    print("Admin created: admin@test.com / admin123")
except Exception as e:
    print(f"Error: {e}")