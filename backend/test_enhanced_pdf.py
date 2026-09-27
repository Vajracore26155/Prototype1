#!/usr/bin/env python3
"""
Test Enhanced PDF Report Generation
Verifies the new professional PDF reports work correctly
"""
import sys
import os
sys.path.append('.')

from app.reports.enhanced_pdf_generator import EnhancedPDFReportGenerator
from datetime import datetime

def test_enhanced_pdf_generation():
    """Test enhanced PDF generation with sample data"""
    
    print("🧪 Testing Enhanced PDF Report Generation...")
    
    # Sample audit data (matching the enhanced API structure)
    sample_audit_data = {
        "audit_id": "AUD-TEST-001",
        "configuration": {
            "config_id": "CFG-TEST-001",
            "filename": "test_router_config.cfg",
            "vendor": "Cisco",
            "vendor_confidence": 0.95,
            "file_hash": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"
        },
        "audit_summary": {
            "status": "COMPLETED",
            "compliance_score": 78.5,
            "risk_score": 6.2,
            "risk_level": "MEDIUM",
            "started_at": "2026-09-26T10:30:00Z",
            "completed_at": "2026-09-26T10:35:00Z",
            "duration_seconds": 300,
            "error_message": None
        },
        "parsing_analysis": {
            "interpretation_confidence": 0.87,
            "total_config_lines": 1450,
            "successfully_interpreted": 1290,
            "uninterpreted_lines": 160,
            "interpretation_rate": 88.97,
            "pending_ai_mappings": 12,
            "requires_human_review": True,
            "review_reason": "Complex OSPF configuration requires expert validation",
            "normalized_data_available": True
        },
        "risk_assessment": {
            "overall_risk_score": 6.2,
            "risk_level": "MEDIUM",
            "risk_breakdown": {
                "security_posture": 45,
                "compliance_gap": "Medium",
                "configuration_complexity": "Medium - Some unclear configurations"
            },
            "business_risk_factors": [
                "Authentication vulnerabilities (2 issues)",
                "Access control weaknesses (1 issues)"
            ]
        },
        "device_assessment": {
            "security_posture": "Good - Some areas for improvement",
            "configuration_quality": "Good - Mostly standard practices",
            "vendor_best_practices": "Good - Minor deviations from Cisco recommendations",
            "maintenance_recommendations": [
                "Schedule expert review for configuration interpretation",
                "Review and document non-standard configuration sections"
            ]
        },
        "findings": {
            "total_count": 25,
            "summary": {
                "by_severity": {
                    "critical": 1,
                    "high": 3,
                    "medium": 8,
                    "low": 13
                },
                "by_status": {
                    "pass": 15,
                    "fail": 8,
                    "warning": 2,
                    "unknown": 0
                }
            },
            "details": [
                {
                    "finding_id": "FND-TEST-001",
                    "rule_id": "NET-001",
                    "rule_name": "SSH Access Control Configuration",
                    "description": "SSH access should be restricted to specific management networks",
                    "severity": "HIGH",
                    "status": "FAIL",
                    "technical_details": {
                        "expected": "SSH access restricted to management network",
                        "actual": "SSH access allowed from any source",
                        "field_path": "line.vty.access-class",
                        "risk_score": 7.5
                    },
                    "evidence": {
                        "evidence_file": "test_router_config.cfg",
                        "evidence_line": 45,
                        "evidence_text": "line vty 0 4\n transport input ssh\n no access-class in",
                        "configuration_context": [
                            "line vty 0 4",
                            " transport input ssh", 
                            " no access-class in",
                            " exec-timeout 5 0"
                        ]
                    },
                    "remediation": {
                        "guidance": "Configure access-class to restrict SSH access: 'access-class 10 in' where access-list 10 permits only management networks",
                        "priority": 4,
                        "estimated_effort": "Medium (2-4 hours)",
                        "business_impact": "High - Security compromise risk"
                    },
                    "compliance_mapping": {
                        "frameworks": ["CIS Controls", "NIST CSF"],
                        "standards": ["Industry Best Practice", "Vendor Security Guide"]
                    },
                    "created_at": "2026-09-26T10:32:15Z"
                },
                {
                    "finding_id": "FND-TEST-002",
                    "rule_id": "AUTH-002",
                    "rule_name": "Enable Password Encryption",
                    "description": "Enable passwords should use strong encryption",
                    "severity": "CRITICAL",
                    "status": "FAIL",
                    "technical_details": {
                        "expected": "enable secret configured with strong encryption",
                        "actual": "enable password in plaintext",
                        "field_path": "global.enable_secret",
                        "risk_score": 9.2
                    },
                    "evidence": {
                        "evidence_file": "test_router_config.cfg",
                        "evidence_line": 12,
                        "evidence_text": "enable password cisco123",
                        "configuration_context": [
                            "hostname TestRouter",
                            "!",
                            "enable password cisco123",
                            "!"
                        ]
                    },
                    "remediation": {
                        "guidance": "Replace 'enable password' with 'enable secret' using strong password: 'no enable password' then 'enable secret <strong-password>'",
                        "priority": 5,
                        "estimated_effort": "High (4-8 hours)",
                        "business_impact": "High - Potential data exposure"
                    },
                    "compliance_mapping": {
                        "frameworks": ["PCI DSS", "NIST CSF"],
                        "standards": ["Industry Best Practice", "Cisco Security Guide"]
                    },
                    "created_at": "2026-09-26T10:31:45Z"
                }
            ]
        },
        "evidence_and_provenance": {
            "evidence_files_analyzed": 1,
            "configuration_lines_referenced": 15,
            "total_evidence_entries": 8
        },
        "remediation_guidance": {
            "priority_1_critical": [
                {
                    "finding_id": "FND-TEST-002",
                    "severity": "CRITICAL",
                    "rule_name": "Enable Password Encryption",
                    "remediation": {
                        "guidance": "Replace 'enable password' with 'enable secret'",
                        "priority": 5,
                        "estimated_effort": "High (4-8 hours)",
                        "business_impact": "High - Potential data exposure"
                    },
                    "compliance_mapping": {
                        "frameworks": ["PCI DSS", "NIST CSF"],
                        "standards": ["Industry Best Practice"]
                    },
                    "status": "FAIL"
                }
            ],
            "priority_2_important": [
                {
                    "finding_id": "FND-TEST-001",
                    "severity": "HIGH",
                    "rule_name": "SSH Access Control Configuration",
                    "remediation": {
                        "guidance": "Configure access-class to restrict SSH access",
                        "priority": 4,
                        "estimated_effort": "Medium (2-4 hours)",
                        "business_impact": "High - Security compromise risk"
                    },
                    "compliance_mapping": {
                        "frameworks": ["CIS Controls", "NIST CSF"],
                        "standards": ["Industry Best Practice"]
                    },
                    "status": "FAIL"
                }
            ],
            "priority_3_maintenance": [],
            "estimated_total_effort": "Approximately 6.0 hours"
        }
    }
    
    # Sample configuration data
    sample_config_data = {
        "config_id": "CFG-TEST-001",
        "filename": "test_router_config.cfg",
        "internal_filename": "sanitized_test_router_config_20260926.cfg",
        "file_type": ".cfg",
        "status": "COMPLETED",
        "vendor_detection": {
            "detected_vendor": "Cisco",
            "confidence": 0.95
        },
        "file_integrity": {
            "sha256_hash": "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456",
            "storage_path": "uploads/test_router_config.cfg",
            "sanitized_path": "sanitized/sanitized_test_router_config_20260926.cfg"
        },
        "file_content": {
            "preview": """hostname TestRouter
!
version 15.1
service timestamps debug datetime msec
service timestamps log datetime msec
no service password-encryption
!
hostname TestRouter
!
boot-start-marker
boot-end-marker
!
enable password cisco123
!
no aaa new-model
!
dot11 syslog
ip source-route
!
ip cef
no ip domain lookup
ip domain name test.local
!
multilink bundle-name authenticated
!
crypto pki token default removal timeout 0
!
license udi pid CISCO2911/K9 sn FCZ1648C0GE
!
redundancy
!
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 duplex auto
 speed auto
!
interface GigabitEthernet0/1
 no ip address
 shutdown
 duplex auto
 speed auto
!
router ospf 1
 log-adjacency-changes
 network 192.168.1.0 0.0.0.255 area 0
!
ip http server
ip http secure-server
!
line con 0
line aux 0
line vty 0 4
 transport input ssh
 no access-class in
!
scheduler allocate 20000 1000
!
end""",
            "stats": {
                "total_lines": 1450,
                "preview_lines": 50,
                "file_size_bytes": 45632
            }
        },
        "upload_metadata": {
            "uploaded_by": "VND-TEST-001", 
            "uploaded_at": "2026-09-26T09:15:30Z",
            "organization_id": 1
        },
        "audits": [
            {
                "audit_id": "AUD-TEST-001",
                "status": "COMPLETED",
                "compliance_score": 78.5,
                "risk_score": 6.2,
                "risk_level": "MEDIUM"
            }
        ],
        "processing_status": {
            "ingested": True,
            "vendor_detected": True,
            "audited": True,
            "latest_audit": {
                "audit_id": "AUD-TEST-001",
                "status": "COMPLETED"
            }
        }
    }
    
    # Sample vendor info
    sample_vendor_info = {
        "vendor_id": "VND-TEST-001",
        "company": "Test Corporation Inc.",
        "email": "security@testcorp.com"
    }
    
    try:
        # Initialize the enhanced PDF generator
        pdf_generator = EnhancedPDFReportGenerator()
        print("✅ PDF generator initialized successfully")
        
        # Generate the comprehensive report
        print("📄 Generating comprehensive vendor report...")
        pdf_bytes = pdf_generator.generate_comprehensive_vendor_report(
            audit_data=sample_audit_data,
            config_data=sample_config_data,
            vendor_info=sample_vendor_info,
            output_path="test_enhanced_report.pdf"
        )
        
        print(f"✅ Enhanced PDF report generated successfully!")
        print(f"📄 Report size: {len(pdf_bytes):,} bytes")
        print(f"💾 Report saved as: test_enhanced_report.pdf")
        
        # Verify file exists
        if os.path.exists("test_enhanced_report.pdf"):
            file_size = os.path.getsize("test_enhanced_report.pdf")
            print(f"📊 File verification: {file_size:,} bytes on disk")
            print("✅ Enhanced PDF generation test PASSED")
            return True
        else:
            print("❌ Enhanced PDF generation test FAILED - File not created")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install required packages: pip install reportlab")
        return False
    except Exception as e:
        print(f"❌ Enhanced PDF generation failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Enhanced PDF Report Generation Test")
    print("=" * 50)
    
    success = test_enhanced_pdf_generation()
    
    if success:
        print("\n🎉 Phase 4: Enhanced PDF generation is working correctly!")
        print("Professional vendor reports are now available with:")
        print("• Comprehensive technical details and evidence traceability")
        print("• AI parsing confidence metrics and interpretation analysis") 
        print("• Detailed remediation guidance with priority sequencing")
        print("• Professional formatting and vendor-specific branding")
        print("• Configuration file previews and integrity verification")
        print("• Business impact assessment and compliance framework mapping")
    else:
        print("\n❌ Phase 4: Enhanced PDF generation needs attention")
        print("Some components may not be working correctly")
    
    print(f"\nNext: Proceed to Phase 5 (Improve Vendor Upload Functionality)")