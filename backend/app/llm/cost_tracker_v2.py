"""
Enhanced LLM Cost Tracker with Redis Persistence
Production-ready cost tracking and limit enforcement
"""
import json
from typing import Dict, Optional
from datetime import datetime
from app.config.redis_config import get_redis_client

# Cost limits
USER_MONTHLY_LIMIT = 10.0  # $10/user/month
ORG_MONTHLY_LIMIT = 1000.0  # $1000/org/month
SINGLE_REQUEST_LIMIT = 1.0  # $1/request

# In-memory fallback
_memory_usage: Dict[str, Dict] = {}


def _get_month_key() -> str:
    """Get current month key for tracking"""
    return datetime.utcnow().strftime("%Y-%m")


def track_usage(
    user_id: int,
    organization_id: int,
    provider: str,
    model: str,
    cost: float
):
    """
    Track LLM usage and cost
    
    Stores in Redis if available, otherwise in memory
    """
    month_key = _get_month_key()
    
    # User tracking
    user_key = f"llm_cost:user:{user_id}:{month_key}"
    org_key = f"llm_cost:org:{organization_id}:{month_key}"
    
    redis_client = get_redis_client()
    if redis_client:
        try:
            # Increment user cost
            redis_client.hincrbyfloat(user_key, "total", cost)
            redis_client.hincrbyfloat(user_key, f"provider:{provider}", cost)
            redis_client.hincrby(user_key, "requests", 1)
            redis_client.expire(user_key, 90 * 24 * 3600)  # 90 days
            
            # Increment org cost
            redis_client.hincrbyfloat(org_key, "total", cost)
            redis_client.hincrbyfloat(org_key, f"provider:{provider}", cost)
            redis_client.hincrby(org_key, "requests", 1)
            redis_client.expire(org_key, 90 * 24 * 3600)
        except Exception as e:
            print(f"[WARNING] Redis cost tracking error: {e}")
            # Fall through to memory tracking
    
    # Memory tracking (always as backup)
    if user_key not in _memory_usage:
        _memory_usage[user_key] = {"total": 0.0, "requests": 0, "providers": {}}
    if org_key not in _memory_usage:
        _memory_usage[org_key] = {"total": 0.0, "requests": 0, "providers": {}}
    
    _memory_usage[user_key]["total"] += cost
    _memory_usage[user_key]["requests"] += 1
    _memory_usage[user_key]["providers"][provider] = \
        _memory_usage[user_key]["providers"].get(provider, 0.0) + cost
    
    _memory_usage[org_key]["total"] += cost
    _memory_usage[org_key]["requests"] += 1
    _memory_usage[org_key]["providers"][provider] = \
        _memory_usage[org_key]["providers"].get(provider, 0.0) + cost


def get_user_usage(user_id: int) -> Dict:
    """Get user usage statistics for current month"""
    month_key = _get_month_key()
    user_key = f"llm_cost:user:{user_id}:{month_key}"
    
    redis_client = get_redis_client()
    if redis_client:
        try:
            data = redis_client.hgetall(user_key)
            if data:
                # Parse Redis data
                total_cost = float(data.get("total", 0))
                requests = int(data.get("requests", 0))
                
                # Extract provider costs
                providers = {}
                for key, value in data.items():
                    if key.startswith("provider:"):
                        provider_name = key.split(":", 1)[1]
                        providers[provider_name] = float(value)
                
                return {
                    "total_cost": total_cost,
                    "requests": requests,
                    "providers": providers,
                    "limit": USER_MONTHLY_LIMIT,
                    "remaining": max(0, USER_MONTHLY_LIMIT - total_cost)
                }
        except Exception as e:
            print(f"[WARNING] Redis usage read error: {e}")
    
    # Fall back to memory
    if user_key in _memory_usage:
        data = _memory_usage[user_key]
        return {
            "total_cost": data["total"],
            "requests": data["requests"],
            "providers": data["providers"],
            "limit": USER_MONTHLY_LIMIT,
            "remaining": max(0, USER_MONTHLY_LIMIT - data["total"])
        }
    
    return {
        "total_cost": 0.0,
        "requests": 0,
        "providers": {},
        "limit": USER_MONTHLY_LIMIT,
        "remaining": USER_MONTHLY_LIMIT
    }


def get_org_usage(organization_id: int) -> Dict:
    """Get organization usage statistics for current month"""
    month_key = _get_month_key()
    org_key = f"llm_cost:org:{organization_id}:{month_key}"
    
    redis_client = get_redis_client()
    if redis_client:
        try:
            data = redis_client.hgetall(org_key)
            if data:
                total_cost = float(data.get("total", 0))
                requests = int(data.get("requests", 0))
                
                providers = {}
                for key, value in data.items():
                    if key.startswith("provider:"):
                        provider_name = key.split(":", 1)[1]
                        providers[provider_name] = float(value)
                
                return {
                    "total_cost": total_cost,
                    "requests": requests,
                    "providers": providers,
                    "limit": ORG_MONTHLY_LIMIT,
                    "remaining": max(0, ORG_MONTHLY_LIMIT - total_cost)
                }
        except Exception as e:
            print(f"[WARNING] Redis usage read error: {e}")
    
    # Fall back to memory
    if org_key in _memory_usage:
        data = _memory_usage[org_key]
        return {
            "total_cost": data["total"],
            "requests": data["requests"],
            "providers": data["providers"],
            "limit": ORG_MONTHLY_LIMIT,
            "remaining": max(0, ORG_MONTHLY_LIMIT - data["total"])
        }
    
    return {
        "total_cost": 0.0,
        "requests": 0,
        "providers": {},
        "limit": ORG_MONTHLY_LIMIT,
        "remaining": ORG_MONTHLY_LIMIT
    }


def check_cost_limit(
    user_id: int,
    organization_id: int,
    estimated_cost: float
) -> tuple[bool, Optional[str]]:
    """
    Check if request would exceed cost limits
    
    Returns (allowed, reason)
    """
    # Check single request limit
    if estimated_cost > SINGLE_REQUEST_LIMIT:
        return False, f"Request cost ${estimated_cost:.4f} exceeds single request limit of ${SINGLE_REQUEST_LIMIT}"
    
    # Check user limit
    user_usage = get_user_usage(user_id)
    if user_usage["total_cost"] + estimated_cost > USER_MONTHLY_LIMIT:
        return False, f"User monthly limit of ${USER_MONTHLY_LIMIT} would be exceeded (current: ${user_usage['total_cost']:.2f})"
    
    # Check org limit
    org_usage = get_org_usage(organization_id)
    if org_usage["total_cost"] + estimated_cost > ORG_MONTHLY_LIMIT:
        return False, f"Organization monthly limit of ${ORG_MONTHLY_LIMIT} would be exceeded (current: ${org_usage['total_cost']:.2f})"
    
    return True, None
