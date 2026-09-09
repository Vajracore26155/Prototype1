"""
Unified Security Model - Vendor-Agnostic Security Representation

This is the architectural heart of the system.
All vendor parsers must map to this common model.
All compliance rules evaluate against this model.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class Evidence(BaseModel):
    """Source evidence for a security setting"""
    file: str
    line: Optional[int] = None
    text: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "file": "cisco_config.cfg",
                "line": 12,
                "text": "transport input telnet ssh"
            }
        }


class DeviceInfo(BaseModel):
    """Device identification information"""
    hostname: Optional[str] = None
    vendor: str  # Cisco, Fortinet, Unknown
    device_type: Optional[str] = None  # router, switch, firewall
    version: Optional[str] = None
    evidence: Optional[Evidence] = None


class RemoteAccess(BaseModel):
    """Remote management access settings"""
    ssh_enabled: Optional[bool] = None
    ssh_version: Optional[int] = None
    telnet_enabled: Optional[bool] = None
    
    # Evidence tracking
    ssh_enabled_evidence: Optional[Evidence] = None
    ssh_version_evidence: Optional[Evidence] = None
    telnet_enabled_evidence: Optional[Evidence] = None


class ManagementProtocols(BaseModel):
    """Management protocol settings"""
    http_enabled: Optional[bool] = None
    https_enabled: Optional[bool] = None
    snmp_enabled: Optional[bool] = None
    
    # Evidence tracking
    http_enabled_evidence: Optional[Evidence] = None
    https_enabled_evidence: Optional[Evidence] = None
    snmp_enabled_evidence: Optional[Evidence] = None


class Authentication(BaseModel):
    """Authentication and authorization settings"""
    local_authentication: Optional[bool] = None
    password_encryption: Optional[bool] = None
    enable_secret_configured: Optional[bool] = None
    
    # Evidence tracking
    local_authentication_evidence: Optional[Evidence] = None
    password_encryption_evidence: Optional[Evidence] = None
    enable_secret_evidence: Optional[Evidence] = None


class Logging(BaseModel):
    """Logging and auditing settings"""
    enabled: Optional[bool] = None
    remote_server: Optional[str] = None
    buffered: Optional[bool] = None
    
    # Evidence tracking
    enabled_evidence: Optional[Evidence] = None


class AccessControl(BaseModel):
    """Access control and filtering settings"""
    source_filtering: Optional[bool] = None
    timeout_configured: Optional[bool] = None
    
    # Evidence tracking
    source_filtering_evidence: Optional[Evidence] = None
    timeout_evidence: Optional[Evidence] = None


class UnifiedSecurityModel(BaseModel):
    """
    Unified Security Model - The Common Security Language
    
    All vendor configurations are normalized into this model.
    All compliance rules evaluate against this model.
    
    This separation of vendor syntax from security meaning
    is the key architectural innovation.
    """
    # Device identification
    device: DeviceInfo
    
    # Security domains
    remote_access: RemoteAccess = Field(default_factory=RemoteAccess)
    management: ManagementProtocols = Field(default_factory=ManagementProtocols)
    authentication: Authentication = Field(default_factory=Authentication)
    logging: Logging = Field(default_factory=Logging)
    access_control: AccessControl = Field(default_factory=AccessControl)
    
    # Metadata
    raw_config_hash: Optional[str] = None
    normalized_at: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "device": {
                    "hostname": "CORE-01",
                    "vendor": "Cisco",
                    "device_type": "router"
                },
                "remote_access": {
                    "ssh_enabled": True,
                    "ssh_version": 2,
                    "telnet_enabled": True
                },
                "management": {
                    "http_enabled": False,
                    "https_enabled": True
                },
                "authentication": {
                    "local_authentication": True
                },
                "logging": {
                    "enabled": True,
                    "remote_server": "10.10.10.10"
                }
            }
        }
    
    def to_flat_dict(self) -> Dict[str, Any]:
        """
        Convert to flat dictionary for rule evaluation
        
        Example:
            remote_access.ssh_enabled -> True
            remote_access.telnet_enabled -> True
        """
        result = {}
        
        # Device fields
        if self.device.hostname:
            result['device.hostname'] = self.device.hostname
        result['device.vendor'] = self.device.vendor
        
        # Remote access fields
        if self.remote_access.ssh_enabled is not None:
            result['remote_access.ssh_enabled'] = self.remote_access.ssh_enabled
        if self.remote_access.ssh_version is not None:
            result['remote_access.ssh_version'] = self.remote_access.ssh_version
        if self.remote_access.telnet_enabled is not None:
            result['remote_access.telnet_enabled'] = self.remote_access.telnet_enabled
        
        # Management fields
        if self.management.http_enabled is not None:
            result['management.http_enabled'] = self.management.http_enabled
        if self.management.https_enabled is not None:
            result['management.https_enabled'] = self.management.https_enabled
        if self.management.snmp_enabled is not None:
            result['management.snmp_enabled'] = self.management.snmp_enabled
        
        # Authentication fields
        if self.authentication.local_authentication is not None:
            result['authentication.local_authentication'] = self.authentication.local_authentication
        if self.authentication.password_encryption is not None:
            result['authentication.password_encryption'] = self.authentication.password_encryption
        if self.authentication.enable_secret_configured is not None:
            result['authentication.enable_secret_configured'] = self.authentication.enable_secret_configured
        
        # Logging fields
        if self.logging.enabled is not None:
            result['logging.enabled'] = self.logging.enabled
        if self.logging.remote_server:
            result['logging.remote_server'] = self.logging.remote_server
        
        # Access control fields
        if self.access_control.timeout_configured is not None:
            result['access_control.timeout_configured'] = self.access_control.timeout_configured
        
        return result
    
    def get_evidence(self, field_path: str) -> Optional[Evidence]:
        """
        Get evidence for a specific field
        
        Args:
            field_path: Path like "remote_access.telnet_enabled"
            
        Returns:
            Evidence object or None
        """
        try:
            parts = field_path.split('.')
            if len(parts) != 2:
                return None
            
            domain, field = parts
            evidence_field = f"{field}_evidence"
            
            if domain == "remote_access":
                return getattr(self.remote_access, evidence_field, None)
            elif domain == "management":
                return getattr(self.management, evidence_field, None)
            elif domain == "authentication":
                return getattr(self.authentication, evidence_field, None)
            elif domain == "logging":
                return getattr(self.logging, evidence_field, None)
            elif domain == "access_control":
                return getattr(self.access_control, evidence_field, None)
            
            return None
        except Exception:
            return None
