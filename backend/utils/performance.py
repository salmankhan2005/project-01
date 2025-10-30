import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)

def cache_result(ttl: int = 300, key_prefix: str = ""):
    """Simple cache decorator"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # For now, just execute the function without caching
            return func(*args, **kwargs)
        return wrapper
    return decorator

def measure_time(func: Callable) -> Callable:
    """Measure execution time decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        logger.debug(f"{func.__name__} executed in {execution_time:.3f}s")
        return result
    return wrapper

class QueryOptimizer:
    """Simple query optimization utilities"""
    
    @staticmethod
    def get_pagination_params(request, max_per_page: int = 100):
        """Extract pagination parameters"""
        try:
            page = max(1, int(request.args.get('page', 1)))
            per_page = min(max_per_page, max(1, int(request.args.get('per_page', 20))))
            offset = (page - 1) * per_page
            return page, per_page, offset
        except (ValueError, TypeError):
            return 1, 20, 0