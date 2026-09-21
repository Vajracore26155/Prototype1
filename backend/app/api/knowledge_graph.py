"""
Knowledge Graph API
Phase 7.4: Entity relationships and impact analysis
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db, User
from app.auth.dependencies import require_permission
from app.auth.permissions import Permission
from app.knowledge.graph_builder import GraphBuilder, EntityType, RelationType

router = APIRouter()


@router.get("/knowledge-graph")
async def get_knowledge_graph(
    current_user: User = Depends(require_permission(Permission.AUDIT_READ)),
    db: Session = Depends(get_db)
):
    """
    Get complete knowledge graph for organization
    
    Returns all entities and relationships
    """
    try:
        # Build graph
        graph = GraphBuilder.build_from_organization(
            current_user.organization_id,
            db
        )
        
        # Get statistics
        stats = graph.get_statistics()
        
        return {
            "success": True,
            "data": {
                "organization_id": current_user.organization_id,
                "statistics": stats,
                "graph_url": f"/api/knowledge-graph/export"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-graph/export")
async def export_knowledge_graph(
    current_user: User = Depends(require_permission(Permission.AUDIT_READ)),
    db: Session = Depends(get_db)
):
    """Export knowledge graph as JSON"""
    try:
        graph = GraphBuilder.build_from_organization(
            current_user.organization_id,
            db
        )
        
        graph_json = graph.export_json()
        
        return {
            "success": True,
            "data": graph_json
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-graph/entity/{entity_id}")
async def get_entity_details(
    entity_id: str,
    current_user: User = Depends(require_permission(Permission.AUDIT_READ)),
    db: Session = Depends(get_db)
):
    """Get detailed information about an entity"""
    try:
        graph = GraphBuilder.build_from_organization(
            current_user.organization_id,
            db
        )
        
        entity = graph.get_entity(entity_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        # Get neighbors
        neighbors = graph.get_neighbors(entity_id)
        
        return {
            "success": True,
            "data": {
                "entity": {
                    "entity_id": entity.entity_id,
                    "entity_type": entity.entity_type.value,
                    "properties": entity.properties
                },
                "neighbors": [
                    {
                        "entity_id": n.entity_id,
                        "entity_type": n.entity_type.value,
                        "properties": n.properties,
                        "relationship": r.relationship_type.value
                    }
                    for n, r in neighbors
                ],
                "neighbor_count": len(neighbors)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-graph/impact/{entity_id}")
async def analyze_impact(
    entity_id: str,
    current_user: User = Depends(require_permission(Permission.AUDIT_READ)),
    db: Session = Depends(get_db),
    max_depth: int = 3
):
    """
    Analyze impact of changes to an entity
    
    Shows all entities that would be affected
    """
    try:
        graph = GraphBuilder.build_from_organization(
            current_user.organization_id,
            db
        )
        
        impact = graph.get_impact_analysis(entity_id, max_depth)
        
        if "error" in impact:
            raise HTTPException(status_code=404, detail=impact["error"])
        
        return {
            "success": True,
            "data": impact
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-graph/path")
async def find_path(
    start_id: str,
    end_id: str,
    current_user: User = Depends(require_permission(Permission.AUDIT_READ)),
    db: Session = Depends(get_db),
    max_depth: int = 5
):
    """Find shortest path between two entities"""
    try:
        graph = GraphBuilder.build_from_organization(
            current_user.organization_id,
            db
        )
        
        path = graph.find_path(start_id, end_id, max_depth)
        
        if not path:
            raise HTTPException(
                status_code=404,
                detail="No path found between entities"
            )
        
        # Get entity details for path
        path_details = []
        for entity_id in path:
            entity = graph.get_entity(entity_id)
            if entity:
                path_details.append({
                    "entity_id": entity.entity_id,
                    "entity_type": entity.entity_type.value,
                    "properties": entity.properties
                })
        
        return {
            "success": True,
            "data": {
                "start_id": start_id,
                "end_id": end_id,
                "path_length": len(path),
                "path": path_details
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
