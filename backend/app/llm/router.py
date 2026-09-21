"""
LLM Router - Intelligent model selection
Phase 6: Route requests to optimal LLM
"""
import os
from typing import Dict, Optional
from enum import Enum

from app.llm.providers import (
    BaseLLMProvider, OpenAIProvider, ClaudeProvider, 
    GeminiProvider, MockLLMProvider, LLMResponse
)
from app.llm.cache import LLMCache


class TaskType(str, Enum):
    """LLM task types"""
    QUERY = "query"  # Natural language queries
    REMEDIATION = "remediation"  # Remediation suggestions
    ANALYSIS = "analysis"  # Configuration analysis
    GENERATION = "generation"  # Configuration generation
    CATEGORIZATION = "categorization"  # Finding categorization


class LLMRouter:
    """
    Intelligent LLM router
    
    Selects optimal model based on:
    - Task type
    - Cost constraints
    - Response quality requirements
    - Availability
    """
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.cache = LLMCache()
        self.default_provider = "mock"
        
        # Initialize providers if API keys available
        self._init_providers()
    
    def _init_providers(self):
        """Initialize available LLM providers"""
        # OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.providers["openai"] = OpenAIProvider(openai_key)
            self.default_provider = "openai"
        
        # Claude
        claude_key = os.getenv("ANTHROPIC_API_KEY")
        if claude_key:
            self.providers["claude"] = ClaudeProvider(claude_key)
            if self.default_provider == "mock":
                self.default_provider = "claude"
        
        # Gemini
        gemini_key = os.getenv("GOOGLE_API_KEY")
        if gemini_key:
            self.providers["gemini"] = GeminiProvider(gemini_key)
            if self.default_provider == "mock":
                self.default_provider = "gemini"
        
        # Always have mock provider as fallback
        self.providers["mock"] = MockLLMProvider("mock")
    
    def select_provider(self, task_type: TaskType, prefer_quality: bool = False) -> str:
        """
        Select optimal provider for task
        
        Args:
            task_type: Type of task
            prefer_quality: Prefer quality over cost
            
        Returns:
            Provider name
        """
        # Task-specific provider selection
        if task_type == TaskType.REMEDIATION and prefer_quality:
            # Use best model for critical remediation
            if "openai" in self.providers:
                return "openai"
            elif "claude" in self.providers:
                return "claude"
        
        elif task_type == TaskType.QUERY:
            # Use fast/cheap model for queries
            if "gemini" in self.providers:
                return "gemini"
            elif "openai" in self.providers:
                return "openai"
        
        elif task_type == TaskType.ANALYSIS:
            # Use balanced model
            if "claude" in self.providers:
                return "claude"
            elif "openai" in self.providers:
                return "openai"
        
        # Default to available provider
        return self.default_provider
    
    async def complete(
        self, 
        prompt: str, 
        task_type: TaskType = TaskType.QUERY,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1000,
        use_cache: bool = True
    ) -> LLMResponse:
        """
        Generate LLM completion with intelligent routing
        
        Args:
            prompt: Input prompt
            task_type: Type of task
            provider: Specific provider (optional, auto-select if None)
            model: Specific model (optional)
            max_tokens: Max response tokens
            use_cache: Use cached responses
            
        Returns:
            LLMResponse
        """
        # Check cache first
        if use_cache:
            cached = self.cache.get(prompt, provider, model)
            if cached:
                cached.cached = True
                return cached
        
        # Select provider if not specified
        if not provider:
            provider = self.select_provider(task_type)
        
        # Get provider instance
        if provider not in self.providers:
            provider = self.default_provider
        
        llm_provider = self.providers[provider]
        
        # Select default model if not specified
        if not model:
            model = self._get_default_model(provider)
        
        # Generate completion
        response = await llm_provider.complete(prompt, model, max_tokens)
        
        # Cache response
        if use_cache:
            self.cache.set(prompt, response, provider, model)
        
        return response
    
    def _get_default_model(self, provider: str) -> str:
        """Get default model for provider"""
        defaults = {
            "openai": "gpt-4-turbo",
            "claude": "claude-3-sonnet",
            "gemini": "gemini-pro",
            "mock": "mock"
        }
        return defaults.get(provider, "mock")
    
    def get_available_providers(self) -> list:
        """Get list of available providers"""
        return [p for p in self.providers.keys() if p != "mock"]


# Global router instance
_router_instance: Optional[LLMRouter] = None


def get_llm_router() -> LLMRouter:
    """Get global LLM router instance"""
    global _router_instance
    if _router_instance is None:
        _router_instance = LLMRouter()
    return _router_instance
