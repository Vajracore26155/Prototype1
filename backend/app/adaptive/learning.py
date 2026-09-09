"""
Learning System - Stores and Reuses Validated Mappings

When administrators validate AI interpretations, the system learns
and can reuse those mappings for future similar configurations
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.database import LearnedMapping, get_db_session
from app.storage import generate_mapping_id


class LearningEngine:
    """
    Manages learned configuration mappings
    
    Workflow:
    1. AI suggests interpretation
    2. Human validates (accept/reject/modify)
    3. If accepted, store mapping
    4. Future similar patterns reuse mapping
    """
    
    def __init__(self):
        """Initialize learning engine"""
        pass
    
    def find_learned_mapping(
        self,
        raw_pattern: str,
        vendor: str = "Unknown"
    ) -> Optional[dict]:
        """
        Find existing learned mapping for pattern
        
        Args:
            raw_pattern: Raw configuration text
            vendor: Vendor name
            
        Returns:
            Mapping dict if found, None otherwise
        """
        db = get_db_session()
        try:
            # Look for exact match first
            mapping = db.query(LearnedMapping).filter(
                LearnedMapping.raw_pattern == raw_pattern,
                LearnedMapping.vendor == vendor,
                LearnedMapping.approved == True
            ).first()
            
            if mapping:
                # Increment usage count
                mapping.usage_count += 1
                db.commit()
                
                # Return as dict to avoid detached instance issues
                return {
                    "mapping_id": mapping.mapping_id,
                    "vendor": mapping.vendor,
                    "raw_pattern": mapping.raw_pattern,
                    "normalized_field": mapping.normalized_field,
                    "value": mapping.value,
                    "suggested_meaning": mapping.suggested_meaning,
                    "confidence": mapping.confidence,
                    "usage_count": mapping.usage_count
                }
            
            # Could implement fuzzy matching here in future
            return None
            
        finally:
            db.close()
    
    def save_mapping(
        self,
        raw_pattern: str,
        normalized_field: str,
        value: str,
        suggested_meaning: str,
        confidence: float,
        vendor: str = "Unknown",
        approved: bool = False,
        approved_by: Optional[str] = None
    ) -> LearnedMapping:
        """
        Save a new learned mapping
        
        Args:
            raw_pattern: Raw configuration text
            normalized_field: Normalized field path (e.g., "remote_access.ssh_enabled")
            value: Value (e.g., "true")
            suggested_meaning: Human-readable meaning
            confidence: AI confidence score
            vendor: Vendor name
            approved: Whether mapping is approved
            approved_by: Who approved it
            
        Returns:
            Created LearnedMapping
        """
        db = get_db_session()
        try:
            mapping = LearnedMapping(
                mapping_id=generate_mapping_id(),
                vendor=vendor,
                raw_pattern=raw_pattern,
                normalized_field=normalized_field,
                value=value,
                suggested_meaning=suggested_meaning,
                confidence=confidence,
                approved=approved,
                approved_by=approved_by,
                created_at=datetime.utcnow(),
                approved_at=datetime.utcnow() if approved else None,
                usage_count=0
            )
            
            db.add(mapping)
            db.commit()
            db.refresh(mapping)
            
            return mapping
            
        finally:
            db.close()
    
    def approve_mapping(
        self,
        mapping_id: str,
        approved_by: Optional[str] = None
    ) -> bool:
        """
        Approve a pending mapping
        
        Args:
            mapping_id: Mapping ID
            approved_by: Who approved it
            
        Returns:
            True if successful
        """
        db = get_db_session()
        try:
            mapping = db.query(LearnedMapping).filter(
                LearnedMapping.mapping_id == mapping_id
            ).first()
            
            if not mapping:
                return False
            
            mapping.approved = True
            mapping.approved_by = approved_by
            mapping.approved_at = datetime.utcnow()
            
            db.commit()
            return True
            
        finally:
            db.close()
    
    def reject_mapping(self, mapping_id: str) -> bool:
        """
        Reject and delete a mapping
        
        Args:
            mapping_id: Mapping ID
            
        Returns:
            True if successful
        """
        db = get_db_session()
        try:
            mapping = db.query(LearnedMapping).filter(
                LearnedMapping.mapping_id == mapping_id
            ).first()
            
            if not mapping:
                return False
            
            db.delete(mapping)
            db.commit()
            return True
            
        finally:
            db.close()
    
    def update_mapping(
        self,
        mapping_id: str,
        normalized_field: Optional[str] = None,
        value: Optional[str] = None,
        suggested_meaning: Optional[str] = None
    ) -> bool:
        """
        Update a mapping (human correction)
        
        Args:
            mapping_id: Mapping ID
            normalized_field: New field path (optional)
            value: New value (optional)
            suggested_meaning: New meaning (optional)
            
        Returns:
            True if successful
        """
        db = get_db_session()
        try:
            mapping = db.query(LearnedMapping).filter(
                LearnedMapping.mapping_id == mapping_id
            ).first()
            
            if not mapping:
                return False
            
            if normalized_field:
                mapping.normalized_field = normalized_field
            if value:
                mapping.value = value
            if suggested_meaning:
                mapping.suggested_meaning = suggested_meaning
            
            db.commit()
            return True
            
        finally:
            db.close()
    
    def get_pending_mappings(self) -> List[LearnedMapping]:
        """
        Get all pending (unapproved) mappings
        
        Returns:
            List of pending LearnedMappings
        """
        db = get_db_session()
        try:
            mappings = db.query(LearnedMapping).filter(
                LearnedMapping.approved == False
            ).order_by(LearnedMapping.created_at.desc()).all()
            
            return mappings
            
        finally:
            db.close()
    
    def get_all_approved_mappings(self) -> List[LearnedMapping]:
        """Get all approved mappings"""
        db = get_db_session()
        try:
            mappings = db.query(LearnedMapping).filter(
                LearnedMapping.approved == True
            ).order_by(LearnedMapping.usage_count.desc()).all()
            
            return mappings
            
        finally:
            db.close()


# Global instance
_learning_engine = None


def get_learning_engine() -> LearningEngine:
    """Get global learning engine instance"""
    global _learning_engine
    if _learning_engine is None:
        _learning_engine = LearningEngine()
    return _learning_engine
