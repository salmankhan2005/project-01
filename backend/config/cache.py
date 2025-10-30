import os
import json
import logging
from typing import Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SimpleCache:
    """Simple in-memory cache implementation"""
    
    def __init__(self):
        self.cache = {}
        self.default_ttl = 300  # 5 minutes
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if key in self.cache:
                entry = self.cache[key]
                if entry['expires'] > datetime.now():
                    return entry['value']
                else:
                    del self.cache[key]
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            if ttl is None:
                ttl = self.default_ttl
            
            self.cache[key] = {
                'value': value,
                'expires': datetime.now() + timedelta(seconds=ttl)
            }
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

# Global cache instance
cache = SimpleCache()