"""
Palo Alto Networks PAN-OS Configuration Parser

Extracts security-relevant settings from PAN-OS configurations
and maps them to the Unified Security Model

Supports set format (CLI-style) for Phase 1.
XML format deferred to Phase 2.
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


class PaloAltoParser(BaseParser):
    """
    Parser for Palo Alto Networks PAN-OS configurations
    
    Extracts:
    - Hostname from deviceconfig
    - SSH/Telnet settings (inverted logic: disable-X yes = disabled)
    - HTTP/HTTPS management protocols
    - Administrative users and password hashes
    - Syslog server configuration
    - Idle timeout settings
    
    Key Features:
    - Inverted logic handling (disable-telnet yes → telnet_enabled = False)
    - SSH version inference from cipher configuration
    - Zone-based security awareness (basic)
    """
    
    @property
    def vendor_name(self) -> str:
        return "Palo Alto"
    
    def can_parse(self, content: str) -> bool:
        """
        Check if this is a PAN-OS configuration
        
        Requires at least 2 PAN-OS indicators for confidence
        """
        panos_indicators = [
            r'^\s*set\s+deviceconfig\s+system',
            r'^\s*set\s+mgt-config',
            r'^\s*set\s+rulebase\s+security',
            r'\bphash\b',
            r'^\s*set\s+zone\s+\S+\s+network\s+layer3',
        ]
        
        matches = 0
        for pattern in panos_indicators:
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                matches += 1
        
        return matches >= 2
    
    def parse(self, content: str, filename: str) -> UnifiedSecurityModel:
        """Parse PAN-OS configuration"""
        try:
            lines = content.split('\n')
            
            # Parse device information
            device = self._parse_device(content, lines, filename)
            
            # Parse remote access settings (with inverted logic)
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
            raise ParserError(f"Failed to parse Palo Alto configuration: {str(e)}")
    
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
        hostname_evidence = None
        
        # Extract hostname
        result = self._find_pattern(r'set\s+deviceconfig\s+system\s+hostname\s+(\S+)', lines)
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
        
        return DeviceInfo(
            hostname=hostname,
            vendor="Palo Alto",
            device_type="firewall",
            version=None,  # Version requires operational command output
            evidence=hostname_evidence
        )
    
    def _parse_remote_access(self, content: str, lines: list, filename: str) -> RemoteAccess:
        """
        Parse remote access settings
        
        PAN-OS uses INVERTED LOGIC:
        - "disable-telnet yes" means telnet_enabled = False
        - "disable-telnet no" means telnet_enabled = True
        - Absence of disable-telnet means enabled by default
        
        SSH is enabled by default and rarely disabled
        """
        ssh_enabled = None
        telnet_enabled = None
        ssh_version = None
        
        ssh_evidence = None
        telnet_evidence = None
        ssh_version_evidence = None
        
        # Check for disable-telnet (INVERTED LOGIC)
        result = self._find_pattern(
            r'set\s+deviceconfig\s+system\s+service\s+disable-telnet\s+(yes|no)',
            lines
        )
        if result:
            line_num, line_text = result
            match = re.search(r'disable-telnet\s+(yes|no)', line_text, re.IGNORECASE)
            if match:
                # INVERTED: disable-telnet yes → telnet_enabled = False
                telnet_enabled = (match.group(1).lower() == 'no')
                telnet_evidence = Evidence(
                    file=filename,
                    line=line_num,
                    text=line_text
                )
        
        # Check for disable-ssh (rare, but possible)
        result = self._find_pattern(
            r'set\s+deviceconfig\s+system\s+service\s+disable-ssh\s+(yes|no)',
            lines
        )
        if result:
            line_num, line_text = result
            match = re.search(r'disable-ssh\s+(yes|no)', line_text, re.IGNORECASE)
            if match:
                # INVERTED: disable-ssh yes → ssh_enabled = False
                ssh_enabled = (match.group(1).lower() == 'no')
                ssh_evidence = Evidence(
                    file=filename,
                    line=line_num,
                    text=line_text
                )
        else:
            # SSH is enabled by default in PAN-OS
            ssh_enabled = True
        
        # Infer SSH version from cipher list
        result = self._find_pattern(
            r'set\s+deviceconfig\s+system\s+ssh-cipher-list',
            lines
        )
        if result:
            line_num, line_text = result
            # Modern ciphers imply SSHv2 (SSHv1 is deprecated)
            modern_ciphers = ['aes256', 'aes128', 'aes192', 'chacha20', '3des']
            if any(cipher in line_text.lower() for cipher in modern_ciphers):
                ssh_version = 2
                ssh_version_evidence = Evidence(
                    file=filename,
                    line=line_num,
                    text=line_text + " [SSHv2 inferred from modern ciphers]"
                )
        
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
        
        # Check for disable-http (INVERTED LOGIC)
        result = self._find_pattern(
            r'set\s+deviceconfig\s+system\s+service\s+disable-http\s+(yes|no)',
            lines
        )
        if result:
            line_num, line_text = result
            match = re.search(r'disable-http\s+(yes|no)', line_text, re.IGNORECASE)
            if match:
                # INVERTED: disable-http yes → http_enabled = False
                http_enabled = (match.group(1).lower() == 'no')
                http_evidence = Evidence(
                    file=filename,
                    line=line_num,
                    text=line_text
                )
        
        # HTTPS is always available on PAN-OS firewalls (management interface)
        # Check if explicitly configured
        result = self._find_pattern(
            r'set\s+deviceconfig\s+system\s+service\s+disable-https\s+(yes|no)',
            lines
        )
        if result:
            line_num, line_text = result
            match = re.search(r'disable-https\s+(yes|no)', line_text, re.IGNORECASE)
            if match:
                # INVERTED: disable-https yes → https_enabled = False
                https_enabled = (match.group(1).lower() == 'no')
                https_evidence = Evidence(
                    file=filename,
                    line=line_num,
                    text=line_text
                )
        else:
            # HTTPS enabled by default
            https_enabled = True
        
        # Check for SNMP configuration
        result = self._find_pattern(
            r'set\s+deviceconfig\s+system\s+snmp-setting',
            lines
        )
        if result:
            line_num, line_text = result
            snmp_enabled = True
            snmp_evidence = Evidence(
                file=filename,
                line=line_num,
                text=line_text
            )
        
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
        
        # Check for admin users (implies local authentication)
        result = self._find_pattern(
            r'set\s+mgt-config\s+users\s+\S+',
            lines
        )
        if result:
            line_num, line_text = result
            local_auth = True
            local_auth_evidence = Evidence(
                file=filename,
                line=line_num,
                text=line_text
            )
        
        # Check for password hash (phash = PAN-OS hash)
        result = self._find_pattern(
            r'phash\s+',
            lines
        )
        if result:
            line_num, line_text = result
            enable_secret = True
            enable_evidence = Evidence(
                file=filename,
                line=line_num,
                text=line_text + " [phash password configured]"
            )
        
        return Authentication(
            local_authentication=local_auth,
            password_encryption=None,  # PAN-OS auto-encrypts all passwords
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
        result = self._find_pattern(
            r'set\s+shared\s+log-settings\s+syslog',
            lines
        )
        if result:
            line_num, line_text = result
            enabled = True
            enabled_evidence = Evidence(
                file=filename,
                line=line_num,
                text=line_text
            )
            
            # Try to extract server IP
            server_result = self._find_pattern(
                r'address\s+(\d+\.\d+\.\d+\.\d+)',
                lines
            )
            if server_result:
                srv_line_num, srv_line_text = server_result
                match = re.search(r'address\s+(\d+\.\d+\.\d+\.\d+)', srv_line_text)
                if match:
                    remote_server = match.group(1)
        
        return Logging(
            enabled=enabled,
            remote_server=remote_server,
            buffered=None,  # PAN-OS always has internal logging
            enabled_evidence=enabled_evidence
        )
    
    def _parse_access_control(self, content: str, lines: list, filename: str) -> AccessControl:
        """Parse access control settings"""
        timeout = None
        timeout_evidence = None
        
        # Check for idle-timeout
        result = self._find_pattern(
            r'set\s+deviceconfig\s+system\s+idle-timeout\s+\d+',
            lines
        )
        if result:
            line_num, line_text = result
            timeout = True
            timeout_evidence = Evidence(
                file=filename,
                line=line_num,
                text=line_text
            )
        
        return AccessControl(
            timeout_configured=timeout,
            timeout_evidence=timeout_evidence
        )
