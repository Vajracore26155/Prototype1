"""
Multi-Framework Compliance API Endpoints

Provides endpoints for multi-framework compliance assessment
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel

from app.database.database import get_db
from app.database.models import Configuration, Audit, User
from app.compliance.framework_engine import MultiFrameworkEngine, FrameworkType
from app.normalization.schema import UnifiedSecurityModel
from app.auth.dependencies import require_permission
from app.auth.permissions import Permission

router = APIRouter(prefix="/api/frameworks", tags=["frameworks"])


class FrameworkAssessmentRequest(BaseModel):
    """Request for framework assessment"""
    configuration_id: Optional[int] = None
    audit_id: Optional[int] = None
    frameworks: Optional[List[str]] = None  # If None, assess all


class FrameworkSummaryResponse(BaseModel):
    """Framework summary response"""
    frameworks: Dict
    total_controls: int
    controls_by_framework: Dict


@router.get("/summary", response_model=FrameworkSummaryResponse)
async def get_framework_summary(
    current_user: User = Depends(require_permission(Permission.FRAMEWORK_READ))
):
    """
    Get summary of all supported frameworks
    
    Returns information about loaded frameworks and control counts
    
    SECURITY: Requires FRAMEWORK_READ permission
    """
    engine = MultiFrameworkEngine()
    summary = engine.get_framework_summary()
    
    return FrameworkSummaryResponse(**summary)


@router.post("/assess/configuration/{config_id}")
async def assess_configuration_frameworks(
    config_id: int,
    frameworks: Optional[List[str]] = None,
    current_user: User = Depends(require_permission(Permission.AUDIT_RUN)),
    db: Session = Depends(get_db)
):
    """
    Assess configuration against multiple frameworks
    
    Args:
        config_id: Configuration ID to assess
        frameworks: List of framework names (CIS, NIST_800_53, DISA_STIG, ISO_27001)
                   If None, assesses against all frameworks
    
    Returns:
        Multi-framework assessment results with cross-framework mappings
    
    SECURITY: Requires AUDIT_RUN permission and organization ownership verification
    """
    # Get configuration and verify organization ownership
    config = db.query(Configuration).filter(
        Configuration.id == config_id,
        Configuration.organization_id == current_user.organization_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=404, 
            detail="Configuration not found or access denied"
        )
    
    # Parse normalized model
    try:
        import json
        normalized_dict = json.loads(config.normalized_config)
        unified_model = UnifiedSecurityModel(**normalized_dict)
        flat_dict = unified_model.to_flat_dict()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse normalized config: {str(e)}"
        )
    
    # Initialize engine
    engine = MultiFrameworkEngine()
    
    # Determine which frameworks to assess
    if frameworks:
        framework_types = []
        for fw_name in frameworks:
            try:
                framework_types.append(FrameworkType(fw_name))
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid framework: {fw_name}. Valid: CIS, NIST_800_53, DISA_STIG, ISO_27001"
                )
        
        # Assess selected frameworks
        results = {}
        for framework in framework_types:
            assessment = engine.assess_framework(framework, flat_dict)
            results[framework.value] = {
                'framework': assessment.framework.value,
                'version': assessment.version,
                'total_controls': assessment.total_controls,
                'applicable_controls': assessment.applicable_controls,
                'compliant_controls': assessment.compliant_controls,
                'non_compliant_controls': assessment.non_compliant_controls,
                'not_applicable_controls': assessment.not_applicable_controls,
                'compliance_percentage': round(assessment.compliance_percentage, 2),
                'control_results': assessment.control_results,
                'assessed_at': assessment.assessed_at
            }
    else:
        # Assess all frameworks
        all_results = engine.assess_all_frameworks(flat_dict)
        results = {}
        for framework, assessment in all_results.items():
            results[framework.value] = {
                'framework': assessment.framework.value,
                'version': assessment.version,
                'total_controls': assessment.total_controls,
                'applicable_controls': assessment.applicable_controls,
                'compliant_controls': assessment.compliant_controls,
                'non_compliant_controls': assessment.non_compliant_controls,
                'not_applicable_controls': assessment.not_applicable_controls,
                'compliance_percentage': round(assessment.compliance_percentage, 2),
                'control_results': assessment.control_results,
                'assessed_at': assessment.assessed_at
            }
    
    return {
        'configuration_id': config_id,
        'hostname': config.hostname,
        'vendor': config.vendor,
        'frameworks_assessed': list(results.keys()),
        'assessments': results,
        'summary': {
            'avg_compliance': round(
                sum(r['compliance_percentage'] for r in results.values()) / len(results),
                2
            ) if results else 0.0,
            'total_controls_evaluated': sum(r['applicable_controls'] for r in results.values()),
            'total_compliant': sum(r['compliant_controls'] for r in results.values()),
            'total_non_compliant': sum(r['non_compliant_controls'] for r in results.values())
        }
    }


@router.get("/controls/{framework}")
async def get_framework_controls(
    framework: str,
    current_user: User = Depends(require_permission(Permission.FRAMEWORK_READ))
):
    """
    Get all controls for a specific framework
    
    Args:
        framework: Framework name (CIS, NIST_800_53, DISA_STIG, ISO_27001)
    
    Returns:
        List of controls with mappings
    
    SECURITY: Requires FRAMEWORK_READ permission
    """
    try:
        framework_type = FrameworkType(framework)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid framework: {framework}. Valid: CIS, NIST_800_53, DISA_STIG, ISO_27001"
        )
    
    engine = MultiFrameworkEngine()
    
    # Filter controls for this framework
    framework_controls = [
        {
            'control_id': control.control_id,
            'framework': control.framework.value,
            'version': control.version,
            'title': control.title,
            'description': control.description,
            'severity': control.severity.value,
            'category': control.category,
            'technical_checks': control.technical_checks,
            'expected_values': control.expected_values,
            'mapped_controls': {
                fw.value: ids for fw, ids in control.mapped_controls.items()
            },
            'tags': control.tags,
            'references': control.references
        }
        for control in engine.controls.values()
        if control.framework == framework_type
    ]
    
    return {
        'framework': framework,
        'version': engine.frameworks[framework_type].version,
        'control_count': len(framework_controls),
        'controls': framework_controls
    }


@router.get("/mappings/{framework}/{control_id}")
async def get_control_mappings(
    framework: str, 
    control_id: str,
    current_user: User = Depends(require_permission(Permission.FRAMEWORK_READ))
):
    """
    Get cross-framework mappings for a specific control
    
    Args:
        framework: Framework name
        control_id: Control ID
    
    Returns:
        Related controls across all frameworks
    
    SECURITY: Requires FRAMEWORK_READ permission
    """
    try:
        framework_type = FrameworkType(framework)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid framework: {framework}"
        )
    
    engine = MultiFrameworkEngine()
    control_key = f"{framework}:{control_id}"
    
    # Get the control
    control = engine.controls.get(control_key)
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    
    # Get all mapped controls
    mapped_keys = engine.get_control_mappings(control_key)
    mapped_controls = []
    
    for mapped_key in mapped_keys:
        mapped_control = engine.controls.get(mapped_key)
        if mapped_control:
            mapped_controls.append({
                'control_id': mapped_control.control_id,
                'framework': mapped_control.framework.value,
                'title': mapped_control.title,
                'severity': mapped_control.severity.value
            })
    
    return {
        'control': {
            'control_id': control.control_id,
            'framework': control.framework.value,
            'title': control.title,
            'description': control.description,
            'severity': control.severity.value
        },
        'mapped_controls': mapped_controls,
        'mapping_count': len(mapped_controls)
    }
