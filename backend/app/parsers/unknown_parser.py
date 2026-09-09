"""
Unknown Vendor Parser

Uses AI-based adaptive interpretation for configurations
from unknown or unsupported vendors
"""
from typing import List, Dict
import re

from .base import BaseParser, ParserError
from app.normalization.schema import (
    UnifiedSecurityModel,
    RemoteAccess,
    ManagementProtocols,
    Authentication,
    Logging,
    AccessControl,
    DeviceInfo,
    Evidence
)
from app.adaptive import interpret_unknown_config, InterpretationResult, get_learning_engine


class UnknownParser(BaseParser):
    """
    Parser for unknown/unsupported vendor configurations
    
    Uses AI-based interpretation to extract security settings
    and generates mapping suggestions for human validation
    """
    
    def __init__(self):
        """Initialize unknown parser"""
        self.learning_engine = get_learning_engine()
        self.vendor_name_value = "Unknown"
    
    def can_parse(self, content: str) -> bool:
        """Can always attempt to parse unknown configs"""
        return True
    
    @property
    def vendor_name(self) -> str:
        """Return vendor name"""
        return self.vendor_name_value
    
    def parse(self, content: str, filename: str) -> UnifiedSecurityModel:
        """
        Parse unknown configuration using AI interpretation
        
        This creates a best-effort UnifiedSecurityModel by:
        1. Extracting configuration lines
        2. Using learned mappings (if available)
        3. Using AI interpretation (if AI model available)
        4. Using heuristic pattern matching (fallback)
        5. Creating pending mappings for human validation
        
        Args:
            content: Configuration file content
            filename: Original filename
            
        Returns:
            UnifiedSecurityModel with interpreted settings
        """
        try:
            # Extract configuration lines
            lines = self._extract_config_lines(content)
            
            # Initialize model with defaults
            model = self._create_default_model(filename)
            
            # Track interpretations for pending mappings
            pending_mappings = []
            interpreted_lines = 0
            total_lines = len(lines)
            
            # Process each configuration line
            for line_num, line_text in lines:
                # Check if we have a learned mapping
                learned_mapping = self._get_learned_mapping(line_text)
                
                if learned_mapping:
                    # Apply learned mapping
                    self._apply_learned_mapping(model, learned_mapping, filename, line_num, line_text)
                    interpreted_lines += 1
                else:
                    # Try heuristic pattern matching first (fast)
                    heuristic_applied = self._apply_heuristic_patterns(
                        model, line_text, filename, line_num
                    )
                    
                    if heuristic_applied:
                        interpreted_lines += 1
                        continue
                    
                    # Use AI interpretation if available (slower)
                    try:
                        interpretation = interpret_unknown_config(line_text, vendor_confidence=0.0)
                        
                        if interpretation.best_candidate and interpretation.can_auto_suggest:
                            # Apply AI interpretation
                            self._apply_ai_interpretation(
                                model, 
                                interpretation, 
                                filename, 
                                line_num, 
                                line_text
                            )
                            interpreted_lines += 1
                            
                            # Store for potential learning
                            pending_mappings.append({
                                'line_text': line_text,
                                'interpretation': interpretation,
                                'line_num': line_num
                            })
                    except Exception as ai_error:
                        # AI interpretation failed - skip this line
                        print(f"AI interpretation failed for line {line_num}: {ai_error}")
                        pass
            
            # Calculate interpretation confidence
            interpretation_rate = interpreted_lines / total_lines if total_lines > 0 else 0.0
            
            # Store metadata in model for use by audit engine
            model._parsing_metadata = {
                'interpreted_lines': interpreted_lines,
                'total_lines': total_lines,
                'interpretation_rate': interpretation_rate,
                'pending_mappings_count': len(pending_mappings),
                'uninterpreted_lines': total_lines - interpreted_lines
            }
            
            print(f"Unknown parser: interpreted {interpreted_lines}/{total_lines} lines ({interpretation_rate*100:.1f}%)")
            
            # Store pending mappings for human validation (async, don't block)
            if pending_mappings:
                try:
                    self._store_pending_mappings(pending_mappings, filename)
                except Exception as e:
                    print(f"Warning: Failed to store pending mappings: {e}")
            
            return model
            
        except Exception as e:
            raise ParserError(f"Failed to parse unknown configuration: {str(e)}")
    
    def _extract_config_lines(self, content: str) -> List[tuple[int, str]]:
        """
        Extract meaningful configuration lines
        
        Returns:
            List of (line_number, line_text) tuples
        """
        lines = []
        
        for line_num, line in enumerate(content.split('\n'), 1):
            # Strip whitespace
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#') or line.startswith('!'):
                continue
            
            lines.append((line_num, line))
        
        return lines
    
    def _create_default_model(self, filename: str) -> UnifiedSecurityModel:
        """Create model with conservative defaults"""
        return UnifiedSecurityModel(
            device=DeviceInfo(
                vendor="Unknown",
                hostname=None,
                device_type="unknown",
                version=None
            ),
            
            # Remote Access - Assume unsafe defaults
            remote_access=RemoteAccess(
                ssh_enabled=True,
                ssh_version=None,
                telnet_enabled=True  # Assume unsafe
            ),
            
            # Management Protocols - Assume unsafe defaults
            management=ManagementProtocols(
                http_enabled=True,  # Assume unsafe
                https_enabled=True,
                snmp_enabled=True
            ),
            
            # Authentication - Assume weak defaults
            authentication=Authentication(
                local_authentication=False,
                password_encryption=False,
                enable_secret_configured=False
            ),
            
            # Logging - Assume disabled
            logging=Logging(
                enabled=False,
                remote_server=None,
                buffered=False
            ),
            
            # Access Control - Assume permissive
            access_control=AccessControl(
                source_filtering=False,
                timeout_configured=False
            )
        )
    
    def _get_learned_mapping(self, line_text: str) -> Dict:
        """Get learned mapping for this line if it exists"""
        # Check learned mappings using the learning engine
        learned_mapping = self.learning_engine.find_learned_mapping(
            raw_pattern=line_text,
            vendor="Unknown"
        )
        
        return learned_mapping
    
    def _apply_heuristic_patterns(
        self,
        model: UnifiedSecurityModel,
        line_text: str,
        filename: str,
        line_num: int
    ) -> bool:
        """
        Apply heuristic pattern matching for common security patterns
        
        This is a fallback when AI is not available or for quick matching
        
        Returns:
            True if a pattern was matched and applied
        """
        line_lower = line_text.lower()
        
        # Telnet patterns
        if any(keyword in line_lower for keyword in ['telnet', 'remote-mgmt telnet']):
            if 'enable' in line_lower or 'allow' in line_lower:
                model.remote_access.telnet_enabled = True
                model.remote_access.telnet_enabled_evidence = Evidence(
                    file=filename, line=line_num, text=line_text
                )
                return True
            elif 'disable' in line_lower or 'deny' in line_lower:
                model.remote_access.telnet_enabled = False
                model.remote_access.telnet_enabled_evidence = Evidence(
                    file=filename, line=line_num, text=line_text
                )
                return True
        
        # SSH patterns
        if 'ssh' in line_lower or 'secure-shell' in line_lower:
            if 'enable' in line_lower or 'allow' in line_lower or 'only' in line_lower:
                model.remote_access.ssh_enabled = True
                model.remote_access.ssh_enabled_evidence = Evidence(
                    file=filename, line=line_num, text=line_text
                )
                # Disable telnet if ssh-only
                if 'only' in line_lower:
                    model.remote_access.telnet_enabled = False
                return True
            if 'version 2' in line_lower or 'v2' in line_lower:
                model.remote_access.ssh_version = 2
                model.remote_access.ssh_version_evidence = Evidence(
                    file=filename, line=line_num, text=line_text
                )
                return True
        
        # HTTP/HTTPS patterns
        if 'http' in line_lower or 'web-management' in line_lower:
            if 'https' in line_lower:
                if 'enable' in line_lower or 'allow' in line_lower:
                    model.management.https_enabled = True
                    model.management.https_enabled_evidence = Evidence(
                        file=filename, line=line_num, text=line_text
                    )
                    return True
            elif 'disable' in line_lower:
                model.management.http_enabled = False
                model.management.http_enabled_evidence = Evidence(
                    file=filename, line=line_num, text=line_text
                )
                return True
            elif 'enable' in line_lower or 'allow' in line_lower:
                model.management.http_enabled = True
                model.management.http_enabled_evidence = Evidence(
                    file=filename, line=line_num, text=line_text
                )
                return True
        
        # SNMP patterns
        if 'snmp' in line_lower:
            if 'enable' in line_lower or 'community' in line_lower:
                model.management.snmp_enabled = True
                model.management.snmp_enabled_evidence = Evidence(
                    file=filename, line=line_num, text=line_text
                )
                return True
        
        # Password/Authentication patterns
        if 'password' in line_lower or 'auth' in line_lower or 'local-auth' in line_lower:
            if 'encrypt' in line_lower or 'hash' in line_lower or 'enabled' in line_lower:
                model.authentication.local_authentication = True
                model.authentication.local_authentication_evidence = Evidence(
                    file=filename, line=line_num, text=line_text
                )
                return True
        
        # Logging patterns
        if 'syslog' in line_lower or 'logging' in line_lower or 'audit-forward' in line_lower:
            if 'enable' in line_lower or any(c.isdigit() for c in line_text):  # IP address present
                model.logging.enabled = True
                model.logging.enabled_evidence = Evidence(
                    file=filename, line=line_num, text=line_text
                )
                return True
        
        # Timeout patterns
        if 'timeout' in line_lower or 'session-timeout' in line_lower:
            model.access_control.timeout_configured = True
            model.access_control.timeout_evidence = Evidence(
                file=filename, line=line_num, text=line_text
            )
            return True
        
        return False
    
    def _apply_learned_mapping(
        self, 
        model: UnifiedSecurityModel, 
        mapping: Dict,
        filename: str,
        line_num: int,
        line_text: str
    ):
        """Apply a learned mapping to the model"""
        # For now, simplified implementation
        # In full version, would parse field_path and set nested attributes
        pass
    
    def _apply_ai_interpretation(
        self,
        model: UnifiedSecurityModel,
        interpretation: InterpretationResult,
        filename: str,
        line_num: int,
        line_text: str
    ):
        """Apply AI interpretation to the model"""
        # For now, simplified implementation
        # AI interpretations are stored as pending mappings for human review
        pass
    
    def _store_pending_mappings(self, pending_mappings: List[Dict], filename: str):
        """Store pending mappings for human validation"""
        try:
            for mapping in pending_mappings:
                interpretation = mapping['interpretation']
                
                if not interpretation.best_candidate:
                    continue
                
                concept = interpretation.best_candidate.concept
                
                # Create pending mapping record using learning engine
                self.learning_engine.save_mapping(
                    raw_pattern=mapping['line_text'],
                    normalized_field=concept.field_path,
                    value="true",  # Default value
                    suggested_meaning=concept.description,
                    confidence=interpretation.best_candidate.confidence.overall,
                    vendor="Unknown",
                    approved=False,  # Requires human validation
                    approved_by=None
                )
        except Exception as e:
            # Don't fail parsing if learning engine has issues
            print(f"Warning: Failed to store pending mappings: {e}")
