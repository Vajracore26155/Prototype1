"""
Drift Detection Engine
Phase 5: Configuration drift analysis
"""
import difflib
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

from app.normalization import UnifiedSecurityModel


@dataclass
class FieldDrift:
    """Represents drift in a single configuration field"""
    field_path: str
    baseline_value: any
    current_value: any
    drift_type: str  # ADDED, REMOVED, MODIFIED
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    security_impact: str


@dataclass
class DriftResult:
    """Result of drift analysis"""
    drift_score: float  # 0-100
    drift_severity: str  # NONE, LOW, MEDIUM, HIGH, CRITICAL
    field_drifts: List[FieldDrift]
    added_fields: int
    removed_fields: int
    modified_fields: int
    total_fields: int
    security_impact: str


def detect_drift(baseline_model: UnifiedSecurityModel, current_model: UnifiedSecurityModel) -> DriftResult:
    """
    Detect configuration drift between baseline and current
    
    Args:
        baseline_model: Baseline UnifiedSecurityModel
        current_model: Current UnifiedSecurityModel
        
    Returns:
        DriftResult with detailed drift analysis
    """
    field_drifts = analyze_field_drifts(baseline_model, current_model)
    
    # Count drift types
    added = sum(1 for d in field_drifts if d.drift_type == "ADDED")
    removed = sum(1 for d in field_drifts if d.drift_type == "REMOVED")
    modified = sum(1 for d in field_drifts if d.drift_type == "MODIFIED")
    
    # Calculate drift score
    drift_score = calculate_drift_score(field_drifts, baseline_model)
    
    # Determine overall severity
    drift_severity = calculate_severity(drift_score, field_drifts)
    
    # Determine security impact
    security_impact = determine_security_impact(field_drifts)
    
    # Get total fields
    total_fields = len(get_all_fields(baseline_model))
    
    return DriftResult(
        drift_score=drift_score,
        drift_severity=drift_severity,
        field_drifts=field_drifts,
        added_fields=added,
        removed_fields=removed,
        modified_fields=modified,
        total_fields=total_fields,
        security_impact=security_impact
    )


def analyze_field_drifts(baseline: UnifiedSecurityModel, current: UnifiedSecurityModel) -> List[FieldDrift]:
    """
    Analyze field-level drifts between baseline and current configurations
    
    Returns:
        List of FieldDrift objects
    """
    drifts = []
    
    # Convert models to flat dictionaries for comparison
    baseline_dict = model_to_dict(baseline)
    current_dict = model_to_dict(current)
    
    # Find all unique keys
    all_keys = set(baseline_dict.keys()) | set(current_dict.keys())
    
    for key in all_keys:
        baseline_val = baseline_dict.get(key)
        current_val = current_dict.get(key)
        
        # Skip if values are the same
        if baseline_val == current_val:
            continue
        
        # Determine drift type
        if baseline_val is None:
            drift_type = "ADDED"
        elif current_val is None:
            drift_type = "REMOVED"
        else:
            drift_type = "MODIFIED"
        
        # Determine severity and security impact
        severity, security_impact = assess_field_importance(key, baseline_val, current_val, drift_type)
        
        drift = FieldDrift(
            field_path=key,
            baseline_value=baseline_val,
            current_value=current_val,
            drift_type=drift_type,
            severity=severity,
            security_impact=security_impact
        )
        
        drifts.append(drift)
    
    return drifts


def calculate_drift_score(field_drifts: List[FieldDrift], baseline: UnifiedSecurityModel) -> float:
    """
    Calculate overall drift score (0-100)
    
    Factors:
    - Number of drifted fields (40%)
    - Severity of drifts (40%)
    - Security impact (20%)
    """
    if not field_drifts:
        return 0.0
    
    total_fields = len(get_all_fields(baseline))
    if total_fields == 0:
        return 0.0
    
    # Factor 1: Proportion of drifted fields (0-100)
    drift_proportion = (len(field_drifts) / total_fields) * 100
    drift_factor = min(drift_proportion, 100) * 0.4
    
    # Factor 2: Severity weighting (0-100)
    severity_weights = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4
    }
    
    total_severity = sum(severity_weights.get(d.severity, 1) for d in field_drifts)
    max_severity = len(field_drifts) * 4  # All CRITICAL
    severity_score = (total_severity / max_severity) * 100 if max_severity > 0 else 0
    severity_factor = severity_score * 0.4
    
    # Factor 3: Security impact (0-100)
    security_impacts = [d for d in field_drifts if d.security_impact in ["MEDIUM", "HIGH", "CRITICAL"]]
    security_proportion = (len(security_impacts) / len(field_drifts)) * 100 if field_drifts else 0
    security_factor = security_proportion * 0.2
    
    # Calculate final score
    drift_score = drift_factor + severity_factor + security_factor
    
    return round(min(drift_score, 100), 2)


def calculate_severity(drift_score: float, field_drifts: List[FieldDrift]) -> str:
    """
    Calculate overall drift severity based on score and critical fields
    """
    # Check for critical security drifts
    has_critical = any(d.severity == "CRITICAL" for d in field_drifts)
    has_high = any(d.severity == "HIGH" for d in field_drifts)
    
    if has_critical or drift_score >= 80:
        return "CRITICAL"
    elif has_high or drift_score >= 60:
        return "HIGH"
    elif drift_score >= 30:
        return "MEDIUM"
    elif drift_score > 0:
        return "LOW"
    else:
        return "NONE"


def determine_security_impact(field_drifts: List[FieldDrift]) -> str:
    """
    Determine overall security impact of drift
    """
    if not field_drifts:
        return "NONE"
    
    # Find highest impact
    impacts = [d.security_impact for d in field_drifts]
    
    if "CRITICAL" in impacts:
        return "CRITICAL"
    elif "HIGH" in impacts:
        return "HIGH"
    elif "MEDIUM" in impacts:
        return "MEDIUM"
    elif "LOW" in impacts:
        return "LOW"
    else:
        return "NONE"


def assess_field_importance(field_path: str, baseline_val: any, current_val: any, drift_type: str) -> Tuple[str, str]:
    """
    Assess the importance and security impact of a field drift
    
    Returns:
        (severity, security_impact)
    """
    # Critical security fields
    critical_fields = [
        "ssh_enabled",
        "telnet_enabled",
        "password_encryption",
        "aaa_enabled",
        "logging_enabled",
        "access_lists",
        "firewall_rules"
    ]
    
    # High importance fields
    high_fields = [
        "snmp_version",
        "ntp_servers",
        "source_filtering",
        "privilege_levels",
        "timeout"
    ]
    
    field_lower = field_path.lower()
    
    # Check for critical fields
    for crit in critical_fields:
        if crit in field_lower:
            # Determine security impact based on drift type and values
            if drift_type == "REMOVED" or (current_val == False and baseline_val == True):
                return ("CRITICAL", "CRITICAL")
            elif drift_type == "ADDED" or (current_val == True and baseline_val == False):
                return ("HIGH", "HIGH")
            else:
                return ("HIGH", "MEDIUM")
    
    # Check for high importance fields
    for high in high_fields:
        if high in field_lower:
            if drift_type == "REMOVED":
                return ("HIGH", "HIGH")
            elif drift_type == "MODIFIED":
                return ("MEDIUM", "MEDIUM")
            else:
                return ("MEDIUM", "LOW")
    
    # Default: low severity
    return ("LOW", "LOW")


def model_to_dict(model: UnifiedSecurityModel, prefix: str = "") -> Dict[str, any]:
    """
    Convert UnifiedSecurityModel to flat dictionary
    
    Args:
        model: UnifiedSecurityModel instance
        prefix: Path prefix for nested fields
        
    Returns:
        Flat dictionary with dotted paths as keys
    """
    result = {}
    
    for attr in dir(model):
        if attr.startswith('_'):
            continue
        
        try:
            value = getattr(model, attr)
            
            # Skip methods
            if callable(value):
                continue
            
            key = f"{prefix}.{attr}" if prefix else attr
            
            # Handle nested objects
            if hasattr(value, '__dict__') and not isinstance(value, (str, int, float, bool, list, dict)):
                nested = model_to_dict(value, prefix=key)
                result.update(nested)
            else:
                result[key] = value
        except:
            continue
    
    return result


def get_all_fields(model: UnifiedSecurityModel) -> List[str]:
    """
    Get all field paths in a UnifiedSecurityModel
    """
    return list(model_to_dict(model).keys())


def compare_configurations(baseline_content: str, current_content: str) -> Dict:
    """
    Compare two configuration file contents line-by-line
    
    Args:
        baseline_content: Baseline configuration text
        current_content: Current configuration text
        
    Returns:
        Dictionary with diff details
    """
    baseline_lines = baseline_content.splitlines()
    current_lines = current_content.splitlines()
    
    differ = difflib.Differ()
    diff = list(differ.compare(baseline_lines, current_lines))
    
    added_lines = [line[2:] for line in diff if line.startswith('+ ')]
    removed_lines = [line[2:] for line in diff if line.startswith('- ')]
    
    # Use unified diff for better readability
    unified_diff = difflib.unified_diff(
        baseline_lines,
        current_lines,
        lineterm='',
        fromfile='baseline',
        tofile='current'
    )
    
    return {
        "added_lines": added_lines,
        "removed_lines": removed_lines,
        "added_count": len(added_lines),
        "removed_count": len(removed_lines),
        "unified_diff": '\n'.join(unified_diff)
    }


def generate_diff(baseline_content: str, current_content: str, format: str = "unified") -> str:
    """
    Generate diff between two configurations
    
    Args:
        baseline_content: Baseline configuration
        current_content: Current configuration
        format: Diff format ("unified", "context", "ndiff")
        
    Returns:
        Formatted diff string
    """
    baseline_lines = baseline_content.splitlines(keepends=True)
    current_lines = current_content.splitlines(keepends=True)
    
    if format == "unified":
        diff = difflib.unified_diff(
            baseline_lines,
            current_lines,
            fromfile='baseline',
            tofile='current'
        )
    elif format == "context":
        diff = difflib.context_diff(
            baseline_lines,
            current_lines,
            fromfile='baseline',
            tofile='current'
        )
    elif format == "ndiff":
        diff = difflib.ndiff(baseline_lines, current_lines)
    else:
        diff = difflib.unified_diff(baseline_lines, current_lines)
    
    return ''.join(diff)
