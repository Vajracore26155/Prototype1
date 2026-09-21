"""
Universal Search API
Phase 7.5: Advanced search and filtering
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db, User
from app.auth.dependencies import require_permission
from app.auth.permissions import Permission
from app.search.indexer import search_engine

router = APIRouter()


@router.post("/search/reindex")
async def reindex_search(
    current_user: User = Depends(require_permission(Permission.SYSTEM_ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Rebuild search indices
    
    Admin only - rebuilds all search indices from database
    """
    try:
        search_engine.index_from_database(db)
        
        return {
            "success": True,
            "data": {
                "message": "Search indices rebuilt successfully",
                "indices": list(search_engine.indices.keys())
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def universal_search(
    q: str = Query(..., min_length=1, description="Search query"),
    types: Optional[List[str]] = Query(None, description="Entity types to search"),
    severity: Optional[List[str]] = Query(None, description="Filter by severity"),
    status: Optional[List[str]] = Query(None, description="Filter by status"),
    vendor: Optional[List[str]] = Query(None, description="Filter by vendor"),
    limit: int = Query(50, le=100, description="Maximum results"),
    current_user: User = Depends(require_permission(Permission.AUDIT_READ)),
    db: Session = Depends(get_db)
):
    """
    Universal search across all entities
    
    Searches devices, audits, findings, configurations
    
    SECURITY: Results are automatically filtered by user's organization
    """
    try:
        # Build filters WITH organization scope
        filters = {
            'organization_id': current_user.organization_id  # SECURITY: Organization isolation
        }
        
        if severity:
            filters['severity'] = severity
        if status:
            filters['status'] = status
        if vendor:
            filters['vendor'] = vendor
        
        # Search with organization-scoped filters
        results = search_engine.search_all(
            query=q,
            entity_types=types,
            filters=filters,
            limit=limit
        )
        
        return {
            "success": True,
            "data": {
                "query": q,
                "results": results['results'],
                "total": results['total'],
                "by_type": results['by_type'],
                "facets": results['facets']
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/suggest")
async def search_suggest(
    q: str = Query(..., min_length=1, description="Prefix for suggestions"),
    field: str = Query("title", description="Field to search"),
    entity_type: str = Query("findings", description="Entity type"),
    limit: int = Query(10, le=20, description="Maximum suggestions"),
    current_user: User = Depends(require_permission(Permission.AUDIT_READ))
):
    """
    Auto-suggest completions
    
    Provides search suggestions as user types
    
    SECURITY: Suggestions are filtered by user's organization
    """
    try:
        if entity_type not in search_engine.indices:
            raise HTTPException(status_code=400, detail="Invalid entity type")
        
        index = search_engine.indices[entity_type]
        
        # Add organization filter to suggestions
        filters = {'organization_id': current_user.organization_id}
        suggestions = index.suggest(q, field, limit, filters=filters)
        
        return {
            "success": True,
            "data": {
                "query": q,
                "suggestions": suggestions
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/facets")
async def get_search_facets(
    entity_type: str = Query(..., description="Entity type"),
    current_user: User = Depends(require_permission(Permission.AUDIT_READ))
):
    """
    Get available facets for filtering
    
    Returns possible filter values and their counts
    
    SECURITY: Facets are scoped to user's organization
    """
    try:
        if entity_type not in search_engine.indices:
            raise HTTPException(status_code=400, detail="Invalid entity type")
        
        index = search_engine.indices[entity_type]
        
        # Get facets filtered by organization
        filters = {'organization_id': current_user.organization_id}
        facets = index.get_facets(filters=filters)
        
        return {
            "success": True,
            "data": {
                "entity_type": entity_type,
                "facets": facets
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
