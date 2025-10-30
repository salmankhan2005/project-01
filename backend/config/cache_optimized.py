import os
import redis
import json
import logging
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import threading
import time
from functools import wraps

logger = logging.getLogger(__name__)

class CacheConfig:
    """Cache configuration and management"""
    
    def __init__(self):
        self.redis_url = os.getenv('REDIS_URL')
        self.redis_client = None
        self.fallback_cache = {}
        self.cache_lock = threading.RLock()
        self.default_ttl = int(os.getenv('CACHE_TTL', 300))  # 5 minutes
        self.max_memory_cache_size = int(os.getenv('MAX_MEMORY_CACHE_SIZE', 1000))
        
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection with error handling"""
        if self.redis_url:
            try:
                self.redis_client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                # Test connection
                self.redis_client.ping()
                logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"Redis initialization failed: {e}. Using in-memory cache.")
                self.redis_client = None
        else:
            logger.info("Redis URL not configured. Using in-memory cache.")

class OptimizedCache:
    """Optimized caching system with Redis and in-memory fallback"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
        self.stats_lock = threading.RLock()
    
    def _update_stats(self, operation: str):
        """Update cache statistics"""
        with self.stats_lock:
            self.stats[operation] = self.stats.get(operation, 0) + 1
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for storage"""
        try:
            return json.dumps(value, default=str, separators=(',', ':'))
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            raise
    
    def _deserialize_value(self, value: str) -> Any:
        """Deserialize value from storage"""
        try:
            return json.loads(value)
        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            return None
    
    def _cleanup_memory_cache(self):
        """Clean up expired entries from memory cache"""
        current_time = datetime.now()
        with self.config.cache_lock:
            expired_keys = []
            for key, entry in self.config.fallback_cache.items():
                if isinstance(entry, dict) and 'expires' in entry:
                    if entry['expires'] <= current_time:
                        expired_keys.append(key)
            
            for key in expired_keys:
                del self.config.fallback_cache[key]
            
            # Limit cache size
            if len(self.config.fallback_cache) > self.config.max_memory_cache_size:
                # Remove oldest entries
                sorted_items = sorted(
                    self.config.fallback_cache.items(),
                    key=lambda x: x[1].get('created', datetime.min) if isinstance(x[1], dict) else datetime.min
                )
                excess_count = len(self.config.fallback_cache) - self.config.max_memory_cache_size
                for key, _ in sorted_items[:excess_count]:
                    del self.config.fallback_cache[key]
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            # Try Redis first
            if self.config.redis_client:
                try:
                    value = self.config.redis_client.get(key)
                    if value is not None:
                        self._update_stats('hits')
                        return self._deserialize_value(value)
                except redis.RedisError as e:
                    logger.warning(f"Redis get error: {e}")
                    self._update_stats('errors')
            
            # Fallback to memory cache
            with self.config.cache_lock:
                if key in self.config.fallback_cache:
                    entry = self.config.fallback_cache[key]
                    if isinstance(entry, dict) and 'expires' in entry:
                        if entry['expires'] > datetime.now():
                            self._update_stats('hits')
                            return entry['value']
                        else:
                            del self.config.fallback_cache[key]
                    else:
                        # Legacy entry without expiration
                        self._update_stats('hits')
                        return entry
            
            self._update_stats('misses')
            return None
            
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self._update_stats('errors')
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        if ttl is None:
            ttl = self.config.default_ttl
        
        try:
            serialized_value = self._serialize_value(value)
            
            # Try Redis first
            if self.config.redis_client:
                try:
                    self.config.redis_client.setex(key, ttl, serialized_value)
                    self._update_stats('sets')
                    return True
                except redis.RedisError as e:
                    logger.warning(f"Redis set error: {e}")
                    self._update_stats('errors')
            
            # Fallback to memory cache
            with self.config.cache_lock:
                self.config.fallback_cache[key] = {\n                    'value': value,\n                    'expires': datetime.now() + timedelta(seconds=ttl),\n                    'created': datetime.now()\n                }\n                self._cleanup_memory_cache()\n                self._update_stats('sets')\n                return True\n                \n        except Exception as e:\n            logger.error(f\"Cache set error for key {key}: {e}\")\n            self._update_stats('errors')\n            return False\n    \n    def delete(self, key: str) -> bool:\n        \"\"\"Delete value from cache\"\"\"\n        try:\n            success = False\n            \n            # Try Redis first\n            if self.config.redis_client:\n                try:\n                    result = self.config.redis_client.delete(key)\n                    success = result > 0\n                except redis.RedisError as e:\n                    logger.warning(f\"Redis delete error: {e}\")\n                    self._update_stats('errors')\n            \n            # Also remove from memory cache\n            with self.config.cache_lock:\n                if key in self.config.fallback_cache:\n                    del self.config.fallback_cache[key]\n                    success = True\n            \n            if success:\n                self._update_stats('deletes')\n            return success\n            \n        except Exception as e:\n            logger.error(f\"Cache delete error for key {key}: {e}\")\n            self._update_stats('errors')\n            return False\n    \n    def clear_pattern(self, pattern: str) -> int:\n        \"\"\"Clear cache entries matching pattern\"\"\"\n        deleted_count = 0\n        \n        try:\n            # Clear from Redis\n            if self.config.redis_client:\n                try:\n                    keys = self.config.redis_client.keys(pattern)\n                    if keys:\n                        deleted_count += self.config.redis_client.delete(*keys)\n                except redis.RedisError as e:\n                    logger.warning(f\"Redis pattern delete error: {e}\")\n                    self._update_stats('errors')\n            \n            # Clear from memory cache\n            with self.config.cache_lock:\n                keys_to_delete = [k for k in self.config.fallback_cache.keys() if pattern in k]\n                for key in keys_to_delete:\n                    del self.config.fallback_cache[key]\n                deleted_count += len(keys_to_delete)\n            \n            self._update_stats('deletes')\n            return deleted_count\n            \n        except Exception as e:\n            logger.error(f\"Cache pattern clear error: {e}\")\n            self._update_stats('errors')\n            return 0\n    \n    def exists(self, key: str) -> bool:\n        \"\"\"Check if key exists in cache\"\"\"\n        try:\n            # Check Redis first\n            if self.config.redis_client:\n                try:\n                    return bool(self.config.redis_client.exists(key))\n                except redis.RedisError as e:\n                    logger.warning(f\"Redis exists error: {e}\")\n                    self._update_stats('errors')\n            \n            # Check memory cache\n            with self.config.cache_lock:\n                if key in self.config.fallback_cache:\n                    entry = self.config.fallback_cache[key]\n                    if isinstance(entry, dict) and 'expires' in entry:\n                        if entry['expires'] > datetime.now():\n                            return True\n                        else:\n                            del self.config.fallback_cache[key]\n                    else:\n                        return True\n            \n            return False\n            \n        except Exception as e:\n            logger.error(f\"Cache exists error for key {key}: {e}\")\n            self._update_stats('errors')\n            return False\n    \n    def get_stats(self) -> Dict[str, Any]:\n        \"\"\"Get cache statistics\"\"\"\n        with self.stats_lock:\n            total_requests = self.stats['hits'] + self.stats['misses']\n            hit_rate = (self.stats['hits'] / total_requests) if total_requests > 0 else 0\n            \n            return {\n                'hits': self.stats['hits'],\n                'misses': self.stats['misses'],\n                'sets': self.stats['sets'],\n                'deletes': self.stats['deletes'],\n                'errors': self.stats['errors'],\n                'hit_rate': round(hit_rate, 3),\n                'total_requests': total_requests,\n                'redis_connected': self.config.redis_client is not None,\n                'memory_cache_size': len(self.config.fallback_cache)\n            }\n    \n    def flush_all(self) -> bool:\n        \"\"\"Flush all cache entries\"\"\"\n        try:\n            success = True\n            \n            # Flush Redis\n            if self.config.redis_client:\n                try:\n                    self.config.redis_client.flushdb()\n                except redis.RedisError as e:\n                    logger.warning(f\"Redis flush error: {e}\")\n                    success = False\n                    self._update_stats('errors')\n            \n            # Flush memory cache\n            with self.config.cache_lock:\n                self.config.fallback_cache.clear()\n            \n            return success\n            \n        except Exception as e:\n            logger.error(f\"Cache flush error: {e}\")\n            self._update_stats('errors')\n            return False\n\n# Global cache instance\ncache_config = CacheConfig()\ncache = OptimizedCache(cache_config)\n\n# Cache decorator\ndef cached(ttl: int = 300, key_prefix: str = \"\"):\n    \"\"\"Decorator for caching function results\"\"\"\n    def decorator(func):\n        @wraps(func)\n        def wrapper(*args, **kwargs):\n            # Generate cache key\n            import hashlib\n            key_data = f\"{key_prefix}:{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}\"\n            cache_key = hashlib.md5(key_data.encode()).hexdigest()\n            \n            # Try to get from cache\n            result = cache.get(cache_key)\n            if result is not None:\n                return result\n            \n            # Execute function and cache result\n            result = func(*args, **kwargs)\n            cache.set(cache_key, result, ttl)\n            return result\n        return wrapper\n    return decorator\n\n# Cache warming utilities\nclass CacheWarmer:\n    \"\"\"Utility for warming up cache with frequently accessed data\"\"\"\n    \n    @staticmethod\n    def warm_user_data(user_id: str, supabase_client):\n        \"\"\"Warm cache with user-specific data\"\"\"\n        try:\n            # Cache user profile\n            user_result = supabase_client.table('users').select('*').eq('id', user_id).execute()\n            if user_result.data:\n                cache.set(f\"user:{user_id}\", user_result.data[0], 3600)  # 1 hour\n            \n            # Cache user recipes\n            recipes_result = supabase_client.table('recipes').select('*').eq('user_id', user_id).limit(50).execute()\n            if recipes_result.data:\n                cache.set(f\"user_recipes:{user_id}\", recipes_result.data, 1800)  # 30 minutes\n            \n            logger.info(f\"Cache warmed for user {user_id}\")\n            \n        except Exception as e:\n            logger.error(f\"Cache warming error for user {user_id}: {e}\")\n    \n    @staticmethod\n    def warm_global_data(supabase_client):\n        \"\"\"Warm cache with global data\"\"\"\n        try:\n            # Cache admin recipes\n            admin_recipes = supabase_client.table('admin_recipes').select('*').limit(100).execute()\n            if admin_recipes.data:\n                cache.set(\"admin_recipes\", admin_recipes.data, 3600)  # 1 hour\n            \n            # Cache subscription plans\n            plans = supabase_client.table('subscription_plans').select('*').execute()\n            if plans.data:\n                cache.set(\"subscription_plans\", plans.data, 7200)  # 2 hours\n            \n            logger.info(\"Global cache warmed\")\n            \n        except Exception as e:\n            logger.error(f\"Global cache warming error: {e}\")\n\n# Background cache maintenance\ndef start_cache_maintenance():\n    \"\"\"Start background cache maintenance tasks\"\"\"\n    def maintenance_worker():\n        while True:\n            try:\n                time.sleep(300)  # 5 minutes\n                cache._cleanup_memory_cache()\n                \n                # Log cache stats periodically\n                stats = cache.get_stats()\n                if stats['total_requests'] > 0:\n                    logger.info(f\"Cache stats: {stats}\")\n                    \n            except Exception as e:\n                logger.error(f\"Cache maintenance error: {e}\")\n    \n    maintenance_thread = threading.Thread(target=maintenance_worker, daemon=True)\n    maintenance_thread.start()\n    logger.info(\"Cache maintenance started\")\n\n# Start maintenance on import\nstart_cache_maintenance()