"""
Webhook Management API
Phase 7.2: Webhook registration and management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime
import secrets

from app.database import get_db, Webhook, WebhookDelivery, User, SecurityAuditLog
from app.auth.dependencies import require_permission
from app.auth.permissions import Permission

router = APIRouter()


def generate_log_id(db: Session) -> str:
    """Generate unique audit log ID"""
    count = db.query(SecurityAuditLog).count()
    return f"LOG-{count + 1:08d}"


def generate_webhook_secret() -> str:
    """Generate secure webhook secret"""
    return secrets.token_urlsafe(32)


class WebhookCreate(BaseModel):
    """Create webhook request"""
    name: str
    url: HttpUrl
    event_types: List[str]
    description: Optional[str] = None
    headers: Optional[dict] = None
    retry_count: int = 3
    timeout_seconds: int = 30


class WebhookUpdate(BaseModel):
    """Update webhook request"""
    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    event_types: Optional[List[str]] = None
    description: Optional[str] = None
    headers: Optional[dict] = None
    is_active: Optional[bool] = None
    retry_count: Optional[int] = None
    timeout_seconds: Optional[int] = None


@router.post("/webhooks")
async def create_webhook(
    webhook_data: WebhookCreate,
    current_user: User = Depends(require_permission(Permission.SYSTEM_ADMIN)),
    db: Session = Depends(get_db)
):
    """
    Register a new webhook
    
    Requires ADMIN permission
    """
    try:
        # Generate webhook ID
        count = db.query(Webhook).filter(
            Webhook.organization_id == current_user.organization_id
        ).count()
        webhook_id = f"WH-{count + 1:06d}"
        
        # Generate secret
        secret = generate_webhook_secret()
        
        # Create webhook
        webhook = Webhook(
            webhook_id=webhook_id,
            organization_id=current_user.organization_id,
            name=webhook_data.name,
            url=str(webhook_data.url),
            secret=secret,
            event_types=webhook_data.event_types,
            description=webhook_data.description,
            headers=webhook_data.headers,
            retry_count=webhook_data.retry_count,
            timeout_seconds=webhook_data.timeout_seconds,
            is_active=True,
            created_by=current_user.email
        )
        
        db.add(webhook)
        db.commit()
        db.refresh(webhook)
        
        # Log
        log = SecurityAuditLog(
            log_id=generate_log_id(db),
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="WEBHOOK",
            action="CREATE",
            result="SUCCESS",
            resource_type="webhook",
            resource_id=webhook_id,
            details={"name": webhook_data.name, "url": str(webhook_data.url)},
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "webhook_id": webhook_id,
                "name": webhook.name,
                "url": webhook.url,
                "secret": secret,  # Only returned on creation
                "event_types": webhook.event_types,
                "is_active": webhook.is_active,
                "created_at": webhook.created_at.isoformat()
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/webhooks")
async def list_webhooks(
    current_user: User = Depends(require_permission(Permission.CONFIG_READ)),
    db: Session = Depends(get_db),
    is_active: Optional[bool] = None
):
    """List all webhooks for organization"""
    try:
        query = db.query(Webhook).filter(
            Webhook.organization_id == current_user.organization_id
        )
        
        if is_active is not None:
            query = query.filter(Webhook.is_active == is_active)
        
        webhooks = query.order_by(desc(Webhook.created_at)).all()
        
        return {
            "success": True,
            "data": {
                "webhooks": [
                    {
                        "webhook_id": w.webhook_id,
                        "name": w.name,
                        "url": w.url,
                        "event_types": w.event_types,
                        "is_active": w.is_active,
                        "created_at": w.created_at.isoformat(),
                        "last_triggered_at": w.last_triggered_at.isoformat() if w.last_triggered_at else None,
                        "statistics": {
                            "total_deliveries": w.total_deliveries,
                            "successful_deliveries": w.successful_deliveries,
                            "failed_deliveries": w.failed_deliveries,
                            "success_rate": round(w.successful_deliveries / max(w.total_deliveries, 1) * 100, 2)
                        }
                    }
                    for w in webhooks
                ],
                "total": len(webhooks)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/webhooks/{webhook_id}")
async def get_webhook(
    webhook_id: str,
    current_user: User = Depends(require_permission(Permission.CONFIG_READ)),
    db: Session = Depends(get_db)
):
    """Get webhook details"""
    try:
        webhook = db.query(Webhook).filter(
            Webhook.webhook_id == webhook_id,
            Webhook.organization_id == current_user.organization_id
        ).first()
        
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        return {
            "success": True,
            "data": {
                "webhook_id": webhook.webhook_id,
                "name": webhook.name,
                "url": webhook.url,
                "event_types": webhook.event_types,
                "description": webhook.description,
                "headers": webhook.headers,
                "retry_count": webhook.retry_count,
                "timeout_seconds": webhook.timeout_seconds,
                "is_active": webhook.is_active,
                "created_by": webhook.created_by,
                "created_at": webhook.created_at.isoformat(),
                "updated_at": webhook.updated_at.isoformat(),
                "last_triggered_at": webhook.last_triggered_at.isoformat() if webhook.last_triggered_at else None,
                "statistics": {
                    "total_deliveries": webhook.total_deliveries,
                    "successful_deliveries": webhook.successful_deliveries,
                    "failed_deliveries": webhook.failed_deliveries,
                    "success_rate": round(webhook.successful_deliveries / max(webhook.total_deliveries, 1) * 100, 2)
                }
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/webhooks/{webhook_id}")
async def update_webhook(
    webhook_id: str,
    webhook_data: WebhookUpdate,
    current_user: User = Depends(require_permission(Permission.SYSTEM_ADMIN)),
    db: Session = Depends(get_db)
):
    """Update webhook configuration"""
    try:
        webhook = db.query(Webhook).filter(
            Webhook.webhook_id == webhook_id,
            Webhook.organization_id == current_user.organization_id
        ).first()
        
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        # Update fields
        update_data = webhook_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "url" and value:
                setattr(webhook, field, str(value))
            else:
                setattr(webhook, field, value)
        
        webhook.updated_at = datetime.utcnow()
        db.commit()
        
        # Log
        log = SecurityAuditLog(
            log_id=generate_log_id(db),
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="WEBHOOK",
            action="UPDATE",
            result="SUCCESS",
            resource_type="webhook",
            resource_id=webhook_id,
            details=update_data,
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "webhook_id": webhook_id,
                "message": "Webhook updated successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    current_user: User = Depends(require_permission(Permission.SYSTEM_ADMIN)),
    db: Session = Depends(get_db)
):
    """Delete webhook"""
    try:
        webhook = db.query(Webhook).filter(
            Webhook.webhook_id == webhook_id,
            Webhook.organization_id == current_user.organization_id
        ).first()
        
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        # Soft delete - just deactivate
        webhook.is_active = False
        db.commit()
        
        # Log
        log = SecurityAuditLog(
            log_id=generate_log_id(db),
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            event_type="WEBHOOK",
            action="DELETE",
            result="SUCCESS",
            resource_type="webhook",
            resource_id=webhook_id,
            details={"name": webhook.name},
            ip_address="",
            user_agent=""
        )
        db.add(log)
        db.commit()
        
        return {
            "success": True,
            "data": {
                "webhook_id": webhook_id,
                "message": "Webhook deactivated successfully"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/webhooks/{webhook_id}/deliveries")
async def get_webhook_deliveries(
    webhook_id: str,
    current_user: User = Depends(require_permission(Permission.CONFIG_READ)),
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    limit: int = 50
):
    """Get webhook delivery history"""
    try:
        webhook = db.query(Webhook).filter(
            Webhook.webhook_id == webhook_id,
            Webhook.organization_id == current_user.organization_id
        ).first()
        
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        query = db.query(WebhookDelivery).filter(
            WebhookDelivery.webhook_id == webhook.id
        )
        
        if status:
            query = query.filter(WebhookDelivery.status == status)
        
        deliveries = query.order_by(desc(WebhookDelivery.created_at)).limit(limit).all()
        
        return {
            "success": True,
            "data": {
                "webhook_id": webhook_id,
                "deliveries": [
                    {
                        "delivery_id": d.delivery_id,
                        "event_id": d.event_id,
                        "event_type": d.event_type,
                        "status": d.status,
                        "http_status": d.http_status,
                        "attempt_count": d.attempt_count,
                        "error_message": d.error_message,
                        "created_at": d.created_at.isoformat(),
                        "delivered_at": d.delivered_at.isoformat() if d.delivered_at else None,
                        "next_retry_at": d.next_retry_at.isoformat() if d.next_retry_at else None
                    }
                    for d in deliveries
                ],
                "total": len(deliveries)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhooks/{webhook_id}/test")
async def test_webhook(
    webhook_id: str,
    current_user: User = Depends(require_permission(Permission.SYSTEM_ADMIN)),
    db: Session = Depends(get_db)
):
    """Send test event to webhook"""
    try:
        from app.events.event_bus import Event, EventType, create_event
        from app.webhooks.delivery import WebhookDeliveryEngine
        
        webhook = db.query(Webhook).filter(
            Webhook.webhook_id == webhook_id,
            Webhook.organization_id == current_user.organization_id
        ).first()
        
        if not webhook:
            raise HTTPException(status_code=404, detail="Webhook not found")
        
        # Create test event
        test_event = create_event(
            event_type=EventType.SYSTEM_WARNING,
            organization_id=current_user.organization_id,
            resource_type="webhook",
            resource_id=webhook_id,
            data={
                "message": "This is a test webhook delivery",
                "test": True
            },
            user_id=current_user.id,
            metadata={"triggered_by": "manual_test"}
        )
        
        # Deliver
        engine = WebhookDeliveryEngine(db)
        delivery = await engine.deliver_event(webhook, test_event)
        
        return {
            "success": True,
            "data": {
                "delivery_id": delivery.delivery_id,
                "status": delivery.status,
                "http_status": delivery.http_status,
                "message": "Test webhook sent"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
