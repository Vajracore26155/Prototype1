"""
Search Indexer
Phase 7.5: Advanced search and filtering capabilities
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import re


class SearchIndex:
    """
    In-memory search index for fast querying
    
    In production, this would use Elasticsearch or similar
    """
    
    def __init__(self):
        self.documents: Dict[str, Dict] = {}
        self.inverted_index: Dict[str, set] = {}
        self.facets: Dict[str, Dict[str, int]] = {}
    
    def index_document(self, doc_id: str, document: Dict):
        """
        Index a document for search
        
        Args:
            doc_id: Unique document identifier
            document: Document to index
        """
        self.documents[doc_id] = document
        
        # Build inverted index
        for field, value in document.items():
            if isinstance(value, str):
                # Tokenize and index
                tokens = self._tokenize(value)
                for token in tokens:
                    if token not in self.inverted_index:
                        self.inverted_index[token] = set()
                    self.inverted_index[token].add(doc_id)
        
        # Build facets
        for field, value in document.items():
            if field in ['type', 'status', 'severity', 'category', 'vendor']:
                if field not in self.facets:
                    self.facets[field] = {}
                str_value = str(value)
                self.facets[field][str_value] = self.facets[field].get(str_value, 0) + 1
    
    def _tokenize(self, text: str) -> List[str]:
        """
        Tokenize text for indexing
        
        Lowercase, split on whitespace and punctuation
        """
        text = text.lower()
        tokens = re.findall(r'\w+', text)
        return tokens
    
    def search(
        self,
        query: str,
        filters: Optional[Dict] = None,
        sort_by: Optional[str] = None,
        limit: int = 50
    ) -> Dict:
        """
        Search indexed documents
        
        Args:
            query: Search query
            filters: Field filters
            sort_by: Field to sort by
            limit: Maximum results
        
        Returns:
            Search results with metadata
        """
        # Tokenize query
        query_tokens = self._tokenize(query) if query else []
        
        # Find matching documents
        if query_tokens:
            matching_docs = None
            for token in query_tokens:
                token_docs = self.inverted_index.get(token, set())
                if matching_docs is None:
                    matching_docs = token_docs
                else:
                    matching_docs = matching_docs.intersection(token_docs)
            
            if matching_docs is None:
                matching_docs = set()
        else:
            # No query, return all documents
            matching_docs = set(self.documents.keys())
        
        # Apply filters
        if filters:
            matching_docs = self._apply_filters(matching_docs, filters)
        
        # Get documents
        results = [self.documents[doc_id] for doc_id in matching_docs]
        
        # Sort
        if sort_by and results:
            reverse = sort_by.startswith('-')
            field = sort_by.lstrip('-')
            results.sort(key=lambda x: x.get(field, ''), reverse=reverse)
        
        # Limit
        total = len(results)
        results = results[:limit]
        
        return {
            "results": results,
            "total": total,
            "limit": limit,
            "facets": self.get_facets(matching_docs)
        }
    
    def _apply_filters(self, doc_ids: set, filters: Dict) -> set:
        """Apply filters to document set"""
        filtered = set()
        
        for doc_id in doc_ids:
            doc = self.documents[doc_id]
            match = True
            
            for field, value in filters.items():
                if field not in doc:
                    match = False
                    break
                
                if isinstance(value, list):
                    if doc[field] not in value:
                        match = False
                        break
                else:
                    if doc[field] != value:
                        match = False
                        break
            
            if match:
                filtered.add(doc_id)
        
        return filtered
    
    def get_facets(self, doc_ids: Optional[set] = None) -> Dict:
        """
        Get facet counts
        
        If doc_ids provided, only count those documents
        """
        if doc_ids is None:
            return self.facets
        
        # Calculate facets for subset
        subset_facets: Dict[str, Dict[str, int]] = {}
        
        for doc_id in doc_ids:
            doc = self.documents.get(doc_id, {})
            for field in ['type', 'status', 'severity', 'category', 'vendor']:
                if field in doc:
                    if field not in subset_facets:
                        subset_facets[field] = {}
                    value = str(doc[field])
                    subset_facets[field][value] = subset_facets[field].get(value, 0) + 1
        
        return subset_facets
    
    def suggest(self, prefix: str, field: str = 'title', limit: int = 10) -> List[str]:
        """
        Auto-suggest completions
        
        Args:
            prefix: Prefix to match
            field: Field to search
            limit: Maximum suggestions
        
        Returns:
            List of suggestions
        """
        suggestions = set()
        prefix_lower = prefix.lower()
        
        for doc in self.documents.values():
            if field in doc:
                value = str(doc[field])
                if value.lower().startswith(prefix_lower):
                    suggestions.add(value)
                    if len(suggestions) >= limit:
                        break
        
        return sorted(list(suggestions))[:limit]


class UniversalSearchEngine:
    """
    Universal search across all entity types
    """
    
    def __init__(self):
        self.indices: Dict[str, SearchIndex] = {
            'devices': SearchIndex(),
            'audits': SearchIndex(),
            'findings': SearchIndex(),
            'configurations': SearchIndex(),
            'users': SearchIndex()
        }
    
    def index_from_database(self, db):
        """
        Build search indices from database
        
        Args:
            db: Database session
        """
        from app.database import Device, Audit, Finding, Configuration, User
        
        # Index devices
        devices = db.query(Device).all()
        for device in devices:
            self.indices['devices'].index_document(
                device.device_id,
                {
                    'id': device.device_id,
                    'type': 'device',
                    'organization_id': device.organization_id,  # SECURITY: Organization isolation
                    'vendor': device.vendor or '',
                    'model': device.model or '',
                    'status': device.status or '',
                    'hostname': device.hostname or '',
                    'title': f"{device.vendor} {device.model} - {device.hostname}"
                }
            )
        
        # Index audits
        audits = db.query(Audit).all()
        for audit in audits:
            self.indices['audits'].index_document(
                audit.audit_id,
                {
                    'id': audit.audit_id,
                    'type': 'audit',
                    'organization_id': audit.organization_id,  # SECURITY: Organization isolation
                    'status': audit.status,
                    'risk_level': audit.risk_level or '',
                    'compliance_score': audit.compliance_score or 0,
                    'created_at': audit.started_at.isoformat() if audit.started_at else ''
                }
            )
        
        # Index findings (inherit organization from audit)
        findings = db.query(Finding).join(Audit).all()
        for finding in findings:
            # Get the audit to access organization_id
            audit = db.query(Audit).filter(Audit.id == finding.audit_id).first()
            self.indices['findings'].index_document(
                finding.finding_id,
                {
                    'id': finding.finding_id,
                    'type': 'finding',
                    'organization_id': audit.organization_id if audit else None,  # SECURITY: Organization isolation
                    'title': finding.title or '',
                    'severity': finding.severity or '',
                    'description': finding.description or '',
                    'status': finding.status or ''
                }
            )
        
        # Index configurations
        configs = db.query(Configuration).all()
        for config in configs:
            self.indices['configurations'].index_document(
                config.config_id,
                {
                    'id': config.config_id,
                    'type': 'configuration',
                    'organization_id': config.organization_id,  # SECURITY: Organization isolation
                    'filename': config.filename or '',
                    'vendor': config.vendor or '',
                    'status': config.status or ''
                }
            )
    
    def search_all(
        self,
        query: str,
        entity_types: Optional[List[str]] = None,
        filters: Optional[Dict] = None,
        limit: int = 50
    ) -> Dict:
        """
        Search across all entity types
        
        Args:
            query: Search query
            entity_types: Limit to specific types
            filters: Field filters
            limit: Maximum results per type
        
        Returns:
            Combined search results
        """
        if entity_types is None:
            entity_types = list(self.indices.keys())
        
        all_results = []
        facets_combined = {}
        
        for entity_type in entity_types:
            if entity_type in self.indices:
                index = self.indices[entity_type]
                results = index.search(query, filters, limit=limit)
                
                # Add to combined results
                for result in results['results']:
                    result['_type'] = entity_type
                    all_results.append(result)
                
                # Merge facets
                for facet_field, facet_values in results['facets'].items():
                    if facet_field not in facets_combined:
                        facets_combined[facet_field] = {}
                    for value, count in facet_values.items():
                        facets_combined[facet_field][value] = \
                            facets_combined[facet_field].get(value, 0) + count
        
        return {
            "results": all_results[:limit],
            "total": len(all_results),
            "by_type": {
                et: len([r for r in all_results if r['_type'] == et])
                for et in entity_types
            },
            "facets": facets_combined
        }


# Global search engine instance
search_engine = UniversalSearchEngine()
