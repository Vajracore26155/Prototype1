"""
Remediation Engine

Provides vendor-specific remediation commands for compliance violations
"""
import os
import yaml
from typing import Optional, Dict


class RemediationEngine:
    """Loads and provides remediation templates"""
    
    def __init__(self, templates_path: Optional[str] = None):
        """Initialize remediation engine"""
        if templates_path is None:
            templates_path = os.path.join(
                os.path.dirname(__file__),
                'templates.yaml'
            )
        
        self.templates = self._load_templates(templates_path)
    
    def _load_templates(self, path: str) -> Dict:
        """Load remediation templates from YAML"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return data.get('remediations', {})
        except Exception as e:
            print(f"Warning: Failed to load remediation templates: {e}")
            return {}
    
    def get_remediation(self, rule_id: str, vendor: str) -> Optional[str]:
        """
        Get remediation command for a rule and vendor
        
        Args:
            rule_id: Rule ID (e.g., "NET-001")
            vendor: Vendor name (e.g., "Cisco", "Fortinet")
            
        Returns:
            Remediation command string or None
        """
        if rule_id not in self.templates:
            return None
        
        template = self.templates[rule_id]
        
        # Get vendor-specific command
        command = template.get(vendor)
        if command:
            return command.strip()
        
        # Fallback to explanation if vendor-specific command not available
        explanation = template.get('explanation')
        if explanation:
            return f"# {explanation.strip()}\n# Vendor-specific command not available"
        
        return None
    
    def get_explanation(self, rule_id: str) -> Optional[str]:
        """Get general remediation explanation"""
        if rule_id not in self.templates:
            return None
        
        template = self.templates[rule_id]
        return template.get('explanation', '').strip()


# Global instance
_remediation_engine = None


def get_remediation_engine() -> RemediationEngine:
    """Get global remediation engine instance"""
    global _remediation_engine
    if _remediation_engine is None:
        _remediation_engine = RemediationEngine()
    return _remediation_engine


def get_remediation(rule_id: str, vendor: str) -> Optional[str]:
    """Convenience function to get remediation"""
    engine = get_remediation_engine()
    return engine.get_remediation(rule_id, vendor)
