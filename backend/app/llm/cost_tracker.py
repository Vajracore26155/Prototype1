"""
LLM Cost Tracking
Phase 6: Track and limit API costs
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from sqlalchemy.orm import Session

from app.database import Organization, User


@dataclass
class CostLimit:
    """Cost limit configuration"""
    user_monthly_limit: float = 10.0  # $10 per user per month
    org_monthly_limit: float = 1000.0  # $1000 per org per month
    single_request_limit: float = 1.0  # $1 per single request


class CostTracker:
    """
    Track LLM API costs and enforce limits
    """
    
    def __init__(self):
        self.limits = CostLimit()
        self.usage = {}  # In-memory tracking (use database in production)
    
    def track_usage(
        self,
        user_id: int,
        organization_id: int,
        provider: str,
        model: str,
        tokens: int,
        cost: float
    ):
        """
        Track API usage
        
        Args:
            user_id: User ID
            organization_id: Organization ID
            provider: LLM provider
            model: Model used
            tokens: Tokens consumed
            cost: Cost in USD
        """
        month_key = datetime.utcnow().strftime("%Y-%m")
        
        # Track user usage
        user_key = f"user:{user_id}:{month_key}"
        if user_key not in self.usage:
            self.usage[user_key] = {
                "total_cost": 0.0,
                "total_tokens": 0,
                "requests": 0,
                "by_provider": {}
            }
        
        self.usage[user_key]["total_cost"] += cost
        self.usage[user_key]["total_tokens"] += tokens
        self.usage[user_key]["requests"] += 1
        
        if provider not in self.usage[user_key]["by_provider"]:
            self.usage[user_key]["by_provider"][provider] = {
                "cost": 0.0,
                "tokens": 0,
                "requests": 0
            }
        
        self.usage[user_key]["by_provider"][provider]["cost"] += cost
        self.usage[user_key]["by_provider"][provider]["tokens"] += tokens
        self.usage[user_key]["by_provider"][provider]["requests"] += 1
        
        # Track organization usage
        org_key = f"org:{organization_id}:{month_key}"
        if org_key not in self.usage:
            self.usage[org_key] = {
                "total_cost": 0.0,
                "total_tokens": 0,
                "requests": 0,
                "by_provider": {}
            }
        
        self.usage[org_key]["total_cost"] += cost
        self.usage[org_key]["total_tokens"] += tokens
        self.usage[org_key]["requests"] += 1
        
        if provider not in self.usage[org_key]["by_provider"]:
            self.usage[org_key]["by_provider"][provider] = {
                "cost": 0.0,
                "tokens": 0,
                "requests": 0
            }
        
        self.usage[org_key]["by_provider"][provider]["cost"] += cost
        self.usage[org_key]["by_provider"][provider]["tokens"] += tokens
        self.usage[org_key]["by_provider"][provider]["requests"] += 1
    
    def check_limits(
        self,
        user_id: int,
        organization_id: int,
        estimated_cost: float
    ) -> tuple[bool, Optional[str]]:
        """
        Check if request would exceed limits
        
        Returns:
            (allowed, reason)
        """
        month_key = datetime.utcnow().strftime("%Y-%m")
        
        # Check single request limit
        if estimated_cost > self.limits.single_request_limit:
            return False, f"Request cost ${estimated_cost:.2f} exceeds single request limit ${self.limits.single_request_limit:.2f}"
        
        # Check user monthly limit
        user_key = f"user:{user_id}:{month_key}"
        if user_key in self.usage:
            user_total = self.usage[user_key]["total_cost"]
            if user_total + estimated_cost > self.limits.user_monthly_limit:
                return False, f"User monthly limit ${self.limits.user_monthly_limit:.2f} would be exceeded"
        
        # Check organization monthly limit
        org_key = f"org:{organization_id}:{month_key}"
        if org_key in self.usage:
            org_total = self.usage[org_key]["total_cost"]
            if org_total + estimated_cost > self.limits.org_monthly_limit:
                return False, f"Organization monthly limit ${self.limits.org_monthly_limit:.2f} would be exceeded"
        
        return True, None
    
    def get_user_usage(self, user_id: int) -> Dict:
        """Get user usage stats"""
        month_key = datetime.utcnow().strftime("%Y-%m")
        user_key = f"user:{user_id}:{month_key}"
        
        if user_key in self.usage:
            usage = self.usage[user_key]
            return {
                "month": month_key,
                "total_cost": round(usage["total_cost"], 2),
                "total_tokens": usage["total_tokens"],
                "requests": usage["requests"],
                "by_provider": usage["by_provider"],
                "limit": self.limits.user_monthly_limit,
                "remaining": round(self.limits.user_monthly_limit - usage["total_cost"], 2)
            }
        
        return {
            "month": month_key,
            "total_cost": 0.0,
            "total_tokens": 0,
            "requests": 0,
            "by_provider": {},
            "limit": self.limits.user_monthly_limit,
            "remaining": self.limits.user_monthly_limit
        }
    
    def get_organization_usage(self, organization_id: int) -> Dict:
        """Get organization usage stats"""
        month_key = datetime.utcnow().strftime("%Y-%m")
        org_key = f"org:{organization_id}:{month_key}"
        
        if org_key in self.usage:
            usage = self.usage[org_key]
            return {
                "month": month_key,
                "total_cost": round(usage["total_cost"], 2),
                "total_tokens": usage["total_tokens"],
                "requests": usage["requests"],
                "by_provider": usage["by_provider"],
                "limit": self.limits.org_monthly_limit,
                "remaining": round(self.limits.org_monthly_limit - usage["total_cost"], 2)
            }
        
        return {
            "month": month_key,
            "total_cost": 0.0,
            "total_tokens": 0,
            "requests": 0,
            "by_provider": {},
            "limit": self.limits.org_monthly_limit,
            "remaining": self.limits.org_monthly_limit
        }


# Global cost tracker instance
_cost_tracker_instance: Optional[CostTracker] = None


def get_cost_tracker() -> CostTracker:
    """Get global cost tracker instance"""
    global _cost_tracker_instance
    if _cost_tracker_instance is None:
        _cost_tracker_instance = CostTracker()
    return _cost_tracker_instance
