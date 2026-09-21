"""
Juniper Networks JunOS Configuration Parser

Extracts security-relevant settings from JunOS configurations
and maps them to the Unified Security Model

Supports both hierarchical (curly-brace) and flattened ('display set') formats.
"""
import re
from typing import Optional, Tuple, Dict, Any
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


class ConfigTokenizer:
    """
    Tokenizes Juniper hierarchical config into structured blocks
    
    Converts curly-brace syntax to nested dictionary for easier processing
    """
    
    def tokenize(self, content: str) -> Dict[str, Any]:
        """
        Convert hierarchical config to nested dict
        
        Example:
            system {
                host-name CORE;
                services {
                    ssh;
                }
            }
        
        Returns:
            {
                'system': {
                    'host-name': 'CORE',
                    'services': {
                        'ssh': True
                    }
                }
            }
        """
        lines = content.split('\n')
        root = {}
        stack = [root]
        
        for line_num, line in enumerate(lines, 1):
            original_line = line
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#') or line.startswith('!'):
                continue
            
            # Handle block start: "system {"
            if line.endswith('{'):
                key = line[:-1].strip()
                new_block = {'__line__': line_num, '__original__': original_line}
                
                if stack and isinstance(stack[-1], dict):
                    stack[-1][key] = new_block
                
                stack.append(new_block)
            
            # Handle block end: "}"
            elif line == '}' or line == '};':
                if len(stack) > 1:
                    stack.pop()
            
            # Handle key-value or standalone key: "host-name CORE;" or "ssh;"
            elif ';' in line:
                line = line.rstrip(';')
                parts = line.split(None, 1)
                key = parts[0]
                value = parts[1] if len(parts) > 1 else True
                
                if stack and isinstance(stack[-1], dict):
                    stack[-1][key] = value
                    stack[-1][f'{key}__line__'] = line_num
        
        return root
    
    def parse_flattened_format(self, content: str) -> Dict[str, Any]:
        """
        Parse flattened 'display set' format
        
        Example:
            set system host-name CORE
            set system services ssh
        
        Returns:
            {
                'system': {
                    'host-name': 'CORE',
                    'services': {
                        'ssh': True
                    }
                }
            }
        """
        lines = content.split('\n')
        root = {}
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            if not line or not line.startswith('set '):
                continue
            
            # Remove 'set ' prefix
            line = line[4:]
            parts = line.split()
            
            if not parts:
                continue
            
            # Navigate/create nested structure
            current = root
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                elif not isinstance(current[part], dict):
                    # Value exists, convert to dict
                    old_value = current[part]
                    current[part] = {'__value__': old_value}
                current = current[part]
            
            # Set final value
            final_key = parts[-1]
            current[final_key] = True
            current[f'{final_key}__line__'] = line_num
        
        return root


