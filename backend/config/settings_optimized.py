import os
import secrets
from dotenv import load_dotenv
from typing import List, Optional

# Load environment variables
load_dotenv()

class Config:
    """Application configuration with validation and security best practices"""
    
    # Required environment variables
    REQUIRED_VARS = ['SUPABASE_URL', 'SUPABASE_KEY', 'JWT_SECRET']
    
    def __init__(self):
        self._validate_required_vars()
        self._setup_config()
    
    def _validate_required_vars(self) -> None:
        """Validate that all required environment variables are present"""
        missing_vars = [var for var in self.REQUIRED_VARS if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f'Missing required environment variables: {missing_vars}')
    
    def _setup_config(self) -> None:
        """Setup configuration with proper validation"""
        # Database configuration
        self.SUPABASE_URL = os.getenv('SUPABASE_URL')
        self.SUPABASE_KEY = os.getenv('SUPABASE_KEY')
        
        # Security configuration
        self.JWT_SECRET = os.getenv('JWT_SECRET')
        self.ADMIN_JWT_SECRET = os.getenv('ADMIN_JWT_SECRET', secrets.token_urlsafe(32))
        
        # Validate JWT secret strength
        if len(self.JWT_SECRET) < 32:
            raise ValueError('JWT_SECRET must be at least 32 characters long for security')
        
        # Server configuration
        self.DEBUG_MODE = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        self.PORT = self._get_int_env('PORT', 5000, 1, 65535)
        self.HOST = os.getenv('HOST', '127.0.0.1')
        
        # Security settings
        self.ALLOWED_ORIGINS = self._get_list_env('ALLOWED_ORIGINS', ['http://localhost:3000'])
        self.RATE_LIMIT_PER_MINUTE = self._get_int_env('RATE_LIMIT_PER_MINUTE', 100, 1, 10000)
        self.MAX_CONTENT_LENGTH = self._get_int_env('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # 16MB
        
        # Cache configuration
        self.REDIS_URL = os.getenv('REDIS_URL')
        self.CACHE_TTL = self._get_int_env('CACHE_TTL', 300, 60, 3600)  # 5 minutes default
        
        # Logging configuration
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.LOG_FILE = os.getenv('LOG_FILE', 'app.log')
        
        # Performance settings
        self.DB_POOL_SIZE = self._get_int_env('DB_POOL_SIZE', 10, 1, 100)
        self.DB_MAX_OVERFLOW = self._get_int_env('DB_MAX_OVERFLOW', 20, 0, 100)
        
        # Pagination limits
        self.DEFAULT_PAGE_SIZE = self._get_int_env('DEFAULT_PAGE_SIZE', 20, 1, 100)
        self.MAX_PAGE_SIZE = self._get_int_env('MAX_PAGE_SIZE', 100, 1, 1000)
    
    def _get_int_env(self, key: str, default: int, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
        """Get integer environment variable with validation"""
        try:
            value = int(os.getenv(key, default))
            if min_val is not None and value < min_val:
                raise ValueError(f'{key} must be at least {min_val}')
            if max_val is not None and value > max_val:
                raise ValueError(f'{key} must be at most {max_val}')
            return value
        except ValueError as e:
            raise ValueError(f'Invalid value for {key}: {e}')
    
    def _get_list_env(self, key: str, default: List[str]) -> List[str]:
        """Get list environment variable"""
        value = os.getenv(key)
        if not value:
            return default
        return [item.strip() for item in value.split(',') if item.strip()]
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return not self.DEBUG_MODE and os.getenv('FLASK_ENV') == 'production'
    
    def get_database_config(self) -> dict:
        """Get database configuration"""
        return {
            'url': self.SUPABASE_URL,
            'key': self.SUPABASE_KEY,
            'pool_size': self.DB_POOL_SIZE,
            'max_overflow': self.DB_MAX_OVERFLOW
        }
    
    def get_security_config(self) -> dict:
        """Get security configuration"""
        return {
            'jwt_secret': self.JWT_SECRET,
            'admin_jwt_secret': self.ADMIN_JWT_SECRET,
            'allowed_origins': self.ALLOWED_ORIGINS,
            'rate_limit': self.RATE_LIMIT_PER_MINUTE,
            'max_content_length': self.MAX_CONTENT_LENGTH
        }
    
    def get_cache_config(self) -> dict:
        """Get cache configuration"""
        return {
            'redis_url': self.REDIS_URL,
            'ttl': self.CACHE_TTL
        }

# Global configuration instance
try:
    config = Config()
except Exception as e:
    print(f"Configuration error: {e}")
    raise

# Backward compatibility exports
JWT_SECRET = config.JWT_SECRET
ADMIN_JWT_SECRET = config.ADMIN_JWT_SECRET
DEBUG_MODE = config.DEBUG_MODE
PORT = config.PORT
HOST = config.HOST