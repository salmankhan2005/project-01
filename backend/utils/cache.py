import redis
import json
import os
from typing import Any, Optional

class Cache:
    def __init__(self):
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
        except:
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        if not self.redis_client:
            return None
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except:
            return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        if not self.redis_client:
            return False
        try:
            self.redis_client.setex(key, ttl, json.dumps(value))
            return True
        except:
            return False

cache = Cache()