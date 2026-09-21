"""
Enhanced LLM Cache with Redis Support
Production-ready caching with dual backend (memory + Redis)
"""
import hashlib
import json
from typing import Optional, Dict
from datetime import datetime, timedelta
from app.config.redis_config import get_redis_client

# In-memory cache fallback
_memory_cache: Dict[str, tuple] = {}

# Cache TTL
CACHE_TTL_SECONDS = 86400  # 24 hours


def _get_cache_key(prompt: str, model: str, task_type: str) -> str:
    """Generate cache key from prompt and metadata"""
    key_string = f"{prompt}|{model}|{task_type}"
    return hashlib.sha256(key_string.encode()).hexdigest()


def get_cached_response(prompt: str, model: str, task_type: str) -> Optional[str]:
    """
    Get cached LLM response
    
    Tries Redis first, falls back to memory cache
    Returns cached response if found and not expired, None otherwise
    """
    cache_key = _get_cache_key(prompt, model, task_type)
    
    # Try Redis first (if available)
    redis_client = get_redis_client()
    if redis_client:
        try:
            cached_data = redis_client.get(f"llm_cache:{cache_key}")
            if cached_data:
                data = json.loads(cached_data)
                return data["response"]
        except Exception as e:
            print(f"[WARNING] Redis cache read error: {e}")
    
    # Fall back to memory cache
    if cache_key in _memory_cache:
        response, timestamp = _memory_cache[cache_key]
        if datetime.utcnow() - timestamp < timedelta(seconds=CACHE_TTL_SECONDS):
            return response
        else:
            # Expired - remove
            del _memory_cache[cache_key]
    
    return None


def cache_response(prompt: str, model: str, task_type: str, response: str):
    """
    Cache LLM response
    
    Stores in both Redis (if available) and memory for redundancy
    """
    cache_key = _get_cache_key(prompt, model, task_type)
    
    # Store in Redis (if available)
    redis_client = get_redis_client()
    if redis_client:
        try:
            cache_data = {
                "response": response,
                "timestamp": datetime.utcnow().isoformat(),
                "model": model,
                "task_type": task_type
            }
            redis_client.setex(
                f"llm_cache:{cache_key}",
                CACHE_TTL_SECONDS,
                json.dumps(cache_data)
            )
        except Exception as e:
            print(f"[WARNING] Redis cache write error: {e}")
    
    # Always store in memory as backup
    _memory_cache[cache_key] = (response, datetime.utcnow())


def clear_cache():
    """Clear all cached responses from both backends"""
    global _memory_cache
    
    # Clear Redis
    redis_client = get_redis_client()
    if redis_client:
        try:
            keys = redis_client.keys("llm_cache:*")
            if keys:
                redis_client.delete(*keys)
                print(f"[SUCCESS] Cleared {len(keys)} Redis cache entries")
        except Exception as e:
            print(f"[WARNING] Redis cache clear error: {e}")
    
    # Clear memory
    _memory_cache = {}
    print("[SUCCESS] Cleared memory cache")


def get_cache_stats() -> dict:
    """Get cache statistics from both backends"""
    stats = {
        "memory_entries": len(_memory_cache),
        "redis_enabled": get_redis_client() is not None,
        "redis_entries": 0
    }
    
    # Get Redis stats
    redis_client = get_redis_client()
    if redis_client:
        try:
            keys = redis_client.keys("llm_cache:*")
            stats["redis_entries"] = len(keys)
        except Exception:
            stats["redis_entries"] = 0
    
    return stats
