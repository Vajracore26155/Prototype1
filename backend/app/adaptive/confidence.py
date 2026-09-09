"""
Confidence Scoring Engine

Calculates confidence scores for AI interpretations using multiple factors
"""
import re
import os
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class ConfidenceScore:
    """Confidence score breakdown"""
    overall: float  # 0.0 - 1.0
    keyword_score: float
    semantic_score: float
    pattern_score: float
    factors: Dict[str, float]
    explanation: str
    confidence_level: str  # HIGH, MEDIUM, LOW, UNKNOWN


class ConfidenceScorer:
    """
    Multi-factor confidence scoring for AI interpretations
    
    Factors:
    - Keyword matching (exact word matches)
    - Semantic similarity (embedding-based)
    - Pattern matching (syntax patterns)
    - Vendor context (if known)
    """
    
    # Default weights (configurable)
    DEFAULT_WEIGHTS = {
        'keyword': float(os.getenv('AI_KEYWORD_WEIGHT', '0.25')),
        'semantic': float(os.getenv('AI_SEMANTIC_WEIGHT', '0.40')),
        'pattern': float(os.getenv('AI_PATTERN_WEIGHT', '0.25')),
        'vendor': float(os.getenv('AI_VENDOR_WEIGHT', '0.10'))
    }
    
    # Confidence thresholds
    HIGH_THRESHOLD = float(os.getenv('AI_HIGH_THRESHOLD', '0.85'))
    REVIEW_THRESHOLD = float(os.getenv('AI_REVIEW_THRESHOLD', '0.60'))
    
    def __init__(self, weights: Dict[str, float] = None):
        """Initialize confidence scorer"""
        self.weights = weights or self.DEFAULT_WEIGHTS
        
        # Validate weights sum to ~1.0
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            # Normalize weights
            self.weights = {k: v/total for k, v in self.weights.items()}
    
    def calculate_keyword_score(
        self,
        unknown_text: str,
        concept_phrases: List[str]
    ) -> float:
        """
        Calculate keyword matching score
        
        Looks for exact word matches between unknown text and concept phrases
        """
        # Tokenize unknown text
        unknown_words = set(re.findall(r'\b\w+\b', unknown_text.lower()))
        
        # Check each concept phrase
        max_match = 0.0
        for phrase in concept_phrases:
            phrase_words = set(re.findall(r'\b\w+\b', phrase.lower()))
            
            if not phrase_words:
                continue
            
            # Calculate word overlap
            overlap = len(unknown_words & phrase_words)
            match_ratio = overlap / len(phrase_words)
            
            max_match = max(max_match, match_ratio)
        
        return max_match
    
    def calculate_pattern_score(
        self,
        unknown_text: str,
        concept_id: str
    ) -> float:
        """
        Calculate pattern matching score
        
        Looks for common configuration patterns
        """
        text_lower = unknown_text.lower()
        
        # Pattern indicators for different concepts
        patterns = {
            'ssh': [
                r'\bssh\b',
                r'\bsecure[_\-]?shell\b',
                r'\bssh[_\-]?access\b',
            ],
            'telnet': [
                r'\btelnet\b',
            ],
            'http': [
                r'\bhttp\b(?!s)',
                r'\bweb\b',
            ],
            'https': [
                r'\bhttps\b',
                r'\bssl\b',
                r'\btls\b',
            ],
            'logging': [
                r'\blog\b',
                r'\bsyslog\b',
                r'\baudit\b',
            ],
        }
        
        # Find matching patterns
        for key, pattern_list in patterns.items():
            if key in concept_id.lower():
                for pattern in pattern_list:
                    if re.search(pattern, text_lower):
                        return 1.0
        
        return 0.0
    
    def calculate_confidence(
        self,
        unknown_text: str,
        concept_id: str,
        concept_phrases: List[str],
        semantic_score: float,
        vendor_confidence: float = 0.0
    ) -> ConfidenceScore:
        """
        Calculate overall confidence score
        
        Args:
            unknown_text: Unknown configuration text
            concept_id: Security concept ID
            concept_phrases: Known phrases for concept
            semantic_score: Semantic similarity score from embeddings
            vendor_confidence: Vendor detection confidence (optional)
            
        Returns:
            ConfidenceScore with breakdown
        """
        # Calculate component scores
        keyword_score = self.calculate_keyword_score(unknown_text, concept_phrases)
        pattern_score = self.calculate_pattern_score(unknown_text, concept_id)
        
        # Calculate weighted overall score
        overall = (
            self.weights['keyword'] * keyword_score +
            self.weights['semantic'] * semantic_score +
            self.weights['pattern'] * pattern_score +
            self.weights['vendor'] * vendor_confidence
        )
        
        # Ensure in range [0, 1]
        overall = max(0.0, min(1.0, overall))
        
        # Determine confidence level
        if overall >= self.HIGH_THRESHOLD:
            level = "HIGH"
        elif overall >= self.REVIEW_THRESHOLD:
            level = "MEDIUM"
        elif overall > 0.0:
            level = "LOW"
        else:
            level = "UNKNOWN"
        
        # Build explanation
        explanation = self._build_explanation(
            keyword_score, semantic_score, pattern_score,
            vendor_confidence, overall, level
        )
        
        return ConfidenceScore(
            overall=overall,
            keyword_score=keyword_score,
            semantic_score=semantic_score,
            pattern_score=pattern_score,
            factors={
                'keyword': keyword_score,
                'semantic': semantic_score,
                'pattern': pattern_score,
                'vendor': vendor_confidence
            },
            explanation=explanation,
            confidence_level=level
        )
    
    def _build_explanation(
        self,
        keyword: float,
        semantic: float,
        pattern: float,
        vendor: float,
        overall: float,
        level: str
    ) -> str:
        """Build human-readable explanation"""
        parts = []
        
        parts.append(f"Overall confidence: {overall:.1%} ({level})")
        parts.append(f"Keyword match: {keyword:.1%}")
        parts.append(f"Semantic similarity: {semantic:.1%}")
        parts.append(f"Pattern match: {pattern:.1%}")
        
        if vendor > 0:
            parts.append(f"Vendor context: {vendor:.1%}")
        
        # Recommendation
        if level == "HIGH":
            parts.append("Recommendation: Auto-suggest with review")
        elif level == "MEDIUM":
            parts.append("Recommendation: Human validation required")
        else:
            parts.append("Recommendation: Manual classification needed")
        
        return " | ".join(parts)
    
    def should_auto_suggest(self, confidence: ConfidenceScore) -> bool:
        """Check if confidence is high enough to auto-suggest"""
        return confidence.overall >= self.HIGH_THRESHOLD
    
    def requires_validation(self, confidence: ConfidenceScore) -> bool:
        """Check if human validation is required"""
        return self.REVIEW_THRESHOLD <= confidence.overall < self.HIGH_THRESHOLD
