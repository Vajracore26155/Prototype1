"""
LLM Response Cache
Phase 6: Cache LLM responses to reduce costs
"""
import hashlib
import json
from typing import Optional
from datetime import datetime, timedelta

from app.llm.providers import LLMResponse


class LLMCache:
    """
    In-memory cache for LLM responses
    
    In production, use Redis for distributed caching
    """
    
    def __init__(self, ttl_hours: int = 24):
        self.cache = {}
        self.ttl = timedelta(hours=ttl_hours)
    
    def _generate_key(self, prompt: str, provider: Optional[str], model: Optional[str]) -> str:
        """Generate cache key"""
        key_data = f"{prompt}:{provider}:{model}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def get(self, prompt: str, provider: Optional[str] = None, model: Optional[str] = None) -> Optional[LLMResponse]:
        """Get cached response"""
        key = self._generate_key(prompt, provider, model)
        
        if key in self.cache:
            entry = self.cache[key]
            
            # Check if expired
            if datetime.utcnow() - entry["timestamp"] > self.ttl:
                del self.cache[key]
                return None
            
            return entry["response"]
        
        return None
    
    def set(self, prompt: str, response: LLMResponse, provider: Optional[str] = None, model: Optional[str] = None):
        """Cache response"""
        key = self._generate_key(prompt, provider, model)
        
        self.cache[key] = {
            "response": response,
            "timestamp": datetime.utcnow()
        }
    
    def clear(self):
        """Clear all cache"""
        self.cache = {}
    
    def size(self) -> int:
        """Get cache size"""
        return len(self.cache)
