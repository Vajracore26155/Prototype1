"""
Knowledge Graph Builder
Phase 7.4: Entity relationship mapping and impact analysis
"""
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import json


class EntityType(str, Enum):
    """Entity types in knowledge graph"""
    DEVICE = "device"
    CONFIGURATION = "configuration"
    FINDING = "finding"
    AUDIT = "audit"
    RULE = "rule"
    USER = "user"
    ORGANIZATION = "organization"
    INTERFACE = "interface"
    VLAN = "vlan"
    ACL = "acl"
    ROUTE = "route"
    SERVICE = "service"


class RelationType(str, Enum):
    """Relationship types"""
    CONTAINS = "contains"
    AFFECTS = "affects"
    DEPENDS_ON = "depends_on"
    RELATED_TO = "related_to"
    CONFIGURED_BY = "configured_by"
    AUDITED_BY = "audited_by"
    FOUND_IN = "found_in"
    MITIGATES = "mitigates"
    OWNS = "owns"
    MEMBER_OF = "member_of"


@dataclass
class Entity:
    """Graph entity"""
    entity_id: str
    entity_type: EntityType
    properties: Dict
    
    def __hash__(self):
        return hash(self.entity_id)
    
    def __eq__(self, other):
        return isinstance(other, Entity) and self.entity_id == other.entity_id


@dataclass
class Relationship:
    """Graph relationship"""
    source_id: str
    target_id: str
    relationship_type: RelationType
    properties: Dict
    
    def __hash__(self):
        return hash((self.source_id, self.target_id, self.relationship_type))


