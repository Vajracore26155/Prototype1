"""
Webhook Delivery Engine
Phase 7.2: Reliable webhook delivery with retry logic
"""
import hmac
import hashlib
import json
import asyncio
from typing import Dict, Optional
from datetime import datetime, timedelta
import httpx
from sqlalchemy.orm import Session

from app.database import Webhook, WebhookDelivery, EventLog
from app.events.event_bus import Event


class WebhookDeliveryEngine:
    """
    Handles webhook delivery with retry logic and monitoring
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.max_retries = 3
        self.timeout = 30
    
    async def deliver_event(self, webhook: Webhook, event: Event) -> WebhookDelivery:
        """
        Deliver an event to a webhook endpoint
        
        Returns WebhookDelivery record with status
        """
        # Check if webhook should receive this event
        if event.event_type.value not in webhook.event_types:
            return None
        
        # Create delivery record
        delivery_count = self.db.query(WebhookDelivery).count()
        delivery_id = f"DEL-{delivery_count + 1:08d}"
        
        # Prepare payload
        payload = self._prepare_payload(event, webhook)
        
        # Create delivery record
        delivery = WebhookDelivery(
            delivery_id=delivery_id,
            webhook_id=webhook.id,
            event_id=event.event_id,
            event_type=event.event_type.value,
            payload=payload,
            status="PENDING",
            attempt_count=0
        )
        
        self.db.add(delivery)
        self.db.commit()
        self.db.refresh(delivery)
        
        # Attempt delivery
        success = await self._attempt_delivery(webhook, delivery, payload)
        
        # Update webhook statistics
        webhook.total_deliveries += 1
        webhook.last_triggered_at = datetime.utcnow()
        
        if success:
            webhook.successful_deliveries += 1
            delivery.status = "DELIVERED"
            delivery.delivered_at = datetime.utcnow()
        else:
            webhook.failed_deliveries += 1
            delivery.status = "FAILED"
            
            # Schedule retry if attempts remaining
            if delivery.attempt_count < webhook.retry_count:
                delivery.status = "PENDING_RETRY"
                delivery.next_retry_at = self._calculate_next_retry(delivery.attempt_count)
        
        self.db.commit()
        return delivery
    
    async def _attempt_delivery(
        self,
        webhook: Webhook,
        delivery: WebhookDelivery,
        payload: Dict
    ) -> bool:
        """
        Attempt to deliver webhook payload
        
        Returns True if successful, False otherwise
        """
        delivery.attempt_count += 1
        
        try:
            # Generate signature
            signature = self._generate_signature(webhook.secret, payload)
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "X-Webhook-Signature": signature,
                "X-Webhook-Delivery": delivery.delivery_id,
                "X-Webhook-Event": delivery.event_type,
                "User-Agent": "VAJRA-Webhook/1.0"
            }
            
            # Add custom headers
            if webhook.headers:
                headers.update(webhook.headers)
            
            # Send request
            async with httpx.AsyncClient(timeout=webhook.timeout_seconds) as client:
                response = await client.post(
                    webhook.url,
                    json=payload,
                    headers=headers
                )
            
            # Update delivery record
            delivery.http_status = response.status_code
            delivery.response_body = response.text[:5000]  # Limit size
            
            # Success if 2xx status
            if 200 <= response.status_code < 300:
                return True
            else:
                delivery.error_message = f"HTTP {response.status_code}: {response.text[:500]}"
                return False
        
        except httpx.TimeoutException as e:
            delivery.error_message = f"Timeout after {webhook.timeout_seconds}s"
            return False
        
        except Exception as e:
            delivery.error_message = f"Error: {str(e)[:500]}"
            return False
        
        finally:
            self.db.commit()
    
    def _prepare_payload(self, event: Event, webhook: Webhook) -> Dict:
        """Prepare webhook payload"""
        return {
            "event_id": event.event_id,
            "event_type": event.event_type.value,
            "timestamp": event.timestamp,
            "organization_id": event.organization_id,
            "resource_type": event.resource_type,
            "resource_id": event.resource_id,
            "data": event.data,
            "metadata": event.metadata,
            "webhook": {
                "webhook_id": webhook.webhook_id,
                "name": webhook.name
            }
        }
    
    def _generate_signature(self, secret: str, payload: Dict) -> str:
        """
        Generate HMAC-SHA256 signature for webhook security
        
        Signature = HMAC-SHA256(secret, payload)
        """
        payload_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        signature = hmac.new(
            secret.encode('utf-8'),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    def _calculate_next_retry(self, attempt_count: int) -> datetime:
        """
        Calculate next retry time with exponential backoff
        
        Delays: 1min, 5min, 15min
        """
        delays = [1, 5, 15]  # minutes
        delay = delays[min(attempt_count, len(delays) - 1)]
        return datetime.utcnow() + timedelta(minutes=delay)
    
    async def process_retry_queue(self):
        """
        Process pending retry deliveries
        
        Should be called periodically by a background worker
        """
        # Get deliveries ready for retry
        now = datetime.utcnow()
        pending = self.db.query(WebhookDelivery).filter(
            WebhookDelivery.status == "PENDING_RETRY",
            WebhookDelivery.next_retry_at <= now
        ).all()
        
        for delivery in pending:
            webhook = self.db.query(Webhook).filter(
                Webhook.id == delivery.webhook_id
            ).first()
            
            if webhook and webhook.is_active:
                success = await self._attempt_delivery(
                    webhook,
                    delivery,
                    delivery.payload
                )
                
                if success:
                    delivery.status = "DELIVERED"
                    delivery.delivered_at = datetime.utcnow()
                elif delivery.attempt_count >= webhook.retry_count:
                    delivery.status = "FAILED"
                else:
                    delivery.next_retry_at = self._calculate_next_retry(delivery.attempt_count)
                
                self.db.commit()


async def deliver_to_webhooks(event: Event, db: Session):
    """
    Deliver event to all matching webhooks
    
    Called by event bus when events are published
    """
    # Get active webhooks for this organization
    webhooks = db.query(Webhook).filter(
        Webhook.organization_id == event.organization_id,
        Webhook.is_active == True
    ).all()
    
    # Deliver to matching webhooks
    engine = WebhookDeliveryEngine(db)
    
    for webhook in webhooks:
        try:
            await engine.deliver_event(webhook, event)
        except Exception as e:
            print(f"Webhook delivery error: {e}")
            # Continue with other webhooks
