"""
Deviation Engine - Configuration Comparison
Phase 0 Critical Feature for Before/After Analysis
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import Audit, Configuration


class DeviationEngine:
    """
    Compares two configuration audits to detect deviations
    
    Core SIH Requirement: Before/After comparison for remediation validation
    """
    
    def compare_audits(
        self,
        baseline_audit_id: str,
        current_audit_id: str,
        db: Session
    ) -> Dict[str, Any]:
        """
        Compare two audits and generate deviation report
        
        Returns:
            - compliance_drift: Change in compliance score
            - new_violations: Findings that failed in current but passed in baseline
            - resolved_violations: Findings that passed in current but failed in baseline
            - field_deviations: Field-level changes in UnifiedSecurityModel
        """
        # Get both audits
        baseline = db.query(Audit).filter(Audit.audit_id == baseline_audit_id).first()
        current = db.query(Audit).filter(Audit.audit_id == current_audit_id).first()
        
        if not baseline or not current:
            raise ValueError("One or both audits not found")
        
        # Calculate compliance drift
        compliance_drift = (current.compliance_score or 0) - (baseline.compliance_score or 0)
        
        # Calculate risk drift
        risk_drift = (current.risk_score or 0) - (baseline.risk_score or 0)
        
        # Compare findings
        from app.database import Finding
        baseline_findings = db.query(Finding).filter(Finding.audit_id == baseline.id).all()
        current_findings = db.query(Finding).filter(Finding.audit_id == current.id).all()
        
        # Group by rule_id for comparison
        baseline_by_rule = {f.rule_id: f for f in baseline_findings}
        current_by_rule = {f.rule_id: f for f in current_findings}
        
        new_violations = []
        resolved_violations = []
        
        for rule_id, current_finding in current_by_rule.items():
            baseline_finding = baseline_by_rule.get(rule_id)
            
            if baseline_finding:
                # Check if status changed
                if baseline_finding.status == "PASS" and current_finding.status == "FAIL":
                    new_violations.append({
                        "rule_id": rule_id,
                        "title": current_finding.title,
                        "severity": current_finding.severity,
                        "baseline_value": baseline_finding.actual,
                        "current_value": current_finding.actual
                    })
                elif baseline_finding.status == "FAIL" and current_finding.status == "PASS":
                    resolved_violations.append({
                        "rule_id": rule_id,
                        "title": current_finding.title,
                        "severity": current_finding.severity,
                        "baseline_value": baseline_finding.actual,
                        "current_value": current_finding.actual
                    })
        
        # Compare normalized data if available
        field_deviations = []
        if baseline.normalized_data and current.normalized_data:
            field_deviations = self._compare_normalized_models(
                baseline.normalized_data,
                current.normalized_data
            )
        
        return {
            "comparison_id": f"CMP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "baseline_audit_id": baseline_audit_id,
            "current_audit_id": current_audit_id,
            "compliance_drift": round(compliance_drift, 2),
            "risk_drift": round(risk_drift, 2),
            "baseline_compliance": baseline.compliance_score,
            "current_compliance": current.compliance_score,
            "new_violations_count": len(new_violations),
            "resolved_violations_count": len(resolved_violations),
            "new_violations": new_violations,
            "resolved_violations": resolved_violations,
            "field_deviations": field_deviations,
            "status": self._assess_status(compliance_drift, len(new_violations), len(resolved_violations)),
            "compared_at": datetime.utcnow().isoformat()
        }
    
    def _compare_normalized_models(
        self,
        baseline_data: Dict[str, Any],
        current_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Compare two UnifiedSecurityModel JSON objects field by field
        """
        deviations = []
        
        # Compare key security fields
        security_fields = [
            "remote_access.ssh_enabled",
            "remote_access.telnet_enabled",
            "remote_access.ssh_version",
            "management.http_enabled",
            "management.https_enabled",
            "authentication.password_encryption",
            "logging.enabled"
        ]
        
        for field in security_fields:
            baseline_val = self._get_nested_value(baseline_data, field)
            current_val = self._get_nested_value(current_data, field)
            
            if baseline_val != current_val:
                deviations.append({
                    "field": field,
                    "baseline_value": baseline_val,
                    "current_value": current_val,
                    "changed": True
                })
        
        return deviations
    
    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get value from nested dict using dot notation"""
        keys = path.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value
    
    def _assess_status(
        self,
        compliance_drift: float,
        new_violations: int,
        resolved_violations: int
    ) -> str:
        """
        Assess overall status of configuration change
        """
        if compliance_drift > 0 and new_violations == 0:
            return "IMPROVED"
        elif compliance_drift < 0 or new_violations > 0:
            return "DEGRADED"
        elif resolved_violations > 0:
            return "IMPROVED"
        else:
            return "NO_CHANGE"
