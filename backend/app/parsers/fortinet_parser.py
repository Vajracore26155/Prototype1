"""
Fortinet FortiGate Configuration Parser

Extracts security-relevant settings from FortiGate configurations
and maps them to the Unified Security Model
"""
import re
from typing import Optional, Tuple, List
from datetime import datetime

from .base import BaseParser, ParserError
from app.normalization.schema import (
    UnifiedSecurityModel,
    DeviceInfo,
    RemoteAccess,
    ManagementProtocols,
    Authentication,
    Logging,
    AccessControl,
    Evidence
)


class FortinetParser(BaseParser):
    """
    Parser for Fortinet FortiGate configurations
    
    Extracts:
    - Hostname
    - SSH/Telnet/HTTP/HTTPS from allowaccess
    - Authentication settings
    - Logging configuration
    
    Demonstrates vendor-agnostic architecture:
    Different syntax, same Unified Security Model output
    """
    
    @property
    def vendor_name(self) -> str:
        return "Fortinet"
    
    def can_parse(self, content: str) -> bool:
        """Check if this is a FortiGate configuration"""
        fortinet_indicators = [
            r'^\s*config\s+(?:system|firewall)',
            r'^\s*edit\s+["\']?\w+["\']?',
            r'\ballowaccess\b',
        ]
        
        for pattern in fortinet_indicators:
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                return True
        
        return False
    
    def parse(self, content: str, filename: str) -> UnifiedSecurityModel:
        """Parse FortiGate configuration"""
        try:
            # Split into lines for line-number tracking
            lines = content.split('\n')
            
            # Parse device information
            device = self._parse_device(content, lines, filename)
            
            # Parse remote access settings (from interface allowaccess)
            remote_access = self._parse_remote_access(content, lines, filename)
            
            # Parse management protocols (also from allowaccess)
            management = self._parse_management(content, lines, filename)
            
            # Parse authentication
            authentication = self._parse_authentication(content, lines, filename)
            
            # Parse logging
            logging = self._parse_logging(content, lines, filename)
            
            # Parse access control
            access_control = self._parse_access_control(content, lines, filename)
            
            # Build unified model
            import hashlib
            model = UnifiedSecurityModel(
                device=device,
                remote_access=remote_access,
                management=management,
                authentication=authentication,
                logging=logging,
                access_control=access_control,
                raw_config_hash=hashlib.sha256(content.encode()).hexdigest()[:16],
                normalized_at=datetime.utcnow().isoformat()
            )
            
            return model
            
        except Exception as e:
            raise ParserError(f"Failed to parse Fortinet configuration: {str(e)}")
    
    def _find_pattern(self, pattern: str, lines: list, flags=re.IGNORECASE) -> Optional[Tuple[int, str]]:
        """
        Find pattern in lines and return (line_number, line_text)
        Line numbers are 1-indexed
        """
        for i, line in enumerate(lines):
            if re.search(pattern, line, flags):
                return (i + 1, line.strip())
        return None
    
    def _find_all_patterns(self, pattern: str, lines: list, flags=re.IGNORECASE) -> List[Tuple[int, str]]:
        """Find all occurrences of pattern"""
        results = []
        for i, line in enumerate(lines):
            if re.search(pattern, line, flags):
                results.append((i + 1, line.strip()))
        return results
    
    def _parse_device(self, content: str, lines: list, filename: str) -> DeviceInfo:
        """Parse device information"""
        hostname = None
        hostname_evidence = None
        
        # Extract hostname from "config system global" section
        result = self._find_pattern(r'set\s+hostname\s+["\']?(\S+)["\']?', lines)
        if result:
            line_num, line_text = result
            match = re.search(r'set\s+hostname\s+["\']?(\S+)["\']?', line_text, re.IGNORECASE)
            if match:
                hostname = match.group(1).strip('"\'')
                hostname_evidence = Evidence(
                    file=filename,
                    line=line_num,
                    text=line_text
                )
        
        return DeviceInfo(
            hostname=hostname,
            vendor="Fortinet",
            device_type="firewall",
            version=None,  # Version extraction would require more parsing
            evidence=hostname_evidence
        )
    
    def _parse_remote_access(self, content: str, lines: list, filename: str) -> RemoteAccess:
        """
        Parse remote access settings from allowaccess
        
        FortiGate uses "set allowaccess" on interfaces to control
        management protocols. Look for SSH and Telnet.
        """
        ssh_enabled = None
        telnet_enabled = None
        
        ssh_evidence = None
        telnet_evidence = None
        
        # Find all allowaccess lines
        allowaccess_lines = self._find_all_patterns(r'set\s+allowaccess\s+', lines)
        
        # Aggregate across all interfaces
        has_ssh = False
        has_telnet = False
        first_ssh_line = None
        first_telnet_line = None
        
        for line_num, line_text in allowaccess_lines:
            # Extract the access list
            match = re.search(r'set\s+allowaccess\s+(.+)', line_text, re.IGNORECASE)
            if match:
                access_list = match.group(1).lower()
                
                # Check for SSH
                if 'ssh' in access_list:
                    has_ssh = True
                    if not first_ssh_line:
                        first_ssh_line = (line_num, line_text)
                
                # Check for Telnet
                if 'telnet' in access_list:
                    has_telnet = True
                    if not first_telnet_line:
                        first_telnet_line = (line_num, line_text)
        
        # Set values based on what we found
        if has_ssh:
            ssh_enabled = True
            line_num, line_text = first_ssh_line
            ssh_evidence = Evidence(file=filename, line=line_num, text=line_text)
        
        if has_telnet:
            telnet_enabled = True
            line_num, line_text = first_telnet_line
            telnet_evidence = Evidence(file=filename, line=line_num, text=line_text)
        elif has_ssh and not has_telnet:
            # SSH found but no telnet - explicitly disabled
            telnet_enabled = False
            if first_ssh_line:
                line_num, line_text = first_ssh_line
                telnet_evidence = Evidence(file=filename, line=line_num, text=line_text)
        
        # SSH version is typically SSHv2 in modern FortiOS
        # We'll assume version 2 if SSH is enabled
        ssh_version = 2 if ssh_enabled else None
        ssh_version_evidence = ssh_evidence  # Same evidence source
        
        return RemoteAccess(
            ssh_enabled=ssh_enabled,
            ssh_version=ssh_version,
            telnet_enabled=telnet_enabled,
            ssh_enabled_evidence=ssh_evidence,
            ssh_version_evidence=ssh_version_evidence,
            telnet_enabled_evidence=telnet_evidence
        )
    
    def _parse_management(self, content: str, lines: list, filename: str) -> ManagementProtocols:
        """Parse management protocol settings"""
        http_enabled = None
        https_enabled = None
        snmp_enabled = None
        
        http_evidence = None
        https_evidence = None
        snmp_evidence = None
        
        # Check allowaccess for HTTP/HTTPS
        allowaccess_lines = self._find_all_patterns(r'set\s+allowaccess\s+', lines)
        
        has_http = False
        has_https = False
        first_http_line = None
        first_https_line = None
        
        for line_num, line_text in allowaccess_lines:
            match = re.search(r'set\s+allowaccess\s+(.+)', line_text, re.IGNORECASE)
            if match:
                access_list = match.group(1).lower()
                
                # Check for HTTP (not https)
                if re.search(r'\bhttp\b(?!s)', access_list):
                    has_http = True
                    if not first_http_line:
                        first_http_line = (line_num, line_text)
                
                # Check for HTTPS
                if 'https' in access_list:
                    has_https = True
                    if not first_https_line:
                        first_https_line = (line_num, line_text)
        
        if has_http:
            http_enabled = True
            line_num, line_text = first_http_line
            http_evidence = Evidence(file=filename, line=line_num, text=line_text)
        
        if has_https:
            https_enabled = True
            line_num, line_text = first_https_line
            https_evidence = Evidence(file=filename, line=line_num, text=line_text)
        
        # Check for SNMP community
        result = self._find_pattern(r'config\s+system\s+snmp\s+community', lines)
        if result:
            line_num, line_text = result
            snmp_enabled = True
            snmp_evidence = Evidence(file=filename, line=line_num, text=line_text)
        
        return ManagementProtocols(
            http_enabled=http_enabled,
            https_enabled=https_enabled,
            snmp_enabled=snmp_enabled,
            http_enabled_evidence=http_evidence,
            https_enabled_evidence=https_evidence,
            snmp_enabled_evidence=snmp_evidence
        )
    
    def _parse_authentication(self, content: str, lines: list, filename: str) -> Authentication:
        """Parse authentication settings"""
        local_auth = None
        enable_secret = None
        
        local_auth_evidence = None
        enable_evidence = None
        
        # Check for admin accounts (implies local auth)
        result = self._find_pattern(r'config\s+system\s+admin', lines)
        if result:
            line_num, line_text = result
            local_auth = True
            local_auth_evidence = Evidence(file=filename, line=line_num, text=line_text)
        
        # FortiGate doesn't have "enable secret" concept
        # Admin passwords serve similar purpose
        result = self._find_pattern(r'set\s+password\s+', lines)
        if result:
            line_num, line_text = result
            enable_secret = True
            enable_evidence = Evidence(file=filename, line=line_num, text=line_text)
        
        return Authentication(
            local_authentication=local_auth,
            password_encryption=None,  # Passwords are automatically encrypted in FortiGate
            enable_secret_configured=enable_secret,
            local_authentication_evidence=local_auth_evidence,
            enable_secret_evidence=enable_evidence
        )
    
    def _parse_logging(self, content: str, lines: list, filename: str) -> Logging:
        """Parse logging settings"""
        enabled = None
        remote_server = None
        
        enabled_evidence = None
        
        # Check for syslog configuration
        result = self._find_pattern(r'config\s+log\s+syslogd\s+setting', lines)
        if result:
            line_num, line_text = result
            
            # Look for status and server in nearby lines
            # This is a simplified approach - production would parse the full block
            status_line = self._find_pattern(r'set\s+status\s+enable', lines)
            if status_line:
                enabled = True
                enabled_evidence = Evidence(file=filename, line=line_num, text=line_text)
            
            # Try to find server
            server_result = self._find_pattern(r'set\s+server\s+["\']?(\d+\.\d+\.\d+\.\d+)["\']?', lines)
            if server_result:
                srv_line_num, srv_line_text = server_result
                match = re.search(r'set\s+server\s+["\']?(\d+\.\d+\.\d+\.\d+)["\']?', srv_line_text)
                if match:
                    remote_server = match.group(1)
        
        return Logging(
            enabled=enabled,
            remote_server=remote_server,
            buffered=None,  # FortiGate always has internal logging
            enabled_evidence=enabled_evidence
        )
    
    def _parse_access_control(self, content: str, lines: list, filename: str) -> AccessControl:
        """Parse access control settings"""
        timeout = None
        timeout_evidence = None
        
        # Check for admin timeout in system global
        result = self._find_pattern(r'set\s+admin-timeout\s+\d+', lines)
        if result:
            line_num, line_text = result
            timeout = True
            timeout_evidence = Evidence(file=filename, line=line_num, text=line_text)
        
        return AccessControl(
            timeout_configured=timeout,
            timeout_evidence=timeout_evidence
        )