class KnowledgeGraph:
    """
    Knowledge graph for network security entities
    
    Tracks relationships between devices, configurations,
    findings, audits, and other entities
    """
    
    def __init__(self):
        self.entities: Dict[str, Entity] = {}
        self.relationships: List[Relationship] = []
        self.index: Dict[EntityType, Set[str]] = {}
    
    def add_entity(self, entity: Entity):
        """Add entity to graph"""
        self.entities[entity.entity_id] = entity
        
        # Update index
        if entity.entity_type not in self.index:
            self.index[entity.entity_type] = set()
        self.index[entity.entity_type].add(entity.entity_id)
    
    def add_relationship(self, relationship: Relationship):
        """Add relationship to graph"""
        # Verify entities exist
        if relationship.source_id not in self.entities:
            raise ValueError(f"Source entity not found: {relationship.source_id}")
        if relationship.target_id not in self.entities:
            raise ValueError(f"Target entity not found: {relationship.target_id}")
        
        self.relationships.append(relationship)
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID"""
        return self.entities.get(entity_id)
    
    def get_entities_by_type(self, entity_type: EntityType) -> List[Entity]:
        """Get all entities of a type"""
        entity_ids = self.index.get(entity_type, set())
        return [self.entities[eid] for eid in entity_ids]
    
    def get_relationships(
        self,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        relationship_type: Optional[RelationType] = None
    ) -> List[Relationship]:
        """Get relationships matching criteria"""
        results = self.relationships
        
        if source_id:
            results = [r for r in results if r.source_id == source_id]
        if target_id:
            results = [r for r in results if r.target_id == target_id]
        if relationship_type:
            results = [r for r in results if r.relationship_type == relationship_type]
        
        return results
    
    def get_neighbors(
        self,
        entity_id: str,
        relationship_type: Optional[RelationType] = None
    ) -> List[Tuple[Entity, Relationship]]:
        """
        Get neighboring entities
        
        Returns entities connected to the given entity
        """
        neighbors = []
        
        # Outgoing relationships
        for rel in self.get_relationships(source_id=entity_id, relationship_type=relationship_type):
            target = self.get_entity(rel.target_id)
            if target:
                neighbors.append((target, rel))
        
        # Incoming relationships
        for rel in self.get_relationships(target_id=entity_id, relationship_type=relationship_type):
            source = self.get_entity(rel.source_id)
            if source:
                neighbors.append((source, rel))
        
        return neighbors
    
    def get_impact_analysis(self, entity_id: str, max_depth: int = 3) -> Dict:
        """
        Analyze impact of changes to an entity
        
        Performs BFS to find all affected entities
        """
        if entity_id not in self.entities:
            return {"error": "Entity not found"}
        
        entity = self.entities[entity_id]
        visited = set()
        affected = []
        queue = [(entity_id, 0)]
        
        while queue:
            current_id, depth = queue.pop(0)
            
            if current_id in visited or depth > max_depth:
                continue
            
            visited.add(current_id)
            current_entity = self.entities[current_id]
            
            if depth > 0:  # Don't include the source entity
                affected.append({
                    "entity_id": current_id,
                    "entity_type": current_entity.entity_type.value,
                    "properties": current_entity.properties,
                    "depth": depth
                })
            
            # Find affected entities
            for rel in self.get_relationships(source_id=current_id):
                if rel.relationship_type in [RelationType.AFFECTS, RelationType.CONTAINS]:
                    queue.append((rel.target_id, depth + 1))
        
        return {
            "source_entity": {
                "entity_id": entity_id,
                "entity_type": entity.entity_type.value,
                "properties": entity.properties
            },
            "affected_entities": affected,
            "total_affected": len(affected),
            "max_depth": max(e["depth"] for e in affected) if affected else 0
        }
    
    def find_path(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 5
    ) -> Optional[List[str]]:
        """
        Find shortest path between two entities
        
        Uses BFS to find the shortest path
        """
        if start_id not in self.entities or end_id not in self.entities:
            return None
        
        visited = set()
        queue = [(start_id, [start_id])]
        
        while queue:
            current_id, path = queue.pop(0)
            
            if current_id == end_id:
                return path
            
            if current_id in visited or len(path) > max_depth:
                continue
            
            visited.add(current_id)
            
            # Explore neighbors
            for neighbor, rel in self.get_neighbors(current_id):
                if neighbor.entity_id not in visited:
                    queue.append((neighbor.entity_id, path + [neighbor.entity_id]))
        
        return None
    
    def get_statistics(self) -> Dict:
        """Get graph statistics"""
        entity_counts = {}
        for entity_type in EntityType:
            entity_counts[entity_type.value] = len(self.index.get(entity_type, set()))
        
        relationship_counts = {}
        for rel_type in RelationType:
            count = len([r for r in self.relationships if r.relationship_type == rel_type])
            relationship_counts[rel_type.value] = count
        
        return {
            "total_entities": len(self.entities),
            "total_relationships": len(self.relationships),
            "entities_by_type": entity_counts,
            "relationships_by_type": relationship_counts
        }
    
    def export_json(self) -> str:
        """Export graph as JSON"""
        data = {
            "entities": [
                {
                    "entity_id": e.entity_id,
                    "entity_type": e.entity_type.value,
                    "properties": e.properties
                }
                for e in self.entities.values()
            ],
            "relationships": [
                {
                    "source_id": r.source_id,
                    "target_id": r.target_id,
                    "relationship_type": r.relationship_type.value,
                    "properties": r.properties
                }
                for r in self.relationships
            ]
        }
        return json.dumps(data, indent=2)


class GraphBuilder:
    """
    Build knowledge graph from database entities
    """
    
    @staticmethod
    def build_from_organization(organization_id: int, db) -> KnowledgeGraph:
        """
        Build knowledge graph for an organization
        
        Args:
            organization_id: Organization ID
            db: Database session
        
        Returns:
            Populated knowledge graph
        """
        from app.database import (
            Device, Configuration, Audit, Finding,
            Organization, User
        )
        
        graph = KnowledgeGraph()
        
        # Add organization
        org = db.query(Organization).filter(Organization.id == organization_id).first()
        if org:
            graph.add_entity(Entity(
                entity_id=f"ORG-{org.id}",
                entity_type=EntityType.ORGANIZATION,
                properties={"name": org.name}
            ))
        
        # Add devices
        devices = db.query(Device).filter(Device.organization_id == organization_id).all()
        for device in devices:
            graph.add_entity(Entity(
                entity_id=device.device_id,
                entity_type=EntityType.DEVICE,
                properties={
                    "vendor": device.vendor,
                    "model": device.model,
                    "status": device.status
                }
            ))
            
            # Link to organization
            graph.add_relationship(Relationship(
                source_id=f"ORG-{org.id}",
                target_id=device.device_id,
                relationship_type=RelationType.OWNS,
                properties={}
            ))
        
        # Add configurations
        configs = db.query(Configuration).filter(
            Configuration.organization_id == organization_id
        ).all()
        for config in configs:
            graph.add_entity(Entity(
                entity_id=config.config_id,
                entity_type=EntityType.CONFIGURATION,
                properties={
                    "filename": config.filename,
                    "vendor": config.vendor,
                    "status": config.status
                }
            ))
        
        # Add audits
        audits = db.query(Audit).filter(Audit.organization_id == organization_id).all()
        for audit in audits:
            graph.add_entity(Entity(
                entity_id=audit.audit_id,
                entity_type=EntityType.AUDIT,
                properties={
                    "compliance_score": audit.compliance_score,
                    "risk_level": audit.risk_level,
                    "status": audit.status
                }
            ))
            
            # Link audit to configuration
            config = db.query(Configuration).filter(
                Configuration.id == audit.configuration_id
            ).first()
            if config:
                graph.add_relationship(Relationship(
                    source_id=audit.audit_id,
                    target_id=config.config_id,
                    relationship_type=RelationType.AUDITED_BY,
                    properties={}
                ))
        
        # Add findings
        findings = db.query(Finding).filter(
            Finding.organization_id == organization_id
        ).all()
        for finding in findings:
            graph.add_entity(Entity(
                entity_id=finding.finding_id,
                entity_type=EntityType.FINDING,
                properties={
                    "title": finding.title,
                    "severity": finding.severity,
                    "category": finding.category
                }
            ))
            
            # Link finding to audit
            audit = db.query(Audit).filter(Audit.id == finding.audit_id).first()
            if audit:
                graph.add_relationship(Relationship(
                    source_id=finding.finding_id,
                    target_id=audit.audit_id,
                    relationship_type=RelationType.FOUND_IN,
                    properties={}
                ))
            
            # Link finding to device
            if finding.device_id:
                graph.add_relationship(Relationship(
                    source_id=finding.finding_id,
                    target_id=finding.device_id,
                    relationship_type=RelationType.AFFECTS,
                    properties={}
                ))
        
        return graph
