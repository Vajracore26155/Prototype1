"""
Input Validation & Sanitization
Phase 8: Security hardening
"""
import re
from typing import Any, Optional
from fastapi import HTTPException
import bleach


class InputValidator:
    """
    Comprehensive input validation
    
    Protects against injection attacks, XSS, path traversal, etc.
    """
    
    # Validation patterns
    PATTERNS = {
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "username": r"^[a-zA-Z0-9_-]{3,32}$",
        "device_id": r"^DEV-[A-Z0-9]{6,12}$",
        "audit_id": r"^AUD-[0-9]{6,12}$",
        "config_id": r"^CFG-[0-9]{6,12}$",
        "finding_id": r"^FND-[0-9]{6,12}$",
        "ip_address": r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$",
        "hostname": r"^[a-zA-Z0-9][a-zA-Z0-9-]{0,62}[a-zA-Z0-9]?$",
        "alphanumeric": r"^[a-zA-Z0-9]+$"
    }
    
    # Dangerous patterns (SQL injection, command injection, etc.)
    DANGEROUS_PATTERNS = [
        r"(\bor\b|\band\b).*?=.*?=",  # SQL injection
        r"union.*?select",  # SQL union
        r"exec\s*\(",  # Code execution
        r"eval\s*\(",  # Code execution
        r"<script",  # XSS
        r"javascript:",  # XSS
        r"\.\./",  # Path traversal
        r"cmd\.exe",  # Command execution
        r"bash\s+-c",  # Command execution
    ]
    
    @classmethod
    def validate_pattern(cls, value: str, pattern_name: str) -> bool:
        """Validate string matches pattern"""
        if pattern_name not in cls.PATTERNS:
            raise ValueError(f"Unknown pattern: {pattern_name}")
        
        pattern = cls.PATTERNS[pattern_name]
        return bool(re.match(pattern, value, re.IGNORECASE))
    
    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validate and sanitize email"""
        email = email.strip().lower()
        
        if not cls.validate_pattern(email, "email"):
            raise HTTPException(
                status_code=400,
                detail="Invalid email format"
            )
        
        if len(email) > 255:
            raise HTTPException(
                status_code=400,
                detail="Email too long"
            )
        
        return email
    
    @classmethod
    def validate_username(cls, username: str) -> str:
        """Validate and sanitize username"""
        username = username.strip()
        
        if not cls.validate_pattern(username, "username"):
            raise HTTPException(
                status_code=400,
                detail="Username must be 3-32 characters, alphanumeric, dash, or underscore"
            )
        
        return username
    
    @classmethod
    def validate_ip_address(cls, ip: str) -> str:
        """Validate IP address"""
        ip = ip.strip()
        
        if not cls.validate_pattern(ip, "ip_address"):
            raise HTTPException(
                status_code=400,
                detail="Invalid IP address format"
            )
        
        # Check each octet is 0-255
        octets = ip.split(".")
        for octet in octets:
            if int(octet) > 255:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid IP address"
                )
        
        return ip
    
    @classmethod
    def sanitize_html(cls, text: str) -> str:
        """
        Sanitize HTML content
        
        Removes dangerous tags and attributes
        """
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li', 'code', 'pre']
        allowed_attributes = {}
        
        return bleach.clean(
            text,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
    
    @classmethod
    def check_dangerous_patterns(cls, text: str) -> bool:
        """
        Check for dangerous injection patterns
        
        Returns True if dangerous patterns found
        """
        text_lower = text.lower()
        
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return True
        
        return False
    
    @classmethod
    def validate_safe_string(cls, text: str, field_name: str = "input") -> str:
        """
        Validate string is safe (no injection attempts)
        """
        if cls.check_dangerous_patterns(text):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid {field_name}: potentially dangerous content detected"
            )
        
        return text
    
    @classmethod
    def validate_filename(cls, filename: str) -> str:
        """
        Validate and sanitize filename
        
        Prevents path traversal and dangerous extensions
        """
        # Remove any path components
        filename = filename.split("/")[-1].split("\\")[-1]
        
        # Check for path traversal
        if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
            raise HTTPException(
                status_code=400,
                detail="Invalid filename: path traversal detected"
            )
        
        # Check length
        if len(filename) > 255:
            raise HTTPException(
                status_code=400,
                detail="Filename too long"
            )
        
        # Check for null bytes
        if "\x00" in filename:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename: null byte detected"
            )
        
        # Validate extension
        allowed_extensions = ['.cfg', '.conf', '.txt', '.json', '.xml']
        ext = filename[filename.rfind('.'):].lower() if '.' in filename else ''
        
        if ext and ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension: {ext}"
            )
        
        return filename
    
    @classmethod
    def validate_json_keys(cls, data: dict, allowed_keys: set) -> dict:
        """
        Validate JSON object only contains allowed keys
        
        Prevents mass assignment vulnerabilities
        """
        provided_keys = set(data.keys())
        invalid_keys = provided_keys - allowed_keys
        
        if invalid_keys:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid fields: {', '.join(invalid_keys)}"
            )
        
        return data
    
    @classmethod
    def validate_string_length(
        cls,
        text: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        field_name: str = "input"
    ) -> str:
        """Validate string length"""
        length = len(text)
        
        if min_length and length < min_length:
            raise HTTPException(
                status_code=400,
                detail=f"{field_name} must be at least {min_length} characters"
            )
        
        if max_length and length > max_length:
            raise HTTPException(
                status_code=400,
                detail=f"{field_name} must be at most {max_length} characters"
            )
        
        return text
    
    @classmethod
    def validate_integer_range(
        cls,
        value: int,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        field_name: str = "value"
    ) -> int:
        """Validate integer is within range"""
        if min_value is not None and value < min_value:
            raise HTTPException(
                status_code=400,
                detail=f"{field_name} must be at least {min_value}"
            )
        
        if max_value is not None and value > max_value:
            raise HTTPException(
                status_code=400,
                detail=f"{field_name} must be at most {max_value}"
            )
        
        return value


# Convenience functions
def validate_id(id_value: str, id_type: str) -> str:
    """Validate entity ID format"""
    pattern_map = {
        "device": "device_id",
        "audit": "audit_id",
        "config": "config_id",
        "finding": "finding_id"
    }
    
    pattern_name = pattern_map.get(id_type)
    if not pattern_name:
        raise ValueError(f"Unknown ID type: {id_type}")
    
    if not InputValidator.validate_pattern(id_value, pattern_name):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {id_type} ID format"
        )
    
    return id_value
