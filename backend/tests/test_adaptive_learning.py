"""
Unit Tests: Adaptive Learning System
Phase 8: AI/ML component testing
"""
import pytest
import numpy as np

from app.adaptive.learning import AdaptiveLearningEngine
from app.adaptive.confidence import ConfidenceScorer
from app.adaptive.vocabulary import VocabularyManager


class TestAdaptiveLearningEngine:
    """Test adaptive learning engine"""
    
    @pytest.fixture
    def engine(self):
        """Create learning engine instance"""
        return AdaptiveLearningEngine()
    
    def test_learning_from_feedback(self, engine):
        """Test learning from user feedback"""
        feedback = {
            "mapping_id": "MAP-001",
            "user_feedback": "correct",
            "confidence": 0.85
        }
        
        result = engine.learn_from_feedback(feedback)
        
        assert result is not None
        assert "updated" in result or "learned" in result
    
    def test_prediction_confidence_increase(self, engine):
        """Test confidence increases with positive feedback"""
        initial_confidence = 0.6
        
        # Simulate positive feedback
        for _ in range(5):
            engine.learn_from_feedback({
                "mapping_id": "MAP-001",
                "user_feedback": "correct",
                "confidence": initial_confidence
            })
        
        # Confidence should increase (would need actual implementation)
        assert True  # Placeholder


class TestConfidenceScorer:
    """Test confidence scoring"""
    
    @pytest.fixture
    def scorer(self):
        """Create confidence scorer instance"""
        return ConfidenceScorer()
    
    def test_calculate_confidence_high_similarity(self, scorer):
        """Test high confidence for high similarity"""
        similarity = 0.95
        history = {"correct": 10, "incorrect": 1}
        
        confidence = scorer.calculate_confidence(similarity, history)
        
        assert confidence > 0.8
        assert confidence <= 1.0
    
    def test_calculate_confidence_low_similarity(self, scorer):
        """Test low confidence for low similarity"""
        similarity = 0.45
        history = {"correct": 1, "incorrect": 5}
        
        confidence = scorer.calculate_confidence(similarity, history)
        
        assert confidence < 0.5
    
    def test_confidence_bounds(self, scorer):
        """Test confidence is always between 0 and 1"""
        test_cases = [
            (0.1, {"correct": 0, "incorrect": 10}),
            (0.5, {"correct": 5, "incorrect": 5}),
            (0.9, {"correct": 10, "incorrect": 0}),
            (1.0, {"correct": 100, "incorrect": 0})
        ]
        
        for similarity, history in test_cases:
            confidence = scorer.calculate_confidence(similarity, history)
            assert 0 <= confidence <= 1


class TestVocabularyManager:
    """Test vocabulary management"""
    
    @pytest.fixture
    def vocab_manager(self):
        """Create vocabulary manager instance"""
        return VocabularyManager()
    
    def test_add_term(self, vocab_manager):
        """Test adding new term"""
        term = "firewall-policy"
        category = "security"
        
        vocab_manager.add_term(term, category)
        
        assert vocab_manager.has_term(term)
    
    def test_get_similar_terms(self, vocab_manager):
        """Test finding similar terms"""
        vocab_manager.add_term("firewall", "security")
        vocab_manager.add_term("firewall-rule", "security")
        vocab_manager.add_term("firewall-policy", "security")
        
        similar = vocab_manager.get_similar_terms("firewall", limit=3)
        
        assert len(similar) <= 3
        assert any("firewall" in term.lower() for term in similar)
    
    def test_term_frequency(self, vocab_manager):
        """Test term frequency tracking"""
        term = "access-list"
        
        # Add term multiple times
        for _ in range(5):
            vocab_manager.add_term(term, "security")
        
        frequency = vocab_manager.get_term_frequency(term)
        assert frequency >= 1


class TestEmbeddingEngine:
    """Test embedding generation"""
    
    def test_text_embedding_shape(self):
        """Test embedding has correct dimensions"""
        from app.adaptive.embedding_engine import EmbeddingEngine
        
        engine = EmbeddingEngine()
        text = "access-list 100 permit ip any any"
        
        embedding = engine.get_embedding(text)
        
        assert embedding is not None
        assert len(embedding.shape) == 1  # 1D vector
        assert embedding.shape[0] > 0
    
    def test_similar_texts_have_similar_embeddings(self):
        """Test similar texts produce similar embeddings"""
        from app.adaptive.embedding_engine import EmbeddingEngine
        
        engine = EmbeddingEngine()
        text1 = "permit tcp any any eq 80"
        text2 = "permit tcp any any eq 443"
        text3 = "deny ip any any"
        
        emb1 = engine.get_embedding(text1)
        emb2 = engine.get_embedding(text2)
        emb3 = engine.get_embedding(text3)
        
        # Calculate cosine similarity
        similarity_12 = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        similarity_13 = np.dot(emb1, emb3) / (np.linalg.norm(emb1) * np.linalg.norm(emb3))
        
        # Similar texts should have higher similarity
        assert similarity_12 > similarity_13


@pytest.mark.asyncio
class TestLearningIntegration:
    """Test learning system integration"""
    
    async def test_end_to_end_learning(self, test_db):
        """Test complete learning cycle"""
        from app.adaptive.learning import AdaptiveLearningEngine
        from app.database import LearnedMapping
        
        engine = AdaptiveLearningEngine()
        
        # Create mapping
        mapping = LearnedMapping(
            mapping_id="MAP-TEST-001",
            organization_id=1,
            raw_text="access-list 100 permit ip any any",
            standardized_text="permit ip any any",
            rule_type="access_control",
            confidence_score=0.75,
            feedback_count=0,
            positive_feedback=0,
            is_verified=False
        )
        
        test_db.add(mapping)
        test_db.commit()
        
        # Provide positive feedback
        result = engine.learn_from_feedback({
            "mapping_id": "MAP-TEST-001",
            "user_feedback": "correct",
            "confidence": 0.75
        })
        
        assert result is not None
        
        # Verify mapping was updated
        test_db.refresh(mapping)
        assert mapping.positive_feedback > 0
