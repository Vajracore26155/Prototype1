"""
Redis Configuration
Optional: For production caching and cost tracking persistence
"""
import os
from typing import Optional
import redis
from dotenv import load_dotenv

load_dotenv()

# Redis configuration
REDIS_ENABLED = os.getenv("REDIS_ENABLED", "false").lower() == "true"
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Global Redis client
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    """
    Get Redis client if enabled
    
    Returns None if Redis is not enabled or connection fails
    """
    global _redis_client
    
    if not REDIS_ENABLED:
        return None
    
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(
                REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            _redis_client.ping()
            print("[SUCCESS] Redis connected successfully")
        except Exception as e:
            print(f"[WARNING] Redis connection failed: {str(e)}")
            print("  Falling back to in-memory storage")
            _redis_client = None
    
    return _redis_client


def close_redis():
    """Close Redis connection"""
    global _redis_client
    if _redis_client:
        _redis_client.close()
        _redis_client = None
