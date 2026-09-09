"""
Base parser interface for vendor-specific parsers
"""
from abc import ABC, abstractmethod
from typing import Optional

from app.normalization.schema import UnifiedSecurityModel


class BaseParser(ABC):
    """
    Base interface for configuration parsers
    
    Each vendor parser implements this interface to convert
    vendor-specific syntax into the Unified Security Model
    """
    
    @abstractmethod
    def can_parse(self, content: str) -> bool:
        """
        Determine if this parser can handle the configuration
        
        Args:
            content: Configuration file content
            
        Returns:
            True if parser can handle this configuration
        """
        pass
    
    @abstractmethod
    def parse(self, content: str, filename: str) -> UnifiedSecurityModel:
        """
        Parse configuration into Unified Security Model
        
        Args:
            content: Configuration file content
            filename: Original filename for evidence tracking
            
        Returns:
            UnifiedSecurityModel with extracted security settings
            
        Raises:
            ParserError: If parsing fails
        """
        pass
    
    @property
    @abstractmethod
    def vendor_name(self) -> str:
        """Return vendor name"""
        pass


class ParserError(Exception):
    """Exception raised when parsing fails"""
    pass
