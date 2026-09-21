from .schema import (
    UnifiedSecurityModel,
    DeviceInfo,
    RemoteAccess,
    ManagementProtocols,
    Authentication,
    Logging,
    AccessControl,
    Evidence
)


def normalize_parsed_data(parsed_data: dict, vendor: str) -> UnifiedSecurityModel:
    """
    Normalize parsed configuration data to UnifiedSecurityModel
    
    Args:
        parsed_data: Parsed configuration dictionary
        vendor: Vendor name
        
    Returns:
        UnifiedSecurityModel instance
    """
    # Create UnifiedSecurityModel from parsed data
    # This is a simplified version - full implementation would map all fields
    
    device_info = DeviceInfo(
        hostname=parsed_data.get("hostname", "unknown"),
        vendor=vendor,
        model=parsed_data.get("model"),
        os_version=parsed_data.get("version"),
        device_type=parsed_data.get("device_type")
    )
    
    remote_access = RemoteAccess(
        ssh_enabled=parsed_data.get("ssh_enabled", False),
        ssh_version=parsed_data.get("ssh_version"),
        telnet_enabled=parsed_data.get("telnet_enabled", False),
        source_filtering=parsed_data.get("source_filtering", False)
    )
    
    mgmt = ManagementProtocols(
        snmp_enabled=parsed_data.get("snmp_enabled", False),
        snmp_version=parsed_data.get("snmp_version"),
        snmp_community=parsed_data.get("snmp_community"),
        http_server=parsed_data.get("http_server", False),
        https_server=parsed_data.get("https_server", False)
    )
    
    auth = Authentication(
        aaa_enabled=parsed_data.get("aaa_enabled", False),
        radius_servers=parsed_data.get("radius_servers", []),
        tacacs_servers=parsed_data.get("tacacs_servers", []),
        local_users=parsed_data.get("local_users", []),
        password_encryption=parsed_data.get("password_encryption", False),
        min_password_length=parsed_data.get("min_password_length"),
        privilege_levels=parsed_data.get("privilege_levels", {})
    )
    
    logging = Logging(
        logging_enabled=parsed_data.get("logging_enabled", False),
        log_servers=parsed_data.get("log_servers", []),
        log_level=parsed_data.get("log_level"),
        ntp_servers=parsed_data.get("ntp_servers", [])
    )
    
    access_control = AccessControl(
        access_lists=parsed_data.get("access_lists", []),
        firewall_rules=parsed_data.get("firewall_rules", []),
        interfaces=parsed_data.get("interfaces", {}),
        vlans=parsed_data.get("vlans", [])
    )
    
    evidence = Evidence(
        source_file=parsed_data.get("source_file", ""),
        line_number=0,
        raw_text=parsed_data.get("raw_config", "")
    )
    
    return UnifiedSecurityModel(
        device_info=device_info,
        remote_access=remote_access,
        management=mgmt,
        authentication=auth,
        logging=logging,
        access_control=access_control,
        evidence=evidence
    )


__all__ = [
    'UnifiedSecurityModel',
    'DeviceInfo',
    'RemoteAccess',
    'ManagementProtocols',
    'Authentication',
    'Logging',
    'AccessControl',
    'Evidence',
    'normalize_parsed_data'
]
