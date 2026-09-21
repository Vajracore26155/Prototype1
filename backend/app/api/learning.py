"""
AI Learning API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db, LearnedMapping, User
from app.adaptive import interpret_unknown_config, get_learning_engine
from app.auth.dependencies import require_permission
from app.auth.permissions import Permission

router = APIRouter()


class InterpretRequest(BaseModel):
    """Request to interpret unknown configuration"""
    text: str
    vendor: Optional[str] = "Unknown"


class AcceptMappingRequest(BaseModel):
    """Request to accept an AI mapping"""
    raw_pattern: str
    normalized_field: str
    value: str
    suggested_meaning: str
    confidence: float
    vendor: Optional[str] = "Unknown"
    approved_by: Optional[str] = "admin"


class UpdateMappingRequest(BaseModel):
    """Request to update a mapping"""
    normalized_field: Optional[str] = None
    value: Optional[str] = None
    suggested_meaning: Optional[str] = None


@router.post("/learning/interpret")
async def interpret_configuration(
    request: InterpretRequest,
    current_user: User = Depends(require_permission(Permission.AI_INTERPRET)),
    db: Session = Depends(get_db)
):
    """
    Interpret unknown configuration syntax using AI
    
    Uses semantic similarity to suggest security meaning
    """
    try:
        # Check if we have a learned mapping first
        learning_engine = get_learning_engine()
        learned = learning_engine.find_learned_mapping(request.text, request.vendor)
        
        if learned:
            return {
                "success": True,
                "data": {
                    "raw_text": request.text,
                    "source": "learned",
                    "mapping": {
                        "mapping_id": learned.mapping_id,
                        "normalized_field": learned.normalized_field,
                        "value": learned.value,
                        "suggested_meaning": learned.suggested_meaning,
                        "confidence": learned.confidence,
                        "usage_count": learned.usage_count
                    },
                    "message": "Using previously learned mapping"
                }
            }
        
        # No learned mapping, use AI interpretation
        result = interpret_unknown_config(request.text)
        
        if result.error_message:
            return {
                "success": False,
                "error": {
                    "code": "INTERPRETATION_ERROR",
                    "message": result.error_message
                }
            }
        
        if not result.best_candidate:
            return {
                "success": False,
                "error": {
                    "code": "NO_MATCH",
                    "message": "Could not find matching security concept"
                }
            }
        
        # Return best candidate
        best = result.best_candidate
        
        return {
            "success": True,
            "data": {
                "raw_text": result.raw_text,
                "source": "ai",
                "interpretation": {
                    "concept_id": best.concept.concept_id,
                    "category": best.concept.category,
                    "normalized_field": best.concept.normalized_field,
                    "value": best.concept.value,
                    "suggested_meaning": best.concept.description,
                    "confidence": best.confidence.overall,
                    "confidence_level": best.confidence.confidence_level,
                    "confidence_breakdown": best.confidence.factors,
                    "explanation": best.confidence.explanation
                },
                "requires_validation": result.requires_validation,
                "can_auto_suggest": result.can_auto_suggest,
                "all_candidates": [
                    {
                        "rank": c.rank,
                        "concept_id": c.concept.concept_id,
                        "normalized_field": c.concept.normalized_field,
                        "value": c.concept.value,
                        "confidence": c.confidence.overall
                    }
                    for c in result.all_candidates[:5]
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "INTERPRETATION_FAILED",
                    "message": f"Failed to interpret configuration: {str(e)}"
                }
            }
        )


@router.get("/learning/pending")
async def get_pending_mappings(
    current_user: User = Depends(require_permission(Permission.AI_REVIEW)),
    db: Session = Depends(get_db)
):
    """
    Get pending AI interpretations for human validation
    """
    try:
        learning_engine = get_learning_engine()
        mappings = learning_engine.get_pending_mappings()
        
        return {
            "success": True,
            "data": {
                "pending_mappings": [
                    {
                        "mapping_id": m.mapping_id,
                        "vendor": m.vendor,
                        "raw_pattern": m.raw_pattern,
                        "normalized_field": m.normalized_field,
                        "value": m.value,
                        "suggested_meaning": m.suggested_meaning,
                        "confidence": m.confidence,
                        "created_at": m.created_at.isoformat()
                    }
                    for m in mappings
                ],
                "total": len(mappings)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "GET_FAILED",
                    "message": "Failed to retrieve pending mappings"
                }
            }
        )


@router.post("/learning/mapping")
async def accept_mapping(
    request: AcceptMappingRequest,
    current_user: User = Depends(require_permission(Permission.AI_APPROVE)),
    db: Session = Depends(get_db)
):
    """
    Accept and save an AI-suggested mapping
    """
    try:
        learning_engine = get_learning_engine()
        
        mapping = learning_engine.save_mapping(
            raw_pattern=request.raw_pattern,
            normalized_field=request.normalized_field,
            value=request.value,
            suggested_meaning=request.suggested_meaning,
            confidence=request.confidence,
            vendor=request.vendor,
            approved=True,
            approved_by=current_user.email
        )
        
        return {
            "success": True,
            "data": {
                "mapping_id": mapping.mapping_id,
                "message": "Mapping accepted and saved successfully"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "SAVE_FAILED",
                    "message": f"Failed to save mapping: {str(e)}"
                }
            }
        )


@router.post("/learning/mapping/{mapping_id}/reject")
async def reject_mapping(
    mapping_id: str,
    current_user: User = Depends(require_permission(Permission.AI_REJECT)),
    db: Session = Depends(get_db)
):
    """
    Reject an AI-suggested mapping
    """
    try:
        learning_engine = get_learning_engine()
        success = learning_engine.reject_mapping(mapping_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Mapping {mapping_id} not found"
                    }
                }
            )
        
        return {
            "success": True,
            "data": {
                "message": "Mapping rejected successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "REJECT_FAILED",
                    "message": "Failed to reject mapping"
                }
            }
        )


@router.patch("/learning/mapping/{mapping_id}")
async def update_mapping(
    mapping_id: str,
    request: UpdateMappingRequest,
    current_user: User = Depends(require_permission(Permission.AI_APPROVE)),
    db: Session = Depends(get_db)
):
    """
    Update a mapping (human correction)
    """
    try:
        learning_engine = get_learning_engine()
        
        success = learning_engine.update_mapping(
            mapping_id=mapping_id,
            normalized_field=request.normalized_field,
            value=request.value,
            suggested_meaning=request.suggested_meaning
        )
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Mapping {mapping_id} not found"
                    }
                }
            )
        
        return {
            "success": True,
            "data": {
                "message": "Mapping updated successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "UPDATE_FAILED",
                    "message": "Failed to update mapping"
                }
            }
        )