class JuniperParser(BaseParser):
    """
    Parser for Juniper Networks JunOS configurations
    
    Extracts:
    - Hostname from system block
    - SSH/Telnet from services (presence = enabled)
    - Web management (HTTP/HTTPS)
    - User authentication
    - Syslog configuration
    - Session idle timeout
    - Firewall filters for access control
    
    Key Features:
    - Handles both hierarchical and flattened formats
    - Service presence implies enabled (unlike Cisco/Palo Alto)
    - Device type inference from interface naming
    - Firewall filter detection for source_filtering
    """
    
    def __init__(self):
        self.tokenizer = ConfigTokenizer()
    
    @property
    def vendor_name(self) -> str:
        return "Juniper"
    
    def can_parse(self, content: str) -> bool:
        """
        Check if this is a JunOS configuration
        
        Requires at least 2 JunOS indicators for confidence
        """
        junos_indicators = [
            r'^\s*system\s*\{',
            r'^\s*set\s+system\s+host-name',
            r'^\s*interfaces\s*\{',
            r'^\s*set\s+interfaces\s+[a-z]{2}-\d+/\d+/\d+',
            r'encrypted-password\s+"\$',
            r'class\s+super-user',
        ]
        
        matches = 0
        for pattern in junos_indicators:
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                matches += 1
        
        return matches >= 2
    
    def parse(self, content: str, filename: str) -> UnifiedSecurityModel:
        """Parse JunOS configuration"""
        try:
            # Detect format and tokenize
            if self._is_flattened_format(content):
                config_tree = self.tokenizer.parse_flattened_format(content)
                format_type = "flattened"
            else:
                config_tree = self.tokenizer.tokenize(content)
                format_type = "hierarchical"
            
            # Store content and format for evidence extraction
            self._content = content
            self._format_type = format_type
            
            # Parse sections
            device = self._parse_device(config_tree, content, filename)
            remote_access = self._parse_remote_access(config_tree, content, filename)
            management = self._parse_management(config_tree, content, filename)
            authentication = self._parse_authentication(config_tree, content, filename)
            logging = self._parse_logging(config_tree, content, filename)
            access_control = self._parse_access_control(config_tree, content, filename)
            
            # Build model
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
            raise ParserError(f"Failed to parse Juniper configuration: {str(e)}")
    
    def _is_flattened_format(self, content: str) -> bool:
        """
        Check if config is in 'display set' format
        
        Returns True if >50% of lines are 'set' commands
        """
        lines = content.split('\n')
        non_empty_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
        set_lines = [l for l in non_empty_lines if l.strip().startswith('set ')]
        
        if not non_empty_lines:
            return False
        
        return len(set_lines) > len(non_empty_lines) * 0.5
    
    def _get_line_text(self, content: str, line_num: int) -> str:
        """Get text of specific line number"""
        if line_num == 0:
            return ""
        lines = content.split('\n')
        if 0 < line_num <= len(lines):
            return lines[line_num - 1].strip()
        return ""
    
    def _parse_device(self, config_tree: Dict, content: str, filename: str) -> DeviceInfo:
        """Parse device information"""
        hostname = None
        hostname_evidence = None
        device_type = "unknown"
        
        # Navigate to system.host-name
        system = config_tree.get('system', {})
        if isinstance(system, dict):
            hostname = system.get('host-name')
            if hostname and isinstance(hostname, str):
                line_num = system.get('host-name__line__', 0)
                hostname_evidence = Evidence(
                    file=filename,
                    line=line_num,
                    text=self._get_line_text(content, line_num)
                )
        
        # Infer device type from interface naming
        interfaces = config_tree.get('interfaces', {})
        if isinstance(interfaces, dict):
            device_type = self._infer_device_type(interfaces)
        
        return DeviceInfo(
            hostname=hostname,
            vendor="Juniper",
            device_type=device_type,
            version=None,  # Version requires operational command output
            evidence=hostname_evidence
        )
    
    def _infer_device_type(self, interfaces: Dict) -> str:
        """
        Infer device type from interface naming
        
        - ge- (GigabitEthernet) → router
        - xe- (10 GigabitEthernet) → router
        - fxp- (Management port) → router/switch
        - ae- (Aggregated Ethernet) → switch
        """
        for interface_name in interfaces.keys():
            if not isinstance(interface_name, str):
                continue
            if interface_name.startswith('ge-'):
                return "router"
            elif interface_name.startswith('xe-'):
                return "router"
            elif interface_name.startswith('ae-'):
                return "switch"
        
        return "unknown"
    
    def _parse_remote_access(self, config_tree: Dict, content: str, filename: str) -> RemoteAccess:
        """
        Parse remote access settings
        
        JunOS: Service PRESENCE means ENABLED
        - system { services { ssh; } } → ssh_enabled = True
        - system { services { telnet; } } → telnet_enabled = True
        """
        ssh_enabled = None
        telnet_enabled = None
        ssh_version = None
        
        ssh_evidence = None
        telnet_evidence = None
        ssh_version_evidence = None
        
        # Navigate to system.services
        system = config_tree.get('system', {})
        services = system.get('services', {}) if isinstance(system, dict) else {}
        
        if isinstance(services, dict):
            # Check for SSH
            if 'ssh' in services:
                ssh_enabled = True
                line_num = services.get('ssh__line__', 0)
                ssh_evidence = Evidence(
                    file=filename,
                    line=line_num,
                    text=self._get_line_text(content, line_num)
                )
                
                # Check SSH version
                ssh_config = services.get('ssh', {})
                if isinstance(ssh_config, dict):
                    protocol_version = ssh_config.get('protocol-version', '')
                    if 'v2' in str(protocol_version):
                        ssh_version = 2
                        line_num = ssh_config.get('protocol-version__line__', line_num)
                        ssh_version_evidence = Evidence(
                            file=filename,
                            line=line_num,
                            text=self._get_line_text(content, line_num)
                        )
            
            # Check for Telnet
            if 'telnet' in services:
                telnet_enabled = True
                line_num = services.get('telnet__line__', 0)
                telnet_evidence = Evidence(
                    file=filename,
                    line=line_num,
                    text=self._get_line_text(content, line_num)
                )
        
        return RemoteAccess(
            ssh_enabled=ssh_enabled,
            ssh_version=ssh_version,
            telnet_enabled=telnet_enabled,
            ssh_enabled_evidence=ssh_evidence,
            ssh_version_evidence=ssh_version_evidence,
            telnet_enabled_evidence=telnet_evidence
        )
    
    def _parse_management(self, config_tree: Dict, content: str, filename: str) -> ManagementProtocols:
        """Parse management protocol settings"""
        http_enabled = None
        https_enabled = None
        snmp_enabled = None
        
        http_evidence = None
        https_evidence = None
        snmp_evidence = None
        
        # Navigate to system.services.web-management
        system = config_tree.get('system', {})
        services = system.get('services', {}) if isinstance(system, dict) else {}
        
        if isinstance(services, dict):
            web_mgmt = services.get('web-management', {})
            
            if isinstance(web_mgmt, dict):
                # Check for HTTP
                if 'http' in web_mgmt:
                    http_enabled = True
                    line_num = web_mgmt.get('http__line__', 0)
                    http_evidence = Evidence(
                        file=filename,
                        line=line_num,
                        text=self._get_line_text(content, line_num)
                    )
                
                # Check for HTTPS
                if 'https' in web_mgmt:
                    https_enabled = True
                    line_num = web_mgmt.get('https__line__', 0)
                    https_evidence = Evidence(
                        file=filename,
                        line=line_num,
                        text=self._get_line_text(content, line_num)
                    )
        
        # Check for SNMP
        snmp_config = config_tree.get('snmp', {})
        if isinstance(snmp_config, dict) and snmp_config:
            snmp_enabled = True
            line_num = snmp_config.get('__line__', 0)
            snmp_evidence = Evidence(
                file=filename,
                line=line_num,
                text=self._get_line_text(content, line_num)
            )
        
        return ManagementProtocols(
            http_enabled=http_enabled,
            https_enabled=https_enabled,
            snmp_enabled=snmp_enabled,
            http_enabled_evidence=http_evidence,
            https_enabled_evidence=https_evidence,
            snmp_enabled_evidence=snmp_evidence
        )
    
    def _parse_authentication(self, config_tree: Dict, content: str, filename: str) -> Authentication:
        """Parse authentication settings"""
        local_auth = None
        enable_secret = None
        
        local_auth_evidence = None
        enable_evidence = None
        
        # Navigate to system.login
        system = config_tree.get('system', {})
        login_config = system.get('login', {}) if isinstance(system, dict) else {}
        
        if isinstance(login_config, dict):
            # Check for users (implies local authentication)
            user_config = login_config.get('user', {})
            if isinstance(user_config, dict) and user_config:
                local_auth = True
                line_num = user_config.get('__line__', 0)
                local_auth_evidence = Evidence(
                    file=filename,
                    line=line_num,
                    text=self._get_line_text(content, line_num)
                )
        
        # Check for root-authentication or user passwords
        root_auth = system.get('root-authentication', {}) if isinstance(system, dict) else {}
        if isinstance(root_auth, dict):
            encrypted_pw = root_auth.get('encrypted-password')
            if encrypted_pw:
                enable_secret = True
                line_num = root_auth.get('encrypted-password__line__', 0)
                enable_evidence = Evidence(
                    file=filename,
                    line=line_num,
                    text=self._get_line_text(content, line_num) + " [encrypted-password configured]"
                )
        
        return Authentication(
            local_authentication=local_auth,
            password_encryption=None,  # JunOS always encrypts passwords
            enable_secret_configured=enable_secret,
            local_authentication_evidence=local_auth_evidence,
            enable_secret_evidence=enable_evidence
        )
    
    def _parse_logging(self, config_tree: Dict, content: str, filename: str) -> Logging:
        """Parse logging settings"""
        enabled = None
        remote_server = None
        buffered = None
        
        enabled_evidence = None
        
        # Navigate to system.syslog
        system = config_tree.get('system', {})
        syslog_config = system.get('syslog', {}) if isinstance(system, dict) else {}
        
        if isinstance(syslog_config, dict):
            # Check for remote syslog host
            # In hierarchical format, key is "host X.X.X.X"
            for key, value in syslog_config.items():
                if key.startswith('__'):
                    continue
                # Check if key starts with "host "
                if key.startswith('host '):
                    # Extract IP from "host 10.10.10.10"
                    parts = key.split()
                    if len(parts) >= 2:
                        ip_addr = parts[1]
                        if re.match(r'\d+\.\d+\.\d+\.\d+', ip_addr):
                            enabled = True
                            remote_server = ip_addr
                            line_num = syslog_config.get(f'__line__', 0)
                            enabled_evidence = Evidence(
                                file=filename,
                                line=line_num,
                                text=self._get_line_text(content, line_num)
                            )
                            break
                # Also check for standalone "host" key with nested config
                elif key == 'host':
                    host_config = value
                    if isinstance(host_config, dict):
                        # Extract IP address (key name is the IP)
                        for host_key in host_config.keys():
                            if host_key.startswith('__'):
                                continue
                            if re.match(r'\d+\.\d+\.\d+\.\d+', host_key):
                                enabled = True
                                remote_server = host_key
                                line_num = host_config.get('__line__', 0)
                                enabled_evidence = Evidence(
                                    file=filename,
                                    line=line_num,
                                    text=self._get_line_text(content, line_num)
                                )
                                break
                    break
            
            # Check for file logging (buffered)
            file_config = syslog_config.get('file', {})
            if isinstance(file_config, dict) and file_config:
                buffered = True
                if not enabled:
                    enabled = True
                    line_num = file_config.get('__line__', 0)
                    enabled_evidence = Evidence(
                        file=filename,
                        line=line_num,
                        text=self._get_line_text(content, line_num)
                    )
        
        return Logging(
            enabled=enabled,
            remote_server=remote_server,
            buffered=buffered,
            enabled_evidence=enabled_evidence
        )
    
    def _parse_access_control(self, config_tree: Dict, content: str, filename: str) -> AccessControl:
        """Parse access control settings"""
        timeout = None
        source_filtering = None
        
        timeout_evidence = None
        source_filtering_evidence = None
        
        # Navigate to system.login.idle-timeout
        system = config_tree.get('system', {})
        login_config = system.get('login', {}) if isinstance(system, dict) else {}
        
        if isinstance(login_config, dict):
            idle_timeout = login_config.get('idle-timeout')
            if idle_timeout is not None:
                timeout = True
                line_num = login_config.get('idle-timeout__line__', 0)
                timeout_evidence = Evidence(
                    file=filename,
                    line=line_num,
                    text=self._get_line_text(content, line_num)
                )
        
        # Check for firewall filters (implies source filtering)
        firewall_config = config_tree.get('firewall', {})
        if isinstance(firewall_config, dict):
            filter_config = firewall_config.get('filter', {})
            if isinstance(filter_config, dict) and filter_config:
                source_filtering = True
                line_num = filter_config.get('__line__', 0)
                source_filtering_evidence = Evidence(
                    file=filename,
                    line=line_num,
                    text=self._get_line_text(content, line_num) + " [firewall filter detected]"
                )
        
        return AccessControl(
            timeout_configured=timeout,
            source_filtering=source_filtering,
            timeout_evidence=timeout_evidence,
            source_filtering_evidence=source_filtering_evidence
        )
