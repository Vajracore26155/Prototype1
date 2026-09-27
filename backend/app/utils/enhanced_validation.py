"""
Enhanced file validation utilities for professional vendor uploads
Provides comprehensive validation, error reporting, and security checks
"""
import os
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import hashlib
import tempfile

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

class UploadValidationResult:
    """Comprehensive validation result with detailed feedback"""
    
    def __init__(self):
        self.valid = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.file_info: Dict = {}
        self.security_checks: Dict = {}
    
    def add_error(self, error: str):
        """Add validation error"""
        self.errors.append(error)
        self.valid = False
    
    def add_warning(self, warning: str):
        """Add validation warning"""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for API response"""
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "file_info": self.file_info,
            "security_checks": self.security_checks
        }

class EnhancedFileValidator:
    """Professional-grade file validation for network device configurations"""
    
    def __init__(self):
        # Configuration file signatures and patterns
        self.config_signatures = {
            'cisco_ios': [
                r'hostname\s+\w+',
                r'interface\s+(FastEthernet|GigabitEthernet|Serial)',
                r'router\s+(ospf|eigrp|bgp)',
                r'ip\s+route',
                r'access-list\s+\d+'
            ],
            'juniper': [
                r'set\s+system\s+host-name',
                r'set\s+interfaces\s+\w+',
                r'set\s+routing-options',
                r'set\s+security\s+zones'
            ],
            'fortinet': [
                r'config\s+system\s+global',
                r'config\s+system\s+interface',
                r'config\s+firewall\s+policy'
            ],
            'palo_alto': [
                r'set\s+deviceconfig\s+system\s+hostname',
                r'set\s+network\s+interface',
                r'set\s+rulebase\s+security'
            ]
        }
        
        # Allowed file extensions with descriptions
        self.allowed_extensions = {
            '.cfg': 'Cisco IOS Configuration',
            '.conf': 'Generic Configuration File',
            '.txt': 'Text Configuration File',
            '.json': 'JSON Configuration File',
            '.xml': 'XML Configuration File',
            '.set': 'Juniper Set Commands',
            '.rsc': 'RouterOS Script Configuration'
        }
        
        # Security patterns to detect (but allow with warnings)
        self.sensitive_patterns = [
            (r'password\s+\w+', 'Plain text passwords detected'),
            (r'enable\s+password\s+\w+', 'Enable password in plain text'),
            (r'snmp-server\s+community\s+\w+', 'SNMP community strings detected'),
            (r'username\s+\w+\s+password\s+\w+', 'User credentials detected'),
            (r'key\s+\w+', 'Encryption keys detected'),
            (r'secret\s+\w+', 'Secret values detected')
        ]
    
    def validate_file_comprehensive(self, file_content: bytes, filename: str) -> UploadValidationResult:
        """
        Comprehensive file validation with detailed feedback
        
        Args:
            file_content: Raw file content as bytes
            filename: Original filename
            
        Returns:
            UploadValidationResult with detailed validation information
        """
        result = UploadValidationResult()
        
        # Basic file info
        result.file_info = {
            "filename": filename,
            "size_bytes": len(file_content),
            "size_human": self._format_bytes(len(file_content))
        }
        
        try:
            # 1. Filename validation
            self._validate_filename(filename, result)
            
            # 2. File size validation
            self._validate_file_size(len(file_content), result)
            
            # 3. File content validation
            if len(file_content) > 0:
                try:
                    content_str = file_content.decode('utf-8', errors='replace')
                    self._validate_content(content_str, filename, result)
                except UnicodeDecodeError:
                    result.add_error("File is not valid UTF-8 text")
            else:
                result.add_error("File is empty")
            
            # 4. Security validation
            if result.valid and len(file_content) > 0:
                self._validate_security(content_str, result)
            
            # 5. Configuration format detection
            if result.valid and len(file_content) > 0:
                self._detect_config_format(content_str, result)
            
        except Exception as e:
            result.add_error(f"Validation failed: {str(e)}")
        
        return result
    
    def _validate_filename(self, filename: str, result: UploadValidationResult):
        """Validate filename for security and format"""
        if not filename:
            result.add_error("Filename is required")
            return
        
        # Security checks
        if '..' in filename or '/' in filename or '\\' in filename:
            result.add_error("Filename contains path traversal characters")
        
        if len(filename) > 255:
            result.add_error("Filename is too long (max 255 characters)")
        
        # Check for suspicious characters
        if re.search(r'[<>:"|?*\x00-\x1f]', filename):
            result.add_error("Filename contains invalid characters")
        
        # Extension validation
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.allowed_extensions:
            allowed_list = ', '.join(self.allowed_extensions.keys())
            result.add_error(f"File extension '{file_ext}' not allowed. Supported: {allowed_list}")
        else:
            result.file_info["extension"] = file_ext
            result.file_info["type_description"] = self.allowed_extensions[file_ext]
    
    def _validate_file_size(self, size: int, result: UploadValidationResult):
        """Validate file size constraints"""
        max_size = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB default
        min_size = 10  # Minimum 10 bytes
        
        if size > max_size:
            result.add_error(f"File size ({self._format_bytes(size)}) exceeds maximum allowed ({self._format_bytes(max_size)})")
        
        if size < min_size:
            result.add_error(f"File too small ({size} bytes), minimum {min_size} bytes required")
        
        # Warning for very large files
        if size > max_size * 0.8:  # 80% of max size
            result.add_warning(f"Large file ({self._format_bytes(size)}) may take longer to process")
    
    def _validate_content(self, content: str, filename: str, result: UploadValidationResult):
        """Validate file content structure and format"""
        lines = content.splitlines()
        result.file_info["line_count"] = len(lines)
        
        # Check for minimum content
        non_empty_lines = [line for line in lines if line.strip()]
        if len(non_empty_lines) < 5:
            result.add_warning("File has very few configuration lines, may not be a complete configuration")
        
        # Check for extremely long lines (potential binary data)
        max_line_length = 2000
        long_lines = [i+1 for i, line in enumerate(lines) if len(line) > max_line_length]
        if long_lines:
            result.add_warning(f"File contains very long lines (lines {long_lines[:5]}), may indicate binary content")
        
        # Check for common configuration indicators
        config_indicators = 0
        if re.search(r'hostname\s+\w+', content, re.IGNORECASE):
            config_indicators += 1
        if re.search(r'interface\s+\w+', content, re.IGNORECASE):
            config_indicators += 1
        if re.search(r'(ip|ipv6)\s+(route|address)', content, re.IGNORECASE):
            config_indicators += 1
        
        result.file_info["config_indicators"] = config_indicators
        
        if config_indicators == 0:
            result.add_warning("File does not appear to contain typical network configuration commands")
    
    def _validate_security(self, content: str, result: UploadValidationResult):
        """Security validation and sensitive data detection"""
        security_issues = []
        
        # Check for sensitive patterns
        for pattern, description in self.sensitive_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                security_issues.append({
                    "pattern": description,
                    "count": len(matches),
                    "severity": "medium"
                })
                result.add_warning(f"{description} ({len(matches)} instances)")
        
        # Check for potential malicious content
        malicious_patterns = [
            (r'<script[^>]*>', 'JavaScript code detected'),
            (r'eval\s*\(', 'Eval function detected'),
            (r'exec\s*\(', 'Exec function detected'),
            (r'system\s*\(', 'System call detected')
        ]
        
        for pattern, description in malicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                security_issues.append({
                    "pattern": description,
                    "severity": "high"
                })
                result.add_error(f"Security risk: {description}")
        
        result.security_checks = {
            "sensitive_data_found": len(security_issues) > 0,
            "issues": security_issues
        }
    
    def _detect_config_format(self, content: str, result: UploadValidationResult):
        """Detect network device configuration format"""
        format_scores = {}
        
        for vendor, patterns in self.config_signatures.items():
            score = 0
            matched_patterns = []
            
            for pattern in patterns:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                if matches > 0:
                    score += matches
                    matched_patterns.append(pattern)
            
            if score > 0:
                format_scores[vendor] = {
                    "score": score,
                    "matched_patterns": matched_patterns
                }
        
        if format_scores:
            # Find best match
            best_match = max(format_scores.keys(), key=lambda k: format_scores[k]["score"])
            confidence = min(format_scores[best_match]["score"] / 5.0, 1.0)  # Normalize to 0-1
            
            result.file_info["detected_format"] = {
                "vendor": best_match,
                "confidence": confidence,
                "all_scores": format_scores
            }
            
            if confidence > 0.7:
                result.add_warning(f"Detected {best_match.replace('_', ' ').title()} configuration format")
            else:
                result.add_warning("Configuration format not clearly identified")
        else:
            result.add_warning("Could not identify configuration format - generic processing will be used")
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes into human readable format"""
        if bytes_value == 0:
            return '0 B'
        
        units = ['B', 'KB', 'MB', 'GB']
        unit_index = 0
        size = bytes_value
        
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        return f"{size:.1f} {units[unit_index]}"

def validate_upload_file(file_content: bytes, filename: str) -> UploadValidationResult:
    """
    Main validation function for upload files
    
    Args:
        file_content: Raw file content as bytes
        filename: Original filename
        
    Returns:
        UploadValidationResult with comprehensive validation information
    """
    validator = EnhancedFileValidator()
    return validator.validate_file_comprehensive(file_content, filename)