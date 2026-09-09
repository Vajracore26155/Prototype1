"""
Cisco IOS/IOS-XE Configuration Parser

Extracts security-relevant settings from Cisco configurations
and maps them to the Unified Security Model
"""
import re
from typing import Optional, Tuple
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


class CiscoParser(BaseParser):
    """
    Parser for Cisco IOS/IOS-XE configurations
    
    Extracts:
    - Hostname
    - SSH/Telnet settings
    - HTTP/HTTPS management
    - Authentication configuration
    - Logging settings
    """
    
    @property
    def vendor_name(self) -> str:
        return "Cisco"
    
    def can_parse(self, content: str) -> bool:
        """Check if this is a Cisco configuration"""
        cisco_indicators = [
            r'^\s*interface\s+(?:GigabitEthernet|FastEthernet)',
            r'^\s*line\s+vty',
            r'^\s*router\s+(?:ospf|eigrp|bgp)',
            r'^\s*ip\s+(?:route|ssh)',
        ]
        
        for pattern in cisco_indicators:
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                return True
        
        return False
    
    def parse(self, content: str, filename: str) -> UnifiedSecurityModel:
        """Parse Cisco configuration"""
        try:
            # Split into lines for line-number tracking
            lines = content.split('\n')
            
            # Parse device information
            device = self._parse_device(content, lines, filename)
            
            # Parse remote access settings
            remote_access = self._parse_remote_access(content, lines, filename)
            
            # Parse management protocols
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
            raise ParserError(f"Failed to parse Cisco configuration: {str(e)}")
    
    def _find_pattern(self, pattern: str, lines: list, flags=re.IGNORECASE) -> Optional[Tuple[int, str]]:
        """
        Find pattern in lines and return (line_number, line_text)
        Line numbers are 1-indexed for human readability
        """
        for i, line in enumerate(lines):
            if re.search(pattern, line, flags):
                return (i + 1, line.strip())
        return None
    
    def _parse_device(self, content: str, lines: list, filename: str) -> DeviceInfo:
        """Parse device information"""
        hostname = None
        version = None
        hostname_evidence = None
        
        # Extract hostname
        result = self._find_pattern(r'^\s*hostname\s+(\S+)', lines)
        if result:
            line_num, line_text = result
            match = re.search(r'hostname\s+(\S+)', line_text, re.IGNORECASE)
            if match:
                hostname = match.group(1)
                hostname_evidence = Evidence(
                    file=filename,
                    line=line_num,
                    text=line_text
                )
        
        # Extract version
        result = self._find_pattern(r'^\s*version\s+([\d.]+)', lines)
        if result:
            line_num, line_text = result
            match = re.search(r'version\s+([\d.]+)', line_text, re.IGNORECASE)
            if match:
                version = match.group(1)
        
        return DeviceInfo(
            hostname=hostname,
            vendor="Cisco",
            device_type="router",  # Could be enhanced to detect switch/router/etc
            version=version,
            evidence=hostname_evidence
        )
    
    def _parse_remote_access(self, content: str, lines: list, filename: str) -> RemoteAccess:
        """Parse remote access settings (SSH, Telnet)"""
        ssh_enabled = None
        ssh_version = None
        telnet_enabled = None
        
        ssh_evidence = None
        ssh_version_evidence = None
        telnet_evidence = None
        
        # Check for "transport input" command
        result = self._find_pattern(r'^\s*transport\s+input\s+(.+)', lines)
        if result:
            line_num, line_text = result
            match = re.search(r'transport\s+input\s+(.+)', line_text, re.IGNORECASE)
            if match:
                transports = match.group(1).lower()
                
                # Check for SSH
                if 'ssh' in transports:
                    ssh_enabled = True
                    ssh_evidence = Evidence(file=filename, line=line_num, text=line_text)
                
                # Check for Telnet
                if 'telnet' in transports:
                    telnet_enabled = True
                    telnet_evidence = Evidence(file=filename, line=line_num, text=line_text)
                elif 'none' in transports or transports.strip() == 'ssh':
                    # Only SSH or none - telnet disabled
                    telnet_enabled = False
                    if not telnet_evidence:
                        telnet_evidence = Evidence(file=filename, line=line_num, text=line_text)
        
        # If transport input not found, check individual line vty settings
        if ssh_enabled is None and telnet_enabled is None:
            # Default behavior: if no transport input, both might be enabled
            # For security, we'll assume telnet could be enabled unless proven otherwise
            pass
        
        # Check SSH version
        result = self._find_pattern(r'^\s*ip\s+ssh\s+version\s+(\d+)', lines)
        if result:
            line_num, line_text = result
            match = re.search(r'ip\s+ssh\s+version\s+(\d+)', line_text, re.IGNORECASE)
            if match:
                ssh_version = int(match.group(1))
                ssh_version_evidence = Evidence(file=filename, line=line_num, text=line_text)
                # If SSH version is configured, SSH is likely enabled
                if ssh_enabled is None:
                    ssh_enabled = True
                    if not ssh_evidence:
                        ssh_evidence = ssh_version_evidence
        
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
        
        # Check for HTTP server
        result = self._find_pattern(r'^\s*(no\s+)?ip\s+http\s+server', lines)
        if result:
            line_num, line_text = result
            if line_text.strip().startswith('no '):
                http_enabled = False
            else:
                http_enabled = True
            http_evidence = Evidence(file=filename, line=line_num, text=line_text)
        
        # Check for HTTPS server
        result = self._find_pattern(r'^\s*(no\s+)?ip\s+http\s+secure-server', lines)
        if result:
            line_num, line_text = result
            if line_text.strip().startswith('no '):
                https_enabled = False
            else:
                https_enabled = True
            https_evidence = Evidence(file=filename, line=line_num, text=line_text)
        
        # Check for SNMP
        result = self._find_pattern(r'^\s*snmp-server\s+community', lines)
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
        password_encryption = None
        enable_secret = None
        
        local_auth_evidence = None
        encryption_evidence = None
        enable_evidence = None
        
        # Check for "login local"
        result = self._find_pattern(r'^\s*login\s+local', lines)
        if result:
            line_num, line_text = result
            local_auth = True
            local_auth_evidence = Evidence(file=filename, line=line_num, text=line_text)
        
        # Check for password encryption service
        result = self._find_pattern(r'^\s*(no\s+)?service\s+password-encryption', lines)
        if result:
            line_num, line_text = result
            if line_text.strip().startswith('no '):
                password_encryption = False
            else:
                password_encryption = True
            encryption_evidence = Evidence(file=filename, line=line_num, text=line_text)
        
        # Check for enable secret
        result = self._find_pattern(r'^\s*enable\s+secret', lines)
        if result:
            line_num, line_text = result
            enable_secret = True
            enable_evidence = Evidence(file=filename, line=line_num, text=line_text)
        
        return Authentication(
            local_authentication=local_auth,
            password_encryption=password_encryption,
            enable_secret_configured=enable_secret,
            local_authentication_evidence=local_auth_evidence,
            password_encryption_evidence=encryption_evidence,
            enable_secret_evidence=enable_evidence
        )
    
    def _parse_logging(self, content: str, lines: list, filename: str) -> Logging:
        """Parse logging settings"""
        enabled = None
        remote_server = None
        buffered = None
        
        enabled_evidence = None
        
        # Check for logging to remote server
        result = self._find_pattern(r'^\s*logging\s+(\d+\.\d+\.\d+\.\d+)', lines)
        if result:
            line_num, line_text = result
            match = re.search(r'logging\s+(\d+\.\d+\.\d+\.\d+)', line_text, re.IGNORECASE)
            if match:
                enabled = True
                remote_server = match.group(1)
                enabled_evidence = Evidence(file=filename, line=line_num, text=line_text)
        
        # Check for buffered logging
        result = self._find_pattern(r'^\s*logging\s+buffered', lines)
        if result:
            buffered = True
            if not enabled:
                line_num, line_text = result
                enabled = True
                enabled_evidence = Evidence(file=filename, line=line_num, text=line_text)
        
        return Logging(
            enabled=enabled,
            remote_server=remote_server,
            buffered=buffered,
            enabled_evidence=enabled_evidence
        )
    
    def _parse_access_control(self, content: str, lines: list, filename: str) -> AccessControl:
        """Parse access control settings"""
        timeout = None
        timeout_evidence = None
        
        # Check for exec-timeout or timeout login response
        result = self._find_pattern(r'^\s*(?:exec-timeout|timeout\s+login\s+response)', lines)
        if result:
            line_num, line_text = result
            timeout = True
            timeout_evidence = Evidence(file=filename, line=line_num, text=line_text)
        
        return AccessControl(
            timeout_configured=timeout,
            timeout_evidence=timeout_evidence
        )
