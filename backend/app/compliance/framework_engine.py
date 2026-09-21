"""
Multi-Framework Compliance Engine

Supports multiple compliance frameworks:
- CIS Benchmarks (Center for Internet Security)
- NIST 800-53 (National Institute of Standards and Technology)
- DISA STIG (Security Technical Implementation Guides)
- ISO 27001/27002 (International Standards)

Phase 2 Core Features:
- Framework versioning
- Control mapping across frameworks
- Technical fact layer (deterministic rules)
- Multi-framework assessment
- Control traceability
"""
from typing import Dict, List, Optional, Set
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class FrameworkType(str, Enum):
    """Supported compliance frameworks"""
    CIS = "CIS"
    NIST = "NIST_800_53"
    STIG = "DISA_STIG"
    ISO = "ISO_27001"


class ControlSeverity(str, Enum):
    """Control severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFORMATIONAL = "INFORMATIONAL"


@dataclass
class FrameworkVersion:
    """Framework version information"""
    framework: FrameworkType
    version: str
    release_date: str
    description: str


@dataclass
class ComplianceControl:
    """Individual compliance control"""
    control_id: str
    framework: FrameworkType
    version: str
    title: str
    description: str
    severity: ControlSeverity
    
    # Technical requirements
    technical_checks: List[str]  # Field paths to check
    expected_values: Dict[str, any]
    
    # Cross-framework mappings
    mapped_controls: Dict[FrameworkType, List[str]]
    
    # Metadata
    category: str
    tags: List[str]
    references: List[str]


@dataclass
class FrameworkAssessment:
    """Assessment results for a framework"""
    framework: FrameworkType
    version: str
    total_controls: int
    applicable_controls: int
    compliant_controls: int
    non_compliant_controls: int
    not_applicable_controls: int
    compliance_percentage: float
    control_results: List[Dict]
    assessed_at: str


class MultiFrameworkEngine:
    """
    Multi-framework compliance assessment engine
    
    Provides unified assessment across multiple frameworks
    with control mapping and traceability
    """
    
    def __init__(self):
        self.frameworks = self._load_frameworks()
        self.controls = self._load_controls()
        self.control_mappings = self._build_control_mappings()
    
    def _load_frameworks(self) -> Dict[FrameworkType, FrameworkVersion]:
        """Load supported framework versions"""
        return {
            FrameworkType.CIS: FrameworkVersion(
                framework=FrameworkType.CIS,
                version="8.0",
                release_date="2021-05-18",
                description="CIS Controls v8.0 - Critical Security Controls"
            ),
            FrameworkType.NIST: FrameworkVersion(
                framework=FrameworkType.NIST,
                version="Rev 5",
                release_date="2020-09-23",
                description="NIST SP 800-53 Rev 5 - Security and Privacy Controls"
            ),
            FrameworkType.STIG: FrameworkVersion(
                framework=FrameworkType.STIG,
                version="V2R1",
                release_date="2023-01-27",
                description="DISA STIG - Network Device Security Requirements"
            ),
            FrameworkType.ISO: FrameworkVersion(
                framework=FrameworkType.ISO,
                version="2022",
                release_date="2022-10-25",
                description="ISO/IEC 27001:2022 - Information Security Management"
            )
        }
    
    def _load_controls(self) -> Dict[str, ComplianceControl]:
        """
        Load compliance controls from all frameworks
        
        Returns dict keyed by f"{framework}:{control_id}"
        """
        controls = {}
        
        # CIS Controls
        controls["CIS:4.3"] = ComplianceControl(
            control_id="4.3",
            framework=FrameworkType.CIS,
            version="8.0",
            title="Configure Data Access Control Lists",
            description="Configure data access control lists based on a user's need to know",
            severity=ControlSeverity.HIGH,
            technical_checks=["access_control.source_filtering"],
            expected_values={"access_control.source_filtering": True},
            mapped_controls={
                FrameworkType.NIST: ["AC-3", "AC-4"],
                FrameworkType.ISO: ["A.9.1.2", "A.9.4.1"],
                FrameworkType.STIG: ["NET-MGMT-001"]
            },
            category="Access Control",
            tags=["network", "access-control", "filtering"],
            references=["CIS Controls v8.0 - Safeguard 4.3"]
        )
        
        controls["CIS:12.4"] = ComplianceControl(
            control_id="12.4",
            framework=FrameworkType.CIS,
            version="8.0",
            title="Deny Communication Over Unauthorized Ports",
            description="Deny communication over unauthorized TCP or UDP ports",
            severity=ControlSeverity.HIGH,
            technical_checks=["remote_access.telnet_enabled"],
            expected_values={"remote_access.telnet_enabled": False},
            mapped_controls={
                FrameworkType.NIST: ["SC-7", "SC-8"],
                FrameworkType.ISO: ["A.13.1.3"],
                FrameworkType.STIG: ["NET-SSH-001", "NET-TELNET-001"]
            },
            category="Network Security",
            tags=["network", "ports", "telnet"],
            references=["CIS Controls v8.0 - Safeguard 12.4"]
        )
        
        controls["CIS:4.1"] = ComplianceControl(
            control_id="4.1",
            framework=FrameworkType.CIS,
            version="8.0",
            title="Establish and Maintain a Secure Configuration Process",
            description="Establish and maintain a secure configuration process",
            severity=ControlSeverity.MEDIUM,
            technical_checks=["authentication.local_authentication", "authentication.enable_secret_configured"],
            expected_values={
                "authentication.local_authentication": True,
                "authentication.enable_secret_configured": True
            },
            mapped_controls={
                FrameworkType.NIST: ["CM-2", "CM-6", "IA-5"],
                FrameworkType.ISO: ["A.9.2.1", "A.12.1.2"],
                FrameworkType.STIG: ["NET-AUTH-001"]
            },
            category="Configuration Management",
            tags=["configuration", "authentication"],
            references=["CIS Controls v8.0 - Safeguard 4.1"]
        )
        
        # NIST 800-53 Controls
        controls["NIST:AC-3"] = ComplianceControl(
            control_id="AC-3",
            framework=FrameworkType.NIST,
            version="Rev 5",
            title="Access Enforcement",
            description="Enforce approved authorizations for logical access to information and system resources",
            severity=ControlSeverity.HIGH,
            technical_checks=["access_control.source_filtering", "authentication.local_authentication"],
            expected_values={
                "access_control.source_filtering": True,
                "authentication.local_authentication": True
            },
            mapped_controls={
                FrameworkType.CIS: ["4.3", "4.1"],
                FrameworkType.ISO: ["A.9.1.2", "A.9.4.1"],
                FrameworkType.STIG: ["NET-MGMT-001"]
            },
            category="Access Control",
            tags=["access-control", "authorization"],
            references=["NIST SP 800-53 Rev 5 - AC-3"]
        )
        
        controls["NIST:SC-8"] = ComplianceControl(
            control_id="SC-8",
            framework=FrameworkType.NIST,
            version="Rev 5",
            title="Transmission Confidentiality and Integrity",
            description="Protect the confidentiality and integrity of transmitted information",
            severity=ControlSeverity.HIGH,
            technical_checks=["remote_access.telnet_enabled", "remote_access.ssh_enabled", "management.http_enabled"],
            expected_values={
                "remote_access.telnet_enabled": False,
                "remote_access.ssh_enabled": True,
                "management.http_enabled": False
            },
            mapped_controls={
                FrameworkType.CIS: ["12.4", "3.10"],
                FrameworkType.ISO: ["A.13.1.1", "A.13.1.3"],
                FrameworkType.STIG: ["NET-SSH-001", "NET-TELNET-001"]
            },
            category="System and Communications Protection",
            tags=["encryption", "transmission", "confidentiality"],
            references=["NIST SP 800-53 Rev 5 - SC-8"]
        )
        
        controls["NIST:IA-5"] = ComplianceControl(
            control_id="IA-5",
            framework=FrameworkType.NIST,
            version="Rev 5",
            title="Authenticator Management",
            description="Manage information system authenticators",
            severity=ControlSeverity.HIGH,
            technical_checks=["authentication.enable_secret_configured", "authentication.password_encryption"],
            expected_values={
                "authentication.enable_secret_configured": True
            },
            mapped_controls={
                FrameworkType.CIS: ["4.1", "5.2"],
                FrameworkType.ISO: ["A.9.2.1", "A.9.4.3"],
                FrameworkType.STIG: ["NET-AUTH-001", "NET-AUTH-002"]
            },
            category="Identification and Authentication",
            tags=["authentication", "passwords"],
            references=["NIST SP 800-53 Rev 5 - IA-5"]
        )
        
        controls["NIST:AU-4"] = ComplianceControl(
            control_id="AU-4",
            framework=FrameworkType.NIST,
            version="Rev 5",
            title="Audit Log Storage Capacity",
            description="Allocate audit log storage capacity",
            severity=ControlSeverity.MEDIUM,
            technical_checks=["logging.enabled", "logging.remote_server"],
            expected_values={
                "logging.enabled": True
            },
            mapped_controls={
                FrameworkType.CIS: ["8.2", "8.5"],
                FrameworkType.ISO: ["A.12.4.1"],
                FrameworkType.STIG: ["NET-LOG-001"]
            },
            category="Audit and Accountability",
            tags=["logging", "audit"],
            references=["NIST SP 800-53 Rev 5 - AU-4"]
        )
        
        # DISA STIG Controls
        controls["STIG:NET-SSH-001"] = ComplianceControl(
            control_id="NET-SSH-001",
            framework=FrameworkType.STIG,
            version="V2R1",
            title="Network devices must use SSH for remote access",
            description="Network devices must be configured to use SSH version 2 for remote management access",
            severity=ControlSeverity.CRITICAL,
            technical_checks=["remote_access.ssh_enabled", "remote_access.ssh_version"],
            expected_values={
                "remote_access.ssh_enabled": True,
                "remote_access.ssh_version": 2
            },
            mapped_controls={
                FrameworkType.CIS: ["12.4"],
                FrameworkType.NIST: ["SC-8", "SC-13"],
                FrameworkType.ISO: ["A.13.1.1"]
            },
            category="Remote Access",
            tags=["ssh", "remote-access", "encryption"],
            references=["STIG ID: V-230001", "SRG-NET-000019"]
        )
        
        controls["STIG:NET-TELNET-001"] = ComplianceControl(
            control_id="NET-TELNET-001",
            framework=FrameworkType.STIG,
            version="V2R1",
            title="Telnet must be disabled",
            description="Network devices must have Telnet disabled for management access",
            severity=ControlSeverity.CRITICAL,
            technical_checks=["remote_access.telnet_enabled"],
            expected_values={"remote_access.telnet_enabled": False},
            mapped_controls={
                FrameworkType.CIS: ["12.4"],
                FrameworkType.NIST: ["SC-8"],
                FrameworkType.ISO: ["A.13.1.3"]
            },
            category="Remote Access",
            tags=["telnet", "insecure-protocols"],
            references=["STIG ID: V-230002", "SRG-NET-000020"]
        )
        
        controls["STIG:NET-MGMT-001"] = ComplianceControl(
            control_id="NET-MGMT-001",
            framework=FrameworkType.STIG,
            version="V2R1",
            title="Management access must be restricted",
            description="Network devices must restrict management access to authorized sources",
            severity=ControlSeverity.HIGH,
            technical_checks=["access_control.source_filtering"],
            expected_values={"access_control.source_filtering": True},
            mapped_controls={
                FrameworkType.CIS: ["4.3"],
                FrameworkType.NIST: ["AC-3", "AC-4"],
                FrameworkType.ISO: ["A.9.1.2"]
            },
            category="Access Control",
            tags=["access-control", "management"],
            references=["STIG ID: V-230003", "SRG-NET-000021"]
            )
        
        controls["STIG:NET-AUTH-001"] = ComplianceControl(
            control_id="NET-AUTH-001",
            framework=FrameworkType.STIG,
            version="V2R1",
            title="Local authentication must be configured",
            description="Network devices must have local authentication configured",
            severity=ControlSeverity.HIGH,
            technical_checks=["authentication.local_authentication", "authentication.enable_secret_configured"],
            expected_values={
                "authentication.local_authentication": True,
                "authentication.enable_secret_configured": True
            },
            mapped_controls={
                FrameworkType.CIS: ["4.1"],
                FrameworkType.NIST: ["IA-5", "IA-2"],
                FrameworkType.ISO: ["A.9.2.1"]
            },
            category="Authentication",
            tags=["authentication", "local-accounts"],
            references=["STIG ID: V-230005", "SRG-NET-000023"]
        )
        
        controls["STIG:NET-LOG-001"] = ComplianceControl(
            control_id="NET-LOG-001",
            framework=FrameworkType.STIG,
            version="V2R1",
            title="Audit logging must be enabled",
            description="Network devices must have audit logging enabled and sent to centralized log server",
            severity=ControlSeverity.MEDIUM,
            technical_checks=["logging.enabled", "logging.remote_server"],
            expected_values={
                "logging.enabled": True
            },
            mapped_controls={
                FrameworkType.CIS: ["8.2"],
                FrameworkType.NIST: ["AU-4", "AU-9"],
                FrameworkType.ISO: ["A.12.4.1"]
            },
            category="Audit and Logging",
            tags=["logging", "audit", "syslog"],
            references=["STIG ID: V-230010", "SRG-NET-000028"]
        )
        
        # ISO 27001 Controls
        controls["ISO:A.9.1.2"] = ComplianceControl(
            control_id="A.9.1.2",
            framework=FrameworkType.ISO,
            version="2022",
            title="Access to networks and network services",
            description="Users shall only be provided with access to network and network services that they have been specifically authorized to use",
            severity=ControlSeverity.HIGH,
            technical_checks=["access_control.source_filtering", "authentication.local_authentication"],
            expected_values={
                "access_control.source_filtering": True,
                "authentication.local_authentication": True
            },
            mapped_controls={
                FrameworkType.CIS: ["4.3", "4.1"],
                FrameworkType.NIST: ["AC-3"],
                FrameworkType.STIG: ["NET-MGMT-001"]
            },
            category="Access Control",
            tags=["access-control", "network-services"],
            references=["ISO/IEC 27001:2022 - A.9.1.2"]
        )
        
        controls["ISO:A.13.1.1"] = ComplianceControl(
            control_id="A.13.1.1",
            framework=FrameworkType.ISO,
            version="2022",
            title="Network controls",
            description="Networks shall be managed and controlled to protect information in systems and applications",
            severity=ControlSeverity.HIGH,
            technical_checks=["remote_access.ssh_enabled", "remote_access.telnet_enabled"],
            expected_values={
                "remote_access.ssh_enabled": True,
                "remote_access.telnet_enabled": False
            },
            mapped_controls={
                FrameworkType.CIS: ["12.4"],
                FrameworkType.NIST: ["SC-8"],
                FrameworkType.STIG: ["NET-SSH-001"]
            },
            category="Communications Security",
            tags=["network-security", "encryption"],
            references=["ISO/IEC 27001:2022 - A.13.1.1"]
        )
        
        controls["ISO:A.9.2.1"] = ComplianceControl(
            control_id="A.9.2.1",
            framework=FrameworkType.ISO,
            version="2022",
            title="User registration and de-registration",
            description="A formal user registration and de-registration process shall be implemented",
            severity=ControlSeverity.MEDIUM,
            technical_checks=["authentication.local_authentication", "authentication.enable_secret_configured"],
            expected_values={
                "authentication.local_authentication": True,
                "authentication.enable_secret_configured": True
            },
            mapped_controls={
                FrameworkType.CIS: ["4.1", "5.2"],
                FrameworkType.NIST: ["IA-5"],
                FrameworkType.STIG: ["NET-AUTH-001"]
            },
            category="Access Control",
            tags=["user-management", "authentication"],
            references=["ISO/IEC 27001:2022 - A.9.2.1"]
        )
        
        controls["ISO:A.12.4.1"] = ComplianceControl(
            control_id="A.12.4.1",
            framework=FrameworkType.ISO,
            version="2022",
            title="Event logging",
            description="Event logs recording user activities, exceptions, faults and information security events shall be produced, kept and regularly reviewed",
            severity=ControlSeverity.MEDIUM,
            technical_checks=["logging.enabled"],
            expected_values={"logging.enabled": True},
            mapped_controls={
                FrameworkType.CIS: ["8.2"],
                FrameworkType.NIST: ["AU-4"],
                FrameworkType.STIG: ["NET-LOG-001"]
            },
            category="Operations Security",
            tags=["logging", "audit"],
            references=["ISO/IEC 27001:2022 - A.12.4.1"]
        )
        
        return controls
    
    def _build_control_mappings(self) -> Dict[str, Set[str]]:
        """
        Build bidirectional control mappings
        
        Returns dict mapping control_key to set of related control_keys
        """
        mappings = {}
        
        for control_key, control in self.controls.items():
            # Initialize set for this control
            if control_key not in mappings:
                mappings[control_key] = set()
            
            # Add all mapped controls
            for framework, control_ids in control.mapped_controls.items():
                for control_id in control_ids:
                    mapped_key = f"{framework.value}:{control_id}"
                    mappings[control_key].add(mapped_key)
                    
                    # Ensure bidirectional mapping
                    if mapped_key not in mappings:
                        mappings[mapped_key] = set()
                    mappings[mapped_key].add(control_key)
        
        return mappings
    
    def assess_framework(
        self,
        framework: FrameworkType,
        unified_model_dict: Dict[str, any]
    ) -> FrameworkAssessment:
        """
        Assess compliance against a specific framework
        
        Args:
            framework: Framework to assess against
            unified_model_dict: Flattened UnifiedSecurityModel dictionary
            
        Returns:
            FrameworkAssessment with results
        """
        framework_version = self.frameworks[framework]
        
        # Get all controls for this framework
        framework_controls = [
            c for c in self.controls.values()
            if c.framework == framework
        ]
        
        control_results = []
        compliant = 0
        non_compliant = 0
        not_applicable = 0
        
        for control in framework_controls:
            result = self._evaluate_control(control, unified_model_dict)
            control_results.append(result)
            
            if result['status'] == 'PASS':
                compliant += 1
            elif result['status'] == 'FAIL':
                non_compliant += 1
            elif result['status'] == 'N/A':
                not_applicable += 1
        
        total_controls = len(framework_controls)
        applicable_controls = total_controls - not_applicable
        
        if applicable_controls > 0:
            compliance_percentage = (compliant / applicable_controls) * 100
        else:
            compliance_percentage = 0.0
        
        return FrameworkAssessment(
            framework=framework,
            version=framework_version.version,
            total_controls=total_controls,
            applicable_controls=applicable_controls,
            compliant_controls=compliant,
            non_compliant_controls=non_compliant,
            not_applicable_controls=not_applicable,
            compliance_percentage=compliance_percentage,
            control_results=control_results,
            assessed_at=datetime.utcnow().isoformat()
        )
    
    def _evaluate_control(
        self,
        control: ComplianceControl,
        unified_model_dict: Dict[str, any]
    ) -> Dict:
        """
        Evaluate a single control
        
        Returns dict with status, findings, and metadata
        """
        checks_passed = 0
        checks_failed = 0
        checks_na = 0
        findings = []
        
        for check_field in control.technical_checks:
            actual_value = unified_model_dict.get(check_field)
            expected_value = control.expected_values.get(check_field)
            
            # Check if field is applicable (has a value)
            if actual_value is None:
                checks_na += 1
                findings.append({
                    'field': check_field,
                    'status': 'N/A',
                    'message': f'Field not configured or detected'
                })
                continue
            
            # Compare actual vs expected
            if expected_value is not None and actual_value == expected_value:
                checks_passed += 1
                findings.append({
                    'field': check_field,
                    'status': 'PASS',
                    'actual': actual_value,
                    'expected': expected_value
                })
            else:
                checks_failed += 1
                findings.append({
                    'field': check_field,
                    'status': 'FAIL',
                    'actual': actual_value,
                    'expected': expected_value,
                    'message': f'Expected {expected_value}, found {actual_value}'
                })
        
        # Determine overall status
        if checks_failed > 0:
            status = 'FAIL'
        elif checks_passed > 0:
            status = 'PASS'
        else:
            status = 'N/A'
        
        return {
            'control_id': control.control_id,
            'title': control.title,
            'severity': control.severity.value,
            'status': status,
            'checks_passed': checks_passed,
            'checks_failed': checks_failed,
            'checks_na': checks_na,
            'findings': findings,
            'category': control.category,
            'mapped_controls': control.mapped_controls
        }
    
    def assess_all_frameworks(
        self,
        unified_model_dict: Dict[str, any]
    ) -> Dict[FrameworkType, FrameworkAssessment]:
        """
        Assess compliance against all supported frameworks
        
        Returns dict mapping framework to assessment results
        """
        results = {}
        
        for framework in FrameworkType:
            results[framework] = self.assess_framework(framework, unified_model_dict)
        
        return results
    
    def get_control_mappings(self, control_key: str) -> Set[str]:
        """Get all controls mapped to the specified control"""
        return self.control_mappings.get(control_key, set())
    
    def get_framework_summary(self) -> Dict:
        """Get summary of all loaded frameworks and controls"""
        summary = {
            'frameworks': {},
            'total_controls': len(self.controls),
            'controls_by_framework': {}
        }
        
        for framework, version in self.frameworks.items():
            summary['frameworks'][framework.value] = {
                'version': version.version,
                'release_date': version.release_date,
                'description': version.description
            }
            
            framework_controls = [
                c for c in self.controls.values()
                if c.framework == framework
            ]
            summary['controls_by_framework'][framework.value] = len(framework_controls)
        
        return summary
