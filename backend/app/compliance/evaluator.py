"""
Compliance Engine - Rule Evaluation

Evaluates the Unified Security Model against compliance rules
"""
import os
import yaml
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from app.normalization.schema import UnifiedSecurityModel, Evidence


class ComplianceStatus(str, Enum):
    """Compliance check status"""
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"


class Severity(str, Enum):
    """Finding severity levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


@dataclass
class ComplianceRule:
    """Compliance rule definition"""
    id: str
    name: str
    description: str
    category: str
    severity: Severity
    field: str  # Path like "remote_access.telnet_enabled"
    operator: str  # equals, not_equals, greater_than, less_than, contains
    expected: Any
    explanation: str
    optional: bool = False
    references: List[str] = None


@dataclass
class ComplianceResult:
    """Result of a single rule evaluation"""
    rule_id: str
    rule_name: str
    status: ComplianceStatus
    severity: Severity
    category: str
    field: str
    expected: Any
    actual: Any
    evidence: Optional[Evidence]
    explanation: str
    optional: bool


class ComplianceEvaluator:
    """
    Evaluates security configurations against compliance rules
    
    The evaluator is vendor-agnostic - it operates purely on
    the Unified Security Model.
    """
    
    def __init__(self, rules_path: Optional[str] = None):
        """
        Initialize evaluator
        
        Args:
            rules_path: Path to rules YAML file (defaults to bundled rules)
        """
        if rules_path is None:
            # Use bundled rules
            rules_path = os.path.join(
                os.path.dirname(__file__),
                'rules.yaml'
            )
        
        self.rules = self._load_rules(rules_path)
    
    def _load_rules(self, path: str) -> List[ComplianceRule]:
        """Load rules from YAML file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            rules = []
            for rule_data in data.get('rules', []):
                rule = ComplianceRule(
                    id=rule_data['id'],
                    name=rule_data['name'],
                    description=rule_data['description'],
                    category=rule_data['category'],
                    severity=Severity(rule_data['severity']),
                    field=rule_data['field'],
                    operator=rule_data['operator'],
                    expected=rule_data['expected'],
                    explanation=rule_data['explanation'],
                    optional=rule_data.get('optional', False),
                    references=rule_data.get('references', [])
                )
                rules.append(rule)
            
            return rules
            
        except Exception as e:
            raise Exception(f"Failed to load compliance rules: {str(e)}")
    
    def evaluate(self, model: UnifiedSecurityModel) -> List[ComplianceResult]:
        """
        Evaluate configuration against all rules
        
        Args:
            model: Unified Security Model to evaluate
            
        Returns:
            List of ComplianceResult objects
        """
        results = []
        flat_model = model.to_flat_dict()
        
        for rule in self.rules:
            result = self._evaluate_rule(rule, model, flat_model)
            results.append(result)
        
        return results
    
    def _evaluate_rule(
        self,
        rule: ComplianceRule,
        model: UnifiedSecurityModel,
        flat_model: Dict[str, Any]
    ) -> ComplianceResult:
        """Evaluate a single rule"""
        
        # Get actual value from model
        actual_value = flat_model.get(rule.field)
        
        # Get evidence
        evidence = model.get_evidence(rule.field)
        
        # If value is None, determine status
        if actual_value is None:
            if rule.optional:
                status = ComplianceStatus.NOT_APPLICABLE
            else:
                status = ComplianceStatus.UNKNOWN
            
            return ComplianceResult(
                rule_id=rule.id,
                rule_name=rule.name,
                status=status,
                severity=rule.severity,
                category=rule.category,
                field=rule.field,
                expected=rule.expected,
                actual=None,
                evidence=evidence,
                explanation=rule.explanation,
                optional=rule.optional
            )
        
        # Evaluate based on operator
        status = self._apply_operator(
            rule.operator,
            actual_value,
            rule.expected
        )
        
        # If rule is optional and failed, downgrade to WARNING
        if status == ComplianceStatus.FAIL and rule.optional:
            status = ComplianceStatus.WARNING
        
        return ComplianceResult(
            rule_id=rule.id,
            rule_name=rule.name,
            status=status,
            severity=rule.severity,
            category=rule.category,
            field=rule.field,
            expected=rule.expected,
            actual=actual_value,
            evidence=evidence,
            explanation=rule.explanation,
            optional=rule.optional
        )
    
    def _apply_operator(self, operator: str, actual: Any, expected: Any) -> ComplianceStatus:
        """Apply comparison operator"""
        try:
            if operator == "equals":
                return ComplianceStatus.PASS if actual == expected else ComplianceStatus.FAIL
            elif operator == "not_equals":
                return ComplianceStatus.PASS if actual != expected else ComplianceStatus.FAIL
            elif operator == "greater_than":
                return ComplianceStatus.PASS if actual > expected else ComplianceStatus.FAIL
            elif operator == "less_than":
                return ComplianceStatus.PASS if actual < expected else ComplianceStatus.FAIL
            elif operator == "contains":
                return ComplianceStatus.PASS if expected in actual else ComplianceStatus.FAIL
            else:
                return ComplianceStatus.UNKNOWN
        except Exception:
            return ComplianceStatus.UNKNOWN
    
    def get_summary(self, results: List[ComplianceResult]) -> Dict[str, Any]:
        """
        Generate summary statistics from results
        
        Returns:
            Dictionary with counts and compliance score
        """
        total = len(results)
        passed = sum(1 for r in results if r.status == ComplianceStatus.PASS)
        failed = sum(1 for r in results if r.status == ComplianceStatus.FAIL)
        warning = sum(1 for r in results if r.status == ComplianceStatus.WARNING)
        not_applicable = sum(1 for r in results if r.status == ComplianceStatus.NOT_APPLICABLE)
        unknown = sum(1 for r in results if r.status == ComplianceStatus.UNKNOWN)
        
        # Calculate compliance score
        # Only count applicable rules (not NA or unknown)
        applicable = total - not_applicable - unknown
        if applicable > 0:
            compliance_score = (passed / applicable) * 100
        else:
            compliance_score = 0.0
        
        # Count by severity
        critical = sum(1 for r in results if r.severity == Severity.CRITICAL and r.status == ComplianceStatus.FAIL)
        high = sum(1 for r in results if r.severity == Severity.HIGH and r.status == ComplianceStatus.FAIL)
        medium = sum(1 for r in results if r.severity == Severity.MEDIUM and r.status == ComplianceStatus.FAIL)
        low = sum(1 for r in results if r.severity == Severity.LOW and r.status == ComplianceStatus.FAIL)
        
        return {
            "total_rules": total,
            "passed": passed,
            "failed": failed,
            "warning": warning,
            "not_applicable": not_applicable,
            "unknown": unknown,
            "compliance_score": round(compliance_score, 2),
            "findings_by_severity": {
                "critical": critical,
                "high": high,
                "medium": medium,
                "low": low
            }
        }
