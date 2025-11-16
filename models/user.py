from datetime import datetime, timezone
from config.database import get_supabase_client
from werkzeug.security import generate_password_hash, check_password_hash

supabase = get_supabase_client()

class User:
    @staticmethod
    def create(email, password, name=None):
        hashed_password = generate_password_hash(password)
        user_data = {
            'email': email,
            'password_hash': hashed_password,
            'name': name or email.split('@')[0],
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        result = supabase.table('users').insert(user_data).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def find_by_email(email):
        result = supabase.table('users').select('*').eq('email', email).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def find_by_id(user_id):
        result = supabase.table('users').select('*').eq('id', user_id).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    def verify_password(user, password):
        return check_password_hash(user['password_hash'], password)
    
    @staticmethod
    def update_last_login(user_id):
        supabase.table('users').update({
            'updated_at': datetime.now(timezone.utc).isoformat()
        }).eq('id', user_id).execute()
    
    @staticmethod
    def get_all():
        result = supabase.table('users').select('id, email, name, created_at, updated_at').execute()
        return result.data