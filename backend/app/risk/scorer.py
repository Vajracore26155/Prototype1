"""
Risk Scoring Engine

Calculates risk scores using transparent deterministic formula
"""
from typing import Dict, Any, List
from dataclasses import dataclass
from app.compliance.evaluator import ComplianceResult, Severity, ComplianceStatus


@dataclass
class RiskScore:
    """Risk score calculation result"""
    score: float  # 0-100
    level: str  # LOW, MEDIUM, HIGH, CRITICAL
    factors: Dict[str, Any]
    explanation: str


class RiskScorer:
    """
    Calculates risk scores using transparent deterministic formula
    
    Formula:
        risk_score = (severity_weight * severity_score +
                     exposure_weight * exposure_score +
                     criticality_weight * criticality_score)
    
    The formula is fully documented and explainable
    """
    
    # Severity scores (0-100)
    SEVERITY_SCORES = {
        Severity.CRITICAL: 100,
        Severity.HIGH: 75,
        Severity.MEDIUM: 50,
        Severity.LOW: 25
    }
    
    # Default weights (must sum to 1.0)
    DEFAULT_WEIGHTS = {
        'severity': 0.60,      # Control severity
        'exposure': 0.25,      # Asset exposure (prototype: default)
        'criticality': 0.15    # Asset criticality (prototype: default)
    }
    
    # Prototype defaults (would come from asset inventory in production)
    DEFAULT_EXPOSURE = 75.0    # Assume internet-facing management
    DEFAULT_CRITICALITY = 60.0  # Assume moderately critical asset
    
    def __init__(
        self,
        weights: Dict[str, float] = None,
        default_exposure: float = None,
        default_criticality: float = None
    ):
        """
        Initialize risk scorer
        
        Args:
            weights: Custom scoring weights
            default_exposure: Default exposure score (0-100)
            default_criticality: Default asset criticality (0-100)
        """
        self.weights = weights or self.DEFAULT_WEIGHTS
        self.default_exposure = default_exposure or self.DEFAULT_EXPOSURE
        self.default_criticality = default_criticality or self.DEFAULT_CRITICALITY
        
        # Validate weights sum to 1.0
        if abs(sum(self.weights.values()) - 1.0) > 0.01:
            raise ValueError("Weights must sum to 1.0")
    
    def calculate_finding_risk(
        self,
        result: ComplianceResult,
        exposure: float = None,
        criticality: float = None
    ) -> RiskScore:
        """
        Calculate risk score for a single compliance finding
        
        Args:
            result: Compliance result
            exposure: Asset exposure score (0-100)
            criticality: Asset criticality score (0-100)
            
        Returns:
            RiskScore with score and explanation
        """
        # Only calculate risk for failures
        if result.status != ComplianceStatus.FAIL:
            return RiskScore(
                score=0.0,
                level="LOW",
                factors={},
                explanation="Control passed - no risk"
            )
        
        # Use defaults if not provided
        exposure = exposure or self.default_exposure
        criticality = criticality or self.default_criticality
        
        # Get severity score
        severity_score = self.SEVERITY_SCORES[result.severity]
        
        # Calculate weighted score
        risk_score = (
            self.weights['severity'] * severity_score +
            self.weights['exposure'] * exposure +
            self.weights['criticality'] * criticality
        )
        
        # Determine risk level
        risk_level = self._score_to_level(risk_score)
        
        # Build explanation
        explanation = self._build_explanation(
            severity_score, exposure, criticality, risk_score
        )
        
        return RiskScore(
            score=round(risk_score, 2),
            level=risk_level,
            factors={
                'severity_score': severity_score,
                'severity_weight': self.weights['severity'],
                'exposure_score': exposure,
                'exposure_weight': self.weights['exposure'],
                'criticality_score': criticality,
                'criticality_weight': self.weights['criticality'],
                'is_prototype_default': exposure == self.default_exposure
            },
            explanation=explanation
        )
    
    def calculate_aggregate_risk(
        self,
        results: List[ComplianceResult]
    ) -> RiskScore:
        """
        Calculate aggregate risk across all findings
        
        Uses worst-case (maximum) risk as overall score
        """
        if not results:
            return RiskScore(
                score=0.0,
                level="LOW",
                factors={},
                explanation="No findings to evaluate"
            )
        
        # Calculate risk for each failed finding
        risk_scores = []
        for result in results:
            if result.status == ComplianceStatus.FAIL:
                risk = self.calculate_finding_risk(result)
                risk_scores.append(risk.score)
        
        if not risk_scores:
            return RiskScore(
                score=0.0,
                level="LOW",
                factors={'passed_all': True},
                explanation="All controls passed - minimal risk"
            )
        
        # Use maximum risk as aggregate
        max_risk = max(risk_scores)
        avg_risk = sum(risk_scores) / len(risk_scores)
        
        level = self._score_to_level(max_risk)
        
        explanation = (
            f"Aggregate risk based on {len(risk_scores)} failed controls. "
            f"Maximum risk: {max_risk:.0f}, Average risk: {avg_risk:.0f}"
        )
        
        return RiskScore(
            score=round(max_risk, 2),
            level=level,
            factors={
                'failed_count': len(risk_scores),
                'max_risk': max_risk,
                'avg_risk': avg_risk,
                'total_evaluated': len(results)
            },
            explanation=explanation
        )
    
    def _score_to_level(self, score: float) -> str:
        """Convert numeric score to risk level"""
        if score >= 76:
            return "CRITICAL"
        elif score >= 51:
            return "HIGH"
        elif score >= 26:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _build_explanation(
        self,
        severity_score: float,
        exposure: float,
        criticality: float,
        final_score: float
    ) -> str:
        """Build human-readable risk explanation"""
        parts = []
        
        # Severity component
        parts.append(
            f"Control severity: {severity_score:.0f} "
            f"(weight: {self.weights['severity']:.0%})"
        )
        
        # Exposure component
        if exposure == self.default_exposure:
            parts.append(
                f"Exposure: {exposure:.0f} [prototype default] "
                f"(weight: {self.weights['exposure']:.0%})"
            )
        else:
            parts.append(
                f"Exposure: {exposure:.0f} "
                f"(weight: {self.weights['exposure']:.0%})"
            )
        
        # Criticality component
        if criticality == self.default_criticality:
            parts.append(
                f"Asset criticality: {criticality:.0f} [prototype default] "
                f"(weight: {self.weights['criticality']:.0%})"
            )
        else:
            parts.append(
                f"Asset criticality: {criticality:.0f} "
                f"(weight: {self.weights['criticality']:.0%})"
            )
        
        # Final score
        parts.append(f"Final risk score: {final_score:.0f}/100")
        
        return " | ".join(parts)


def calculate_risk(result: ComplianceResult) -> RiskScore:
    """Convenience function to calculate risk for a finding"""
    scorer = RiskScorer()
    return scorer.calculate_finding_risk(result)
