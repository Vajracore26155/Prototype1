"""
Secret Masking Engine
Detects and masks sensitive information in network configurations
"""
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class MaskingResult:
    """Result of masking operation"""
    sanitized_content: str
    masked_count: int
    masked_types: List[str]
    original_hash: str  # For verification purposes


class SecretMasker:
    """
    Detects and masks common network secrets without destroying original file
    
    Supports:
    - Passwords (Cisco, generic)
    - Enable secrets
    - SNMP community strings
    - API keys
    - Private keys (RSA, certificate blocks)
    - Pre-shared keys
    - Tokens
    """
    
    def __init__(self):
        self.patterns = self._build_patterns()
    
    def _build_patterns(self) -> List[Tuple[str, str, str]]:
        """
        Build list of (pattern, replacement, secret_type) tuples
        Order matters - more specific patterns first
        """
        return [
            # Private key blocks (match entire block)
            (
                r'-----BEGIN[A-Z\s]+PRIVATE KEY-----.*?-----END[A-Z\s]+PRIVATE KEY-----',
                '[PRIVATE_KEY_REDACTED]',
                'private_key'
            ),
            (
                r'-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----',
                '[CERTIFICATE_REDACTED]',
                'certificate'
            ),
            
            # Cisco passwords and secrets
            (
                r'(username\s+\S+\s+(?:password|secret)(?:\s+\d+)?\s+)(\S+)',
                r'\1[REDACTED]',
                'cisco_user_password'
            ),
            (
                r'(enable\s+(?:password|secret)(?:\s+\d+)?\s+)(\S+)',
                r'\1[REDACTED]',
                'enable_secret'
            ),
            (
                r'(password\s+(?:\d+\s+)?)(\S+)',
                r'\1[REDACTED]',
                'password'
            ),
            (
                r'(secret\s+(?:\d+\s+)?)(\S+)',
                r'\1[REDACTED]',
                'secret'
            ),
            
            # SNMP community strings
            (
                r'(snmp-server\s+community\s+)(\S+)',
                r'\1[REDACTED]',
                'snmp_community'
            ),
            (
                r'(community\s+)(\S+)',
                r'\1[REDACTED]',
                'snmp_community'
            ),
            
            # Pre-shared keys
            (
                r'(preshared-key\s+)(\S+)',
                r'\1[REDACTED]',
                'preshared_key'
            ),
            (
                r'(pre-shared-key\s+)(\S+)',
                r'\1[REDACTED]',
                'preshared_key'
            ),
            
            # API keys and tokens
            (
                r'(api[-_]?key["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-]{20,})',
                r'\1[REDACTED]',
                'api_key'
            ),
            (
                r'(token["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-]{20,})',
                r'\1[REDACTED]',
                'token'
            ),
            (
                r'(auth[-_]?token["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-]{20,})',
                r'\1[REDACTED]',
                'auth_token'
            ),
            
            # Fortinet passwords
            (
                r'(set\s+password\s+)(\S+)',
                r'\1[REDACTED]',
                'fortinet_password'
            ),
            (
                r'(set\s+passwd\s+)(\S+)',
                r'\1[REDACTED]',
                'fortinet_password'
            ),
            
            # Generic key patterns (must be after specific ones)
            (
                r'(key\s+)([a-fA-F0-9]{32,})',
                r'\1[REDACTED]',
                'hex_key'
            ),
        ]
    
    def mask_secrets(self, content: str) -> MaskingResult:
        """
        Mask secrets in configuration content
        
        Args:
            content: Original configuration content
            
        Returns:
            MaskingResult with sanitized content and metadata
        """
        import hashlib
        
        # Calculate original hash for verification
        original_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        sanitized = content
        masked_count = 0
        masked_types = set()
        
        # Apply each masking pattern
        for pattern, replacement, secret_type in self.patterns:
            matches = re.findall(pattern, sanitized, re.DOTALL | re.IGNORECASE)
            if matches:
                masked_count += len(matches)
                masked_types.add(secret_type)
                sanitized = re.sub(pattern, replacement, sanitized, flags=re.DOTALL | re.IGNORECASE)
        
        return MaskingResult(
            sanitized_content=sanitized,
            masked_count=masked_count,
            masked_types=sorted(list(masked_types)),
            original_hash=original_hash
        )
    
    def detect_secrets(self, content: str) -> Dict[str, int]:
        """
        Detect secrets without masking (for reporting)
        
        Returns:
            Dictionary of {secret_type: count}
        """
        detected = {}
        
        for pattern, _, secret_type in self.patterns:
            matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
            if matches:
                detected[secret_type] = len(matches)
        
        return detected


def mask_configuration(content: str) -> MaskingResult:
    """
    Convenience function to mask secrets in configuration
    
    Args:
        content: Original configuration content
        
    Returns:
        MaskingResult with sanitized content
    """
    masker = SecretMasker()
    return masker.mask_secrets(content)


def detect_secrets(content: str) -> Dict[str, int]:
    """
    Convenience function to detect secrets without masking
    
    Args:
        content: Configuration content
        
    Returns:
        Dictionary of detected secret types and counts
    """
    masker = SecretMasker()
    return masker.detect_secrets(content)


# Example usage and testing
if __name__ == "__main__":
    # Test Cisco configuration
    test_cisco = """
hostname CORE-01

username admin secret 5 $1$abc$xyz123
username operator password MyPassword123

enable secret 5 $1$def$xyz789

snmp-server community public RO
snmp-server community private RW

line vty 0 4
 password CiscoPass
 transport input ssh

key config-key password-encrypt SuperSecretKey123
"""
    
    print("Testing Secret Masking Engine")
    print("=" * 60)
    
    masker = SecretMasker()
    result = masker.mask_secrets(test_cisco)
    
    print(f"Masked {result.masked_count} secrets")
    print(f"Types: {', '.join(result.masked_types)}")
    print("\nSanitized configuration:")
    print(result.sanitized_content)
    print("\nDetected secrets:")
    for secret_type, count in masker.detect_secrets(test_cisco).items():
        print(f"  {secret_type}: {count}")
