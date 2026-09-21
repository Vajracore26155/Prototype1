"""
AI/LLM API Endpoints
Phase 6: Natural language queries, remediation suggestions, config generation
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db, User, Device, Finding, SecurityAuditLog
from app.auth.dependencies import require_permission
from app.auth.permissions import Permission
from app.llm import get_llm_router, get_cost_tracker
from app.llm.router import TaskType

router = APIRouter()


class QueryRequest(BaseModel):
    """Natural language query request"""
    query: str
    context: Optional[str] = "organization_wide"
    model: Optional[str] = None


class RemediationRequest(BaseModel):
    """Remediation suggestion request"""
    finding_id: str
    device_id: str
    prefer_quality: bool = True
    model: Optional[str] = None


class ConfigGenerationRequest(BaseModel):
    """Configuration generation request"""
    requirements: str
    vendor: str
    device_type: Optional[str] = None
    model: Optional[str] = None


@router.post("/ai/query")
async def natural_language_query(
    request: QueryRequest,
    current_user: User = Depends(require_permission(Permission.AI_INTERPRET)),
    db: Session = Depends(get_db)
):
    """
    Process natural language query about security posture
    
    Examples:
    - "Show me all devices with insecure SSH configuration"
    - "What are the top 5 critical findings?"
    - "List devices in DC1 with compliance score below 70"
    """
    try:
        llm_router = get_llm_router()
        cost_tracker = get_cost_tracker()
        
        # Check cost limits
        estimated_cost = 0.01  # Rough estimate
        allowed, reason = cost_tracker.check_limits(
            current_user.id,
            current_user.organization_id,
            estimated_cost
        )
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "success": False,
                    "error": {
                        "code": "COST_LIMIT_EXCEEDED",
                        "message": reason
                    }
                }
            )
        
        # Build context for LLM
        context_info = f"""
Organization: {current_user.organization_id}
User Query: {request.query}
Context: {request.context}

Please analyze this query and provide a helpful response about network security posture.
If the query asks for specific data, explain what information would be retrieved.
        """
        
        # Generate response
        response = await llm_router.complete(
            prompt=context_info,
            task_type=TaskType.QUERY,
            model=request.model,
            max_tokens=500
        )
        
        # Track cost
        cost_tracker.track_usage(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            provider=response.provider,
            model=response.model,
            tokens=response.tokens_used,
            cost=response.cost
        )
        
        # Log action
        log = SecurityAuditLog(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            action="AI_QUERY",
            resource_type="ai",
            resource_id="",
            details=f"Natural language query: {request.query[:100]}",
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "query": request.query,
                "response": response.content,
                "model": response.model,
                "provider": response.provider,
                "tokens_used": response.tokens_used,
                "cost": response.cost,
                "cached": response.cached
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "QUERY_FAILED",
                    "message": f"Failed to process query: {str(e)}"
                }
            }
        )


@router.post("/ai/remediation/suggest")
async def suggest_remediation(
    request: RemediationRequest,
    current_user: User = Depends(require_permission(Permission.AI_INTERPRET)),
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered remediation suggestions for a finding
    """
    try:
        # Get finding
        finding = db.query(Finding).filter(
            Finding.finding_id == request.finding_id
        ).first()
        
        if not finding:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Finding {request.finding_id} not found"
                    }
                }
            )
        
        # Get device
        device = db.query(Device).filter(
            Device.device_id == request.device_id,
            Device.organization_id == current_user.organization_id
        ).first()
        
        if not device:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Device {request.device_id} not found"
                    }
                }
            )
        
        llm_router = get_llm_router()
        cost_tracker = get_cost_tracker()
        
        # Check cost limits (higher for remediation)
        estimated_cost = 0.05
        allowed, reason = cost_tracker.check_limits(
            current_user.id,
            current_user.organization_id,
            estimated_cost
        )
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "success": False,
                    "error": {
                        "code": "COST_LIMIT_EXCEEDED",
                        "message": reason
                    }
                }
            )
        
        # Build remediation prompt
        prompt = f"""
Generate detailed remediation steps for the following security finding:

Device: {device.hostname} ({device.vendor} {device.device_type})
Finding: {finding.title}
Severity: {finding.severity}
Description: {finding.description}
Current State: {finding.actual}
Expected State: {finding.expected}

Please provide:
1. Step-by-step remediation commands (vendor-specific)
2. Verification steps
3. Potential impact assessment
4. Rollback procedure if needed

Format the response in a clear, actionable way.
        """
        
        # Generate remediation
        response = await llm_router.complete(
            prompt=prompt,
            task_type=TaskType.REMEDIATION,
            model=request.model,
            max_tokens=1500
        )
        
        # Track cost
        cost_tracker.track_usage(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            provider=response.provider,
            model=response.model,
            tokens=response.tokens_used,
            cost=response.cost
        )
        
        # Log action
        log = SecurityAuditLog(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            action="AI_REMEDIATION",
            resource_type="ai",
            resource_id=finding.finding_id,
            details=f"Generated remediation for finding {finding.finding_id}",
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "finding_id": request.finding_id,
                "device_id": request.device_id,
                "remediation": response.content,
                "model": response.model,
                "provider": response.provider,
                "tokens_used": response.tokens_used,
                "cost": response.cost
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "REMEDIATION_FAILED",
                    "message": f"Failed to generate remediation: {str(e)}"
                }
            }
        )


