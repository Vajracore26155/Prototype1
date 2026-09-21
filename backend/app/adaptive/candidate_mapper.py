"""
Candidate Mapper - AI Interpretation Engine

Maps unknown configuration syntax to security concepts
using semantic similarity and confidence scoring
"""
from typing import List, Dict, Optional
from dataclasses import dataclass

from .vocabulary import get_all_concepts, SecurityConcept
from .embedding_engine import get_embedding_engine
from .confidence import ConfidenceScorer, ConfidenceScore


@dataclass
class InterpretationCandidate:
    """A candidate interpretation of unknown syntax"""
    concept: SecurityConcept
    confidence: ConfidenceScore
    rank: int  # 1 = best match


@dataclass
class InterpretationResult:
    """Result of interpreting unknown configuration"""
    raw_text: str
    best_candidate: Optional[InterpretationCandidate]
    all_candidates: List[InterpretationCandidate]
    requires_validation: bool
    can_auto_suggest: bool
    error_message: Optional[str] = None


class CandidateMapper:
    """
    Maps unknown configuration syntax to security concepts
    
    Process:
    1. Extract tokens from unknown text
    2. Compute embeddings
    3. Compare to known security concepts
    4. Calculate confidence scores
    5. Rank candidates
    """
    
    def __init__(self):
        """Initialize candidate mapper"""
        self.embedding_engine = get_embedding_engine()
        self.confidence_scorer = ConfidenceScorer()
        self.concepts = get_all_concepts()
        
        # Pre-compute embeddings for all concept phrases
        self._initialize_concept_embeddings()
    
    def _initialize_concept_embeddings(self):
        """Pre-compute embeddings for all security concepts"""
        # Don't initialize embeddings at startup - do it lazily
        self.concept_embeddings = {}
        self.embeddings_initialized = False
    
    def _ensure_embeddings_initialized(self):
        """Ensure embeddings are initialized (lazy initialization)"""
        if self.embeddings_initialized:
            return
        
        if not self.embedding_engine.is_available():
            print("Warning: Embedding engine not available - using fallback mode")
            return
        
        try:
            print("Initializing security concept embeddings (one-time setup)...")
            
            for concept in self.concepts:
                # Embed all phrases for this concept
                embeddings = self.embedding_engine.embed_batch(concept.phrases)
                self.concept_embeddings[concept.concept_id] = [
                    (phrase, emb.embedding)
                    for phrase, emb in zip(concept.phrases, embeddings)
                    if emb is not None
                ]
            
            self.embeddings_initialized = True
            print(f"[SUCCESS] Initialized embeddings for {len(self.concept_embeddings)} concepts")
        except Exception as e:
            print(f"Warning: Failed to initialize embeddings: {e}")
            self.embeddings_initialized = False
    
    def interpret(
        self,
        unknown_text: str,
        vendor_confidence: float = 0.0,
        top_k: int = 5
    ) -> InterpretationResult:
        """
        Interpret unknown configuration syntax
        
        Args:
            unknown_text: Unknown configuration command
            vendor_confidence: Vendor detection confidence (optional)
            top_k: Number of top candidates to return
            
        Returns:
            InterpretationResult with ranked candidates
        """
        # Lazy initialize embeddings if needed
        if not self.embeddings_initialized:
            self._ensure_embeddings_initialized()
        
        # Check if embedding engine is available
        if not self.embedding_engine.is_available() or not self.embeddings_initialized:
            return InterpretationResult(
                raw_text=unknown_text,
                best_candidate=None,
                all_candidates=[],
                requires_validation=True,
                can_auto_suggest=False,
                error_message="AI embedding engine not available - using heuristic patterns only"
            )
        
        try:
            # Compute embedding for unknown text
            query_embedding = self.embedding_engine.embed(unknown_text)
            if not query_embedding:
                return InterpretationResult(
                    raw_text=unknown_text,
                    best_candidate=None,
                    all_candidates=[],
                    requires_validation=True,
                    can_auto_suggest=False,
                    error_message="Failed to compute embedding"
                )
            
            # Score all concepts
            candidates = []
            
            for concept in self.concepts:
                # Get pre-computed embeddings for this concept
                concept_embs = self.concept_embeddings.get(concept.concept_id, [])
                
                if not concept_embs:
                    continue
                
                # Find best semantic match among concept phrases
                best_semantic_score = 0.0
                for phrase, phrase_embedding in concept_embs:
                    similarity = self.embedding_engine.cosine_similarity(
                        query_embedding.embedding,
                        phrase_embedding
                    )
                    best_semantic_score = max(best_semantic_score, similarity)
                
                # Calculate overall confidence
                confidence = self.confidence_scorer.calculate_confidence(
                    unknown_text=unknown_text,
                    concept_id=concept.concept_id,
                    concept_phrases=concept.phrases,
                    semantic_score=best_semantic_score,
                    vendor_confidence=vendor_confidence
                )
                
                candidates.append((concept, confidence))
            
            # Sort by overall confidence
            candidates.sort(key=lambda x: x[1].overall, reverse=True)
            
            # Take top k
            top_candidates = candidates[:top_k]
            
            # Create InterpretationCandidate objects
            ranked_candidates = [
                InterpretationCandidate(
                    concept=concept,
                    confidence=confidence,
                    rank=i+1
                )
                for i, (concept, confidence) in enumerate(top_candidates)
            ]
            
            # Determine best candidate
            best = ranked_candidates[0] if ranked_candidates else None
            
            # Determine if validation is required
            requires_validation = True
            can_auto_suggest = False
            
            if best:
                can_auto_suggest = self.confidence_scorer.should_auto_suggest(best.confidence)
                requires_validation = self.confidence_scorer.requires_validation(best.confidence)
                
                # If high confidence, we can auto-suggest (but still show for validation)
                if can_auto_suggest:
                    requires_validation = True  # Always show for human review in prototype
            
            return InterpretationResult(
                raw_text=unknown_text,
                best_candidate=best,
                all_candidates=ranked_candidates,
                requires_validation=requires_validation,
                can_auto_suggest=can_auto_suggest,
                error_message=None
            )
            
        except Exception as e:
            return InterpretationResult(
                raw_text=unknown_text,
                best_candidate=None,
                all_candidates=[],
                requires_validation=True,
                can_auto_suggest=False,
                error_message=f"Interpretation error: {str(e)}"
            )


def interpret_unknown_config(
    unknown_text: str,
    vendor_confidence: float = 0.0
) -> InterpretationResult:
    """
    Convenience function to interpret unknown configuration
    
    Args:
        unknown_text: Unknown configuration text
        vendor_confidence: Vendor detection confidence
        
    Returns:
        InterpretationResult
    """
    mapper = CandidateMapper()
    return mapper.interpret(unknown_text, vendor_confidence)
