"""
LLM Provider Implementations
Phase 6: OpenAI, Claude, Gemini
"""
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """LLM response wrapper"""
    content: str
    model: str
    tokens_used: int
    cost: float
    provider: str
    cached: bool = False


class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    @abstractmethod
    async def complete(self, prompt: str, model: str, max_tokens: int = 1000) -> LLMResponse:
        """Generate completion"""
        pass
    
    @abstractmethod
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate API cost"""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT-4 provider"""
    
    # Pricing per 1K tokens (as of Dec 2024)
    PRICING = {
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
    }
    
    async def complete(self, prompt: str, model: str = "gpt-4-turbo", max_tokens: int = 1000) -> LLMResponse:
        """
        Generate completion using OpenAI API
        """
        try:
            import openai
            
            client = openai.AsyncOpenAI(api_key=self.api_key)
            
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a network security expert assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            cost = self.calculate_cost(tokens_used, model)
            
            return LLMResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                cost=cost,
                provider="openai"
            )
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate OpenAI API cost"""
        pricing = self.PRICING.get(model, self.PRICING["gpt-4"])
        # Simplified: assume 50/50 input/output split
        cost = (tokens / 2000) * (pricing["input"] + pricing["output"])
        return round(cost, 6)


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude provider"""
    
    # Pricing per 1K tokens
    PRICING = {
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125}
    }
    
    async def complete(self, prompt: str, model: str = "claude-3-sonnet", max_tokens: int = 1000) -> LLMResponse:
        """
        Generate completion using Claude API
        """
        try:
            import anthropic
            
            client = anthropic.AsyncAnthropic(api_key=self.api_key)
            
            response = await client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            cost = self.calculate_cost(tokens_used, model)
            
            return LLMResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                cost=cost,
                provider="claude"
            )
            
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")
    
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate Claude API cost"""
        pricing = self.PRICING.get(model, self.PRICING["claude-3-sonnet"])
        cost = (tokens / 2000) * (pricing["input"] + pricing["output"])
        return round(cost, 6)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider"""
    
    # Pricing per 1K tokens
    PRICING = {
        "gemini-pro": {"input": 0.00025, "output": 0.0005},
        "gemini-pro-vision": {"input": 0.00025, "output": 0.0005}
    }
    
    async def complete(self, prompt: str, model: str = "gemini-pro", max_tokens: int = 1000) -> LLMResponse:
        """
        Generate completion using Gemini API
        """
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model_instance = genai.GenerativeModel(model)
            
            response = model_instance.generate_content(prompt)
            
            content = response.text
            # Gemini doesn't provide token counts in all responses
            tokens_used = len(prompt.split()) + len(content.split())  # Rough estimate
            cost = self.calculate_cost(tokens_used, model)
            
            return LLMResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                cost=cost,
                provider="gemini"
            )
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate Gemini API cost"""
        pricing = self.PRICING.get(model, self.PRICING["gemini-pro"])
        cost = (tokens / 2000) * (pricing["input"] + pricing["output"])
        return round(cost, 6)


class MockLLMProvider(BaseLLMProvider):
    """Mock provider for testing (no API calls)"""
    
    async def complete(self, prompt: str, model: str = "mock", max_tokens: int = 1000) -> LLMResponse:
        """Generate mock completion"""
        content = f"Mock response for: {prompt[:50]}..."
        
        return LLMResponse(
            content=content,
            model=model,
            tokens_used=100,
            cost=0.001,
            provider="mock"
        )
    
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Calculate mock cost"""
        return 0.001


def get_available_providers() -> list:
    """Get list of available LLM providers"""
    providers = []
    
    # Check for API keys
    if os.getenv("OPENAI_API_KEY"):
        providers.append("openai")
    
    if os.getenv("ANTHROPIC_API_KEY"):
        providers.append("anthropic")
    
    if os.getenv("GOOGLE_API_KEY"):
        providers.append("gemini")
    
    # Mock is always available
    providers.append("mock")
    
    return providers
