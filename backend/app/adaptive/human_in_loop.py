"""
Human-in-the-Loop Learning System

Phase 3: Adaptive AI with Human Validation

Core Features:
- AI-generated mapping candidates with confidence scores
- Human training interface for validation
- Mapping storage and reuse
- Confidence tracking over time
- Prompt injection defenses
"""
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re


class MappingStatus(str, Enum):
    """Status of a mapping suggestion"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


class ConfidenceLevel(str, Enum):
    """Confidence level for AI suggestions"""
    VERY_HIGH = "very_high"  # >= 0.9
    HIGH = "high"            # >= 0.75
    MEDIUM = "medium"        # >= 0.5
    LOW = "low"              # < 0.5


@dataclass
class MappingCandidate:
    """
    AI-generated mapping candidate
    
    Represents a suggested mapping from raw config pattern
    to normalized UnifiedSecurityModel field
    """
    id: Optional[int]
    raw_pattern: str
    vendor: str
    
    # Suggested mapping
    normalized_field: str
    suggested_value: any
    suggested_meaning: str
    
    # Confidence and reasoning
    confidence: float  # 0.0 to 1.0
    confidence_level: ConfidenceLevel
    reasoning: str
    similar_patterns: List[str]
    
    # Status
    status: MappingStatus
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    
    # Metadata
    created_at: datetime
    source_config: str
    line_number: int


@dataclass
class TrainingExample:
    """
    Human-validated training example
    
    Used to improve AI mapping suggestions over time
    """
    id: Optional[int]
    raw_pattern: str
    vendor: str
    normalized_field: str
    correct_value: any
    explanation: str
    validated_by: str
    validated_at: datetime
    
    # Context
    source_config: str
    line_number: int
    
    # Feedback
    was_ai_suggested: bool
    ai_confidence: Optional[float]


class HumanInLoopEngine:
    """
    Human-in-the-Loop Learning Engine
    
    Manages AI-generated candidates, human validation,
    and continuous learning
    """
    
    def __init__(self, db_session=None):
        self.db = db_session
        self.confidence_threshold = 0.75
    
    def generate_mapping_candidate(
        self,
        raw_pattern: str,
        vendor: str,
        context_lines: List[str],
        source_config: str,
        line_number: int
    ) -> MappingCandidate:
        """
        Generate AI mapping candidate with confidence scoring
        
        Args:
            raw_pattern: Raw configuration line
            vendor: Vendor name
            context_lines: Surrounding lines for context
            source_config: Configuration filename
            line_number: Line number in config
            
        Returns:
            MappingCandidate with confidence score
        """
        # Sanitize input (prompt injection defense)
        sanitized_pattern = self._sanitize_input(raw_pattern)
        
        # Check for learned mappings first
        learned = self._check_learned_mappings(sanitized_pattern, vendor)
        if learned:
            return self._create_high_confidence_candidate(
                learned, sanitized_pattern, vendor, source_config, line_number
            )
        
        # Use AI embedding similarity
        similar_patterns = self._find_similar_patterns(sanitized_pattern, vendor)
        
        # Generate suggestion using heuristics + AI
        suggestion = self._generate_suggestion(
            sanitized_pattern,
            vendor,
            context_lines,
            similar_patterns
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            sanitized_pattern,
            suggestion,
            similar_patterns
        )
        
        # Determine confidence level
        if confidence >= 0.9:
            confidence_level = ConfidenceLevel.VERY_HIGH
        elif confidence >= 0.75:
            confidence_level = ConfidenceLevel.HIGH
        elif confidence >= 0.5:
            confidence_level = ConfidenceLevel.MEDIUM
        else:
            confidence_level = ConfidenceLevel.LOW
        
        # Determine initial status
        if confidence >= self.confidence_threshold:
            status = MappingStatus.PENDING  # Ready for human review
        else:
            status = MappingStatus.NEEDS_REVIEW  # Low confidence, needs expert
        
        return MappingCandidate(
            id=None,
            raw_pattern=sanitized_pattern,
            vendor=vendor,
            normalized_field=suggestion['field'],
            suggested_value=suggestion['value'],
            suggested_meaning=suggestion['meaning'],
            confidence=confidence,
            confidence_level=confidence_level,
            reasoning=suggestion['reasoning'],
            similar_patterns=[p['pattern'] for p in similar_patterns],
            status=status,
            reviewed_by=None,
            reviewed_at=None,
            created_at=datetime.utcnow(),
            source_config=source_config,
            line_number=line_number
        )
    
    def _sanitize_input(self, raw_input: str) -> str:
        """
        Sanitize input to prevent prompt injection
        
        Defense against malicious config lines that try to
        manipulate AI prompts
        """
        # Remove control characters
        sanitized = ''.join(char for char in raw_input if ord(char) >= 32 or char in '\n\t')
        
        # Limit length
        max_length = 500
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        # Remove potential prompt injection patterns
        dangerous_patterns = [
            r'ignore previous',
            r'forget instructions',
            r'new instructions',
            r'disregard',
            r'system:',
            r'admin:',
            r'<script>',
            r'javascript:',
        ]
        
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '[FILTERED]', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    def _check_learned_mappings(
        self,
        pattern: str,
        vendor: str
    ) -> Optional[Dict]:
        """
        Check if we have a learned mapping for this pattern
        
        Returns learned mapping if found, None otherwise
        """
        # In production, this would query the database
        # For now, return None (no learned mappings yet)
        return None
    
    def _find_similar_patterns(
        self,
        pattern: str,
        vendor: str,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Find similar patterns using embedding similarity
        
        Uses sentence-transformers if available, falls back to
        string similarity
        """
        # Try to use AI embeddings
        try:
            from app.adaptive.embedding_engine import find_similar_configs
            similar = find_similar_configs(pattern, vendor, top_k)
            return similar
        except Exception:
            # Fallback to simple string matching
            return []
    
    def _generate_suggestion(
        self,
        pattern: str,
        vendor: str,
        context_lines: List[str],
        similar_patterns: List[Dict]
    ) -> Dict:
        """
        Generate mapping suggestion
        
        Returns dict with field, value, meaning, and reasoning
        """
        pattern_lower = pattern.lower()
        
        # SSH detection
        if 'ssh' in pattern_lower:
            if 'enable' in pattern_lower or 'allow' in pattern_lower:
                return {
                    'field': 'remote_access.ssh_enabled',
                    'value': True,
                    'meaning': 'SSH remote access is enabled',
                    'reasoning': 'Pattern contains "ssh" and "enable/allow" keywords'
                }
            elif 'version 2' in pattern_lower or 'v2' in pattern_lower:
                return {
                    'field': 'remote_access.ssh_version',
                    'value': 2,
                    'meaning': 'SSH version 2 configured',
                    'reasoning': 'Pattern contains "version 2" or "v2"'
                }
        
        # Telnet detection
        if 'telnet' in pattern_lower:
            if 'disable' in pattern_lower or 'deny' in pattern_lower:
                return {
                    'field': 'remote_access.telnet_enabled',
                    'value': False,
                    'meaning': 'Telnet is disabled (secure)',
                    'reasoning': 'Pattern contains "telnet" and "disable/deny"'
                }
            elif 'enable' in pattern_lower or 'allow' in pattern_lower:
                return {
                    'field': 'remote_access.telnet_enabled',
                    'value': True,
                    'meaning': 'Telnet is enabled (insecure)',
                    'reasoning': 'Pattern contains "telnet" and "enable/allow"'
                }
        
        # HTTP/HTTPS detection
        if 'http' in pattern_lower:
            if 'https' in pattern_lower:
                return {
                    'field': 'management.https_enabled',
                    'value': True,
                    'meaning': 'HTTPS web management enabled',
                    'reasoning': 'Pattern contains "https"'
                }
            elif 'disable' in pattern_lower:
                return {
                    'field': 'management.http_enabled',
                    'value': False,
                    'meaning': 'HTTP is disabled (secure)',
                    'reasoning': 'Pattern contains "http" and "disable"'
                }
            else:
                return {
                    'field': 'management.http_enabled',
                    'value': True,
                    'meaning': 'HTTP web management enabled (insecure)',
                    'reasoning': 'Pattern contains "http"'
                }
        
        # Logging detection
        if 'log' in pattern_lower or 'syslog' in pattern_lower:
            return {
                'field': 'logging.enabled',
                'value': True,
                'meaning': 'Logging is enabled',
                'reasoning': 'Pattern contains logging keywords'
            }
        
        # Timeout detection
        if 'timeout' in pattern_lower or 'idle' in pattern_lower:
            return {
                'field': 'access_control.timeout_configured',
                'value': True,
                'meaning': 'Session timeout configured',
                'reasoning': 'Pattern contains timeout keywords'
            }
        
        # Default: unknown
        return {
            'field': 'unknown',
            'value': None,
            'meaning': 'Unable to determine mapping',
            'reasoning': 'No matching patterns found'
        }
    
    def _calculate_confidence(
        self,
        pattern: str,
        suggestion: Dict,
        similar_patterns: List[Dict]
    ) -> float:
        """
        Calculate confidence score for suggestion
        
        Returns float between 0.0 and 1.0
        """
        confidence = 0.0
        
        # Base confidence from suggestion quality
        if suggestion['field'] != 'unknown':
            confidence += 0.4
        
        # Boost from keyword matching
        pattern_lower = pattern.lower()
        field_keywords = suggestion['field'].split('.')
        
        for keyword in field_keywords:
            if keyword in pattern_lower:
                confidence += 0.15
        
        # Boost from similar patterns
        if similar_patterns:
            confidence += min(0.3, len(similar_patterns) * 0.1)
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def _create_high_confidence_candidate(
        self,
        learned_mapping: Dict,
        pattern: str,
        vendor: str,
        source_config: str,
        line_number: int
    ) -> MappingCandidate:
        """Create candidate from learned mapping (high confidence)"""
        return MappingCandidate(
            id=None,
            raw_pattern=pattern,
            vendor=vendor,
            normalized_field=learned_mapping['field'],
            suggested_value=learned_mapping['value'],
            suggested_meaning=learned_mapping['meaning'],
            confidence=0.95,
            confidence_level=ConfidenceLevel.VERY_HIGH,
            reasoning="Based on previously validated mapping",
            similar_patterns=[],
            status=MappingStatus.APPROVED,  # Already validated
            reviewed_by=learned_mapping.get('validated_by'),
            reviewed_at=learned_mapping.get('validated_at'),
            created_at=datetime.utcnow(),
            source_config=source_config,
            line_number=line_number
        )
    
    def approve_candidate(
        self,
        candidate: MappingCandidate,
        reviewer: str,
        corrected_field: Optional[str] = None,
        corrected_value: Optional[any] = None
    ) -> TrainingExample:
        """
        Approve a mapping candidate (with optional corrections)
        
        Creates training example for future learning
        """
        # Use corrected values if provided, otherwise use suggested
        final_field = corrected_field or candidate.normalized_field
        final_value = corrected_value if corrected_value is not None else candidate.suggested_value
        
        # Create training example
        training_example = TrainingExample(
            id=None,
            raw_pattern=candidate.raw_pattern,
            vendor=candidate.vendor,
            normalized_field=final_field,
            correct_value=final_value,
            explanation=f"Approved by {reviewer}. Original confidence: {candidate.confidence:.2f}",
            validated_by=reviewer,
            validated_at=datetime.utcnow(),
            source_config=candidate.source_config,
            line_number=candidate.line_number,
            was_ai_suggested=True,
            ai_confidence=candidate.confidence
        )
        
        # Update candidate status
        candidate.status = MappingStatus.APPROVED
        candidate.reviewed_by = reviewer
        candidate.reviewed_at=datetime.utcnow()
        
        # In production, save to database
        # self._save_training_example(training_example)
        
        return training_example
    
    def reject_candidate(
        self,
        candidate: MappingCandidate,
        reviewer: str,
        reason: str
    ):
        """
        Reject a mapping candidate
        
        Helps AI learn what not to suggest
        """
        candidate.status = MappingStatus.REJECTED
        candidate.reviewed_by = reviewer
        candidate.reviewed_at = datetime.utcnow()
        
        # In production, log rejection for learning
        # self._log_rejection(candidate, reason)
    
    def get_pending_candidates(
        self,
        vendor: Optional[str] = None,
        confidence_min: float = 0.0,
        limit: int = 50
    ) -> List[MappingCandidate]:
        """
        Get pending candidates for human review
        
        Returns candidates sorted by confidence (highest first)
        """
        # In production, query database
        # For now, return empty list
        return []
    
    def get_statistics(self) -> Dict:
        """
        Get human-in-loop statistics
        
        Returns metrics about learning system performance
        """
        # In production, calculate from database
        return {
            'total_candidates': 0,
            'pending_review': 0,
            'approved': 0,
            'rejected': 0,
            'avg_confidence': 0.0,
            'approval_rate': 0.0,
            'learning_examples': 0
        }