@router.post("/ai/config/generate")
async def generate_configuration(
    request: ConfigGenerationRequest,
    current_user: User = Depends(require_permission(Permission.CONFIG_UPLOAD)),
    db: Session = Depends(get_db)
):
    """
    Generate secure configuration from natural language requirements
    """
    try:
        llm_router = get_llm_router()
        cost_tracker = get_cost_tracker()
        
        # Check cost limits
        estimated_cost = 0.1  # Higher for generation
        allowed, reason = cost_tracker.check_limits(
            current_user.id,
            current_user.organization_id,
            estimated_cost
        )
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "success": False,
                    "error": {
                        "code": "COST_LIMIT_EXCEEDED",
                        "message": reason
                    }
                }
            )
        
        # Build generation prompt
        prompt = f"""
Generate a secure {request.vendor} configuration based on these requirements:

Requirements:
{request.requirements}

Device Type: {request.device_type or 'Router'}
Vendor: {request.vendor}

Please generate:
1. Complete configuration file
2. Security best practices applied
3. Explanation of key security settings
4. Compliance considerations

The configuration should follow {request.vendor} syntax and include:
- Secure remote access (SSH v2, no Telnet)
- Strong authentication (AAA if applicable)
- Comprehensive logging
- Proper access controls
        """
        
        # Generate config
        response = await llm_router.complete(
            prompt=prompt,
            task_type=TaskType.GENERATION,
            model=request.model,
            max_tokens=2000
        )
        
        # Track cost
        cost_tracker.track_usage(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            provider=response.provider,
            model=response.model,
            tokens=response.tokens_used,
            cost=response.cost
        )
        
        # Log action
        log = SecurityAuditLog(
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            action="AI_CONFIG_GENERATION",
            resource_type="ai",
            resource_id="",
            details=f"Generated {request.vendor} configuration",
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "vendor": request.vendor,
                "configuration": response.content,
                "model": response.model,
                "provider": response.provider,
                "tokens_used": response.tokens_used,
                "cost": response.cost,
                "warning": "AI-generated configuration should be reviewed by a network engineer before deployment"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "GENERATION_FAILED",
                    "message": f"Failed to generate configuration: {str(e)}"
                }
            }
        )


@router.get("/ai/usage")
async def get_ai_usage(
    current_user: User = Depends(require_permission(Permission.USER_READ)),
    db: Session = Depends(get_db)
):
    """
    Get AI/LLM usage statistics
    """
    try:
        cost_tracker = get_cost_tracker()
        
        user_usage = cost_tracker.get_user_usage(current_user.id)
        org_usage = cost_tracker.get_organization_usage(current_user.organization_id)
        
        return {
            "success": True,
            "data": {
                "user": user_usage,
                "organization": org_usage
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "GET_FAILED",
                    "message": "Failed to retrieve usage statistics"
                }
            }
        )


@router.get("/ai/providers")
async def get_available_providers(
    current_user: User = Depends(require_permission(Permission.USER_READ))
):
    """
    Get list of available LLM providers
    """
    try:
        llm_router = get_llm_router()
        providers = llm_router.get_available_providers()
        
        return {
            "success": True,
            "data": {
                "providers": providers,
                "default": llm_router.default_provider
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": {
                    "code": "GET_FAILED",
                    "message": "Failed to retrieve providers"
                }
            }
        )
