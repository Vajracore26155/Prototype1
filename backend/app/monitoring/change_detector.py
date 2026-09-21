"""
Configuration Change Detection Engine
Phase 7.1: Real-time change detection and impact analysis
"""
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import difflib

from app.database import ConfigurationVersion, Device, DriftAnalysis


class ChangeType:
    """Change type constants"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class ChangeDetector:
    """
    Detects and analyzes configuration changes
    """
    
    # Critical keywords that trigger high-priority alerts
    CRITICAL_KEYWORDS = [
        'shutdown', 'no shutdown', 'enable secret', 'enable password',
        'access-list', 'permit any any', 'no logging', 'no ip verify',
        'no service password-encryption', 'transport input all'
    ]
    
    # Security-related keywords
    SECURITY_KEYWORDS = [
        'crypto', 'ipsec', 'vpn', 'authentication', 'authorization',
        'aaa', 'radius', 'tacacs', 'ssh', 'telnet', 'https', 'certificate'
    ]
    
    def detect_changes(
        self,
        baseline_version: ConfigurationVersion,
        current_version: ConfigurationVersion
    ) -> Dict:
        """
        Detect changes between two configuration versions
        
        Returns detailed change analysis with impact assessment
        """
        baseline_lines = baseline_version.content.splitlines()
        current_lines = current_version.content.splitlines()
        
        # Generate diff
        diff = list(difflib.unified_diff(
            baseline_lines,
            current_lines,
            lineterm=''
        ))
        
        # Analyze changes
        added_lines = [line[1:] for line in diff if line.startswith('+') and not line.startswith('+++')]
        removed_lines = [line[1:] for line in diff if line.startswith('-') and not line.startswith('---')]
        
        # Classify changes
        critical_changes = []
        security_changes = []
        
        for line in added_lines + removed_lines:
            line_lower = line.lower()
            
            # Check for critical changes
            for keyword in self.CRITICAL_KEYWORDS:
                if keyword in line_lower:
                    critical_changes.append({
                        "line": line.strip(),
                        "keyword": keyword,
                        "type": "added" if line in [l for l in added_lines] else "removed"
                    })
                    break
            
            # Check for security changes
            for keyword in self.SECURITY_KEYWORDS:
                if keyword in line_lower:
                    security_changes.append({
                        "line": line.strip(),
                        "keyword": keyword,
                        "type": "added" if line in [l for l in added_lines] else "removed"
                    })
                    break
        
        # Calculate change severity
        severity = self._calculate_severity(
            len(critical_changes),
            len(security_changes),
            len(added_lines),
            len(removed_lines)
        )
        
        # Calculate change score (0-100)
        total_lines = max(len(baseline_lines), 1)
        change_percentage = (len(added_lines) + len(removed_lines)) / total_lines * 100
        change_score = min(change_percentage, 100)
        
        return {
            "baseline_version_id": baseline_version.version_id,
            "current_version_id": current_version.version_id,
            "detected_at": datetime.utcnow().isoformat(),
            "severity": severity,
            "change_score": round(change_score, 2),
            "statistics": {
                "total_lines_baseline": len(baseline_lines),
                "total_lines_current": len(current_lines),
                "added_lines": len(added_lines),
                "removed_lines": len(removed_lines),
                "changed_lines": len(added_lines) + len(removed_lines),
                "change_percentage": round(change_percentage, 2)
            },
            "critical_changes": critical_changes,
            "security_changes": security_changes,
            "impact_analysis": self._analyze_impact(
                critical_changes,
                security_changes,
                added_lines,
                removed_lines
            ),
            "recommendations": self._generate_recommendations(
                severity,
                critical_changes,
                security_changes
            )
        }
    
    def _calculate_severity(
        self,
        critical_count: int,
        security_count: int,
        added_count: int,
        removed_count: int
    ) -> str:
        """Calculate change severity level"""
        if critical_count > 0:
            return ChangeType.CRITICAL
        elif security_count >= 3 or removed_count > 10:
            return ChangeType.HIGH
        elif security_count > 0 or added_count + removed_count > 5:
            return ChangeType.MEDIUM
        elif added_count + removed_count > 0:
            return ChangeType.LOW
        else:
            return ChangeType.INFO
    
    def _analyze_impact(
        self,
        critical_changes: List[Dict],
        security_changes: List[Dict],
        added_lines: List[str],
        removed_lines: List[str]
    ) -> Dict:
        """Analyze potential impact of changes"""
        impact = {
            "security_impact": "HIGH" if len(critical_changes) > 0 else "MEDIUM" if len(security_changes) > 0 else "LOW",
            "operational_impact": "HIGH" if len(removed_lines) > 10 else "MEDIUM" if len(removed_lines) > 5 else "LOW",
            "risk_level": "HIGH" if len(critical_changes) > 0 else "MEDIUM" if len(security_changes) > 2 else "LOW",
            "blast_radius": "DEVICE" if len(added_lines) + len(removed_lines) < 10 else "NETWORK",
            "affected_areas": []
        }
        
        # Identify affected areas
        all_lines = [c["line"] for c in critical_changes + security_changes]
        if any('interface' in line.lower() for line in all_lines):
            impact["affected_areas"].append("INTERFACE_CONFIG")
        if any('routing' in line.lower() or 'route' in line.lower() for line in all_lines):
            impact["affected_areas"].append("ROUTING")
        if any('acl' in line.lower() or 'access-list' in line.lower() for line in all_lines):
            impact["affected_areas"].append("ACCESS_CONTROL")
        if any('vlan' in line.lower() for line in all_lines):
            impact["affected_areas"].append("VLAN_CONFIG")
        
        return impact
    
    def _generate_recommendations(
        self,
        severity: str,
        critical_changes: List[Dict],
        security_changes: List[Dict]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if severity == ChangeType.CRITICAL:
            recommendations.append("URGENT: Review and approve changes immediately before deployment")
            recommendations.append("Run comprehensive security audit after deployment")
            recommendations.append("Monitor device closely for 24 hours post-deployment")
        
        if len(critical_changes) > 0:
            recommendations.append("Critical configuration changes detected - verify intended behavior")
            recommendations.append("Ensure rollback plan is tested and ready")
        
        if len(security_changes) > 3:
            recommendations.append("Multiple security-related changes detected - conduct security review")
            recommendations.append("Update security posture assessment")
        
        if not recommendations:
            recommendations.append("Changes appear routine - standard change management applies")
        
        return recommendations
    
    def should_trigger_drift_detection(
        self,
        change_score: float,
        severity: str
    ) -> bool:
        """Determine if change should trigger drift detection"""
        if severity in [ChangeType.CRITICAL, ChangeType.HIGH]:
            return True
        if change_score > 20:
            return True
        return False
    
    def should_send_alert(
        self,
        severity: str,
        critical_changes: List[Dict]
    ) -> bool:
        """Determine if change should trigger immediate alert"""
        if severity == ChangeType.CRITICAL:
            return True
        if len(critical_changes) > 0:
            return True
        return False
