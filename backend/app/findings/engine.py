"""
Audit Orchestration Engine

Coordinates the entire audit pipeline:
1. Load configuration
2. Parse → Unified Security Model
3. Evaluate compliance
4. Calculate risk
5. Generate remediation
6. Create findings with evidence
"""
from typing import Optional
from datetime import datetime

from app.storage import read_file
from app.parsers import CiscoParser, FortinetParser, UnknownParser, ParserError
from app.normalization import UnifiedSecurityModel
from app.compliance import ComplianceEvaluator, ComplianceResult
from app.risk import RiskScorer, RiskScore
from app.remediation import get_remediation_engine
from app.database import Configuration, Audit, Finding, get_db_session
from app.storage import generate_audit_id, generate_finding_id


class AuditOrchestrator:
    """
    Orchestrates the complete audit pipeline
    
    This is the canonical audit workflow
    """
    
    def __init__(self):
        self.cisco_parser = CiscoParser()
        self.fortinet_parser = FortinetParser()
        self.unknown_parser = UnknownParser()
        self.evaluator = ComplianceEvaluator()
        self.risk_scorer = RiskScorer()
        self.remediation_engine = get_remediation_engine()
    
    def run_audit(self, configuration: Configuration) -> Audit:
        """
        Run complete security audit on a configuration
        
        Args:
            configuration: Configuration database object
            
        Returns:
            Audit database object with results
        """
        db = get_db_session()
        
        try:
            # Create audit record
            audit = Audit(
                audit_id=generate_audit_id(),
                configuration_id=configuration.id,
                status="PROCESSING",
                started_at=datetime.utcnow()
            )
            db.add(audit)
            db.commit()
            db.refresh(audit)
            
            # Step 1: Load sanitized configuration
            config_content = read_file(configuration.sanitized_path)
            
            # Step 2: Parse configuration
            if configuration.vendor == "Cisco":
                model = self.cisco_parser.parse(config_content, configuration.original_filename)
            elif configuration.vendor == "Fortinet":
                model = self.fortinet_parser.parse(config_content, configuration.original_filename)
            else:
                # Use adaptive AI parser for unknown vendors
                print(f"Using AI-based parser for unknown vendor: {configuration.vendor}")
                model = self.unknown_parser.parse(config_content, configuration.original_filename)
                
                # Check if human review is needed based on interpretation quality
                if hasattr(model, '_parsing_metadata'):
                    metadata = model._parsing_metadata
                    interpretation_rate = metadata.get('interpretation_rate', 0.0)
                    uninterpreted_lines = metadata.get('uninterpreted_lines', 0)
                    pending_mappings_count = metadata.get('pending_mappings_count', 0)
                    
                    # Store metadata in audit record
                    audit.interpretation_confidence = interpretation_rate
                    audit.uninterpreted_lines_count = uninterpreted_lines
                    audit.total_lines_count = metadata.get('total_lines', 0)
                    audit.pending_mappings_count = pending_mappings_count
                    
                    # Determine if human review is needed
                    # Thresholds:
                    # - <30% interpretation rate = definitely needs review
                    # - 30-60% = needs review if significant config (>20 lines)
                    # - >60% = review recommended but not critical
                    
                    review_reasons = []
                    
                    if interpretation_rate < 0.30:
                        audit.requires_human_review = True
                        review_reasons.append(f"Low interpretation rate ({interpretation_rate*100:.1f}%)")
                    elif interpretation_rate < 0.60 and audit.total_lines_count > 20:
                        audit.requires_human_review = True
                        review_reasons.append(f"Medium interpretation rate ({interpretation_rate*100:.1f}%) with significant config size")
                    elif uninterpreted_lines > 50:
                        audit.requires_human_review = True
                        review_reasons.append(f"Many uninterpreted lines ({uninterpreted_lines})")
                    elif pending_mappings_count > 10:
                        audit.requires_human_review = True
                        review_reasons.append(f"Many AI suggestions pending validation ({pending_mappings_count})")
                    
                    if audit.requires_human_review:
                        audit.review_reason = "; ".join(review_reasons)
                        audit.status = "NEEDS_REVIEW"
                        print(f"⚠️  Audit flagged for human review: {audit.review_reason}")
            
            # Store normalized data
            audit.normalized_data = model.model_dump(mode='json')
            
            # Step 3: Evaluate compliance
            compliance_results = self.evaluator.evaluate(model)
            
            # Step 4: Generate findings
            findings = []
            for result in compliance_results:
                finding = self._create_finding(audit, result, model, configuration.vendor)
                findings.append(finding)
                db.add(finding)
            
            # Step 5: Calculate summary
            summary = self.evaluator.get_summary(compliance_results)
            aggregate_risk = self.risk_scorer.calculate_aggregate_risk(compliance_results)
            
            # Update audit record
            if not audit.requires_human_review:
                audit.status = "COMPLETED"
            # else: keep status as "NEEDS_REVIEW" set during parsing
            
            audit.compliance_score = summary['compliance_score']
            audit.risk_score = aggregate_risk.score
            audit.risk_level = aggregate_risk.level
            audit.passed_count = summary['passed']
            audit.failed_count = summary['failed']
            audit.warning_count = summary['warning']
            audit.completed_at = datetime.utcnow()
            
            # Update configuration status
            configuration.status = "COMPLETED"
            
            db.commit()
            db.refresh(audit)
            
            return audit
            
        except Exception as e:
            # Mark audit as failed
            if audit:
                audit.status = "FAILED"
                audit.error_message = str(e)
                audit.completed_at = datetime.utcnow()
                db.commit()
            
            raise
        finally:
            db.close()
    
    def _create_finding(
        self,
        audit: Audit,
        result: ComplianceResult,
        model: UnifiedSecurityModel,
        vendor: str
    ) -> Finding:
        """Create finding from compliance result"""
        
        # Calculate risk for this finding
        risk = self.risk_scorer.calculate_finding_risk(result)
        
        # Get remediation
        remediation = None
        if result.status.value == "FAIL":
            remediation = self.remediation_engine.get_remediation(result.rule_id, vendor)
        
        # Extract evidence
        evidence_file = None
        evidence_line = None
        evidence_text = None
        if result.evidence:
            evidence_file = result.evidence.file
            evidence_line = result.evidence.line
            evidence_text = result.evidence.text
        
        # Create finding
        finding = Finding(
            finding_id=generate_finding_id(),
            audit_id=audit.id,
            rule_id=result.rule_id,
            title=result.rule_name,
            description=result.explanation,
            status=result.status.value,
            severity=result.severity.value,
            expected=str(result.expected) if result.expected is not None else None,
            actual=str(result.actual) if result.actual is not None else None,
            field_path=result.field,
            evidence_file=evidence_file,
            evidence_line=evidence_line,
            evidence_text=evidence_text,
            risk_score=risk.score if result.status.value == "FAIL" else 0.0,
            remediation=remediation,
            created_at=datetime.utcnow()
        )
        
        return finding


def run_configuration_audit(config_id: str) -> Audit:
    """
    Convenience function to run audit by configuration ID
    
    Args:
        config_id: Configuration ID (e.g., "CFG-000001")
        
    Returns:
        Completed Audit object
    """
    db = get_db_session()
    try:
        configuration = db.query(Configuration).filter(
            Configuration.config_id == config_id
        ).first()
        
        if not configuration:
            raise ValueError(f"Configuration {config_id} not found")
        
        orchestrator = AuditOrchestrator()
        return orchestrator.run_audit(configuration)
    finally:
        db.close()
