"""
Semantic Embedding Engine

Uses sentence-transformers to compute semantic similarity
between unknown configuration commands and known security concepts
"""
import os
from typing import List, Tuple, Optional
import numpy as np
from dataclasses import dataclass

# Import sentence transformers (will be loaded on first use)
_model = None


def get_model():
    """Lazy load the sentence transformer model"""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            model_name = os.getenv("AI_MODEL", "all-MiniLM-L6-v2")
            print(f"Loading embedding model: {model_name}")
            _model = SentenceTransformer(model_name)
            print("✓ Embedding model loaded successfully")
        except Exception as e:
            print(f"Warning: Failed to load embedding model: {e}")
            print("AI features will be limited")
            _model = None
    return _model


@dataclass
class EmbeddingResult:
    """Result of embedding computation"""
    text: str
    embedding: np.ndarray
    model_name: str


class EmbeddingEngine:
    """
    Computes semantic embeddings for text
    
    Uses sentence-transformers to convert text into dense vectors
    that can be compared using cosine similarity
    """
    
    def __init__(self):
        """Initialize embedding engine"""
        self.model = get_model()
        self.model_name = os.getenv("AI_MODEL", "all-MiniLM-L6-v2")
    
    def is_available(self) -> bool:
        """Check if embedding model is available"""
        return self.model is not None
    
    def embed(self, text: str) -> Optional[EmbeddingResult]:
        """
        Compute embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            EmbeddingResult or None if model unavailable
        """
        if not self.is_available():
            return None
        
        try:
            # Normalize text
            text = text.lower().strip()
            
            # Compute embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            return EmbeddingResult(
                text=text,
                embedding=embedding,
                model_name=self.model_name
            )
        except Exception as e:
            print(f"Embedding error: {e}")
            return None
    
    def embed_batch(self, texts: List[str]) -> List[Optional[EmbeddingResult]]:
        """
        Compute embeddings for multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of EmbeddingResults
        """
        if not self.is_available():
            return [None] * len(texts)
        
        try:
            # Normalize texts
            normalized = [t.lower().strip() for t in texts]
            
            # Compute embeddings in batch
            embeddings = self.model.encode(normalized, convert_to_numpy=True)
            
            results = []
            for text, embedding in zip(texts, embeddings):
                results.append(EmbeddingResult(
                    text=text.lower().strip(),
                    embedding=embedding,
                    model_name=self.model_name
                ))
            
            return results
        except Exception as e:
            print(f"Batch embedding error: {e}")
            return [None] * len(texts)
    
    def cosine_similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        try:
            # Normalize vectors
            norm1 = embedding1 / np.linalg.norm(embedding1)
            norm2 = embedding2 / np.linalg.norm(embedding2)
            
            # Compute cosine similarity
            similarity = np.dot(norm1, norm2)
            
            # Ensure result is in [0, 1]
            # (cosine similarity can be -1 to 1, we map to 0 to 1)
            similarity = (similarity + 1.0) / 2.0
            
            return float(similarity)
        except Exception as e:
            print(f"Similarity calculation error: {e}")
            return 0.0
    
    def find_most_similar(
        self,
        query_embedding: np.ndarray,
        candidate_embeddings: List[Tuple[str, np.ndarray]]
    ) -> List[Tuple[str, float]]:
        """
        Find most similar candidates to query
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of (text, embedding) tuples
            
        Returns:
            List of (text, similarity_score) tuples, sorted by similarity
        """
        similarities = []
        
        for text, embedding in candidate_embeddings:
            similarity = self.cosine_similarity(query_embedding, embedding)
            similarities.append((text, similarity))
        
        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities


# Global instance
_embedding_engine = None


def get_embedding_engine() -> EmbeddingEngine:
    """Get global embedding engine instance"""
    global _embedding_engine
    if _embedding_engine is None:
        _embedding_engine = EmbeddingEngine()
    return _embedding_engine
