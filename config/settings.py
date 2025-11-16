import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv('JWT_SECRET')
ADMIN_JWT_SECRET = os.getenv('ADMIN_JWT_SECRET', 'admin-super-secret-key')
DEBUG_MODE = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
PORT = int(os.getenv('PORT', 5000))
HOST = os.getenv('HOST', '127.0.0.1')

if not JWT_SECRET:
    raise ValueError('JWT_SECRET environment variable is required')