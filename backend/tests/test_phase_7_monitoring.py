"""
Phase 7 Monitoring System Tests
Comprehensive test coverage for monitoring, events, and webhooks
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.main import app
from app.database import Base, get_db


# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestMonitoringSystem:
    """Test monitoring dashboard and APIs"""
    
    def test_health_endpoint(self):
        """Test basic health check"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_monitoring_dashboard_unauthorized(self):
        """Test dashboard requires authentication"""
        response = client.get("/api/monitoring/dashboard")
        assert response.status_code in [401, 403]
    
    def test_change_detector_initialization(self):
        """Test change detector can be initialized"""
        from app.monitoring.change_detector import ChangeDetector
        
        detector = ChangeDetector()
        assert detector is not None
        assert len(detector.CRITICAL_KEYWORDS) > 0
        assert len(detector.SECURITY_KEYWORDS) > 0


class TestEventSystem:
    """Test event bus and event handling"""
    
    def test_event_creation(self):
        """Test event can be created"""
        from app.events.event_bus import Event, EventType
        
        event = Event(
            event_id="TEST-001",
            event_type=EventType.CONFIG_UPLOADED,
            timestamp=datetime.utcnow().isoformat(),
            organization_id=1,
            user_id=1,
            resource_type="configuration",
            resource_id="CFG-001",
            data={"test": True},
            metadata={}
        )
        
        assert event.event_id == "TEST-001"
        assert event.event_type == EventType.CONFIG_UPLOADED
    
    def test_event_bus_subscription(self):
        """Test event bus subscription"""
        from app.events.event_bus import EventBus, EventType
        
        bus = EventBus()
        handler_called = []
        
        def test_handler(event):
            handler_called.append(event.event_id)
        
        bus.subscribe(EventType.CONFIG_UPLOADED, test_handler)
        assert EventType.CONFIG_UPLOADED in bus._handlers
    
    def test_event_history(self):
        """Test event history tracking"""
        from app.events.event_bus import EventBus, Event, EventType
        
        bus = EventBus()
        history = bus.get_history()
        assert isinstance(history, list)


class TestWebhookSystem:
    """Test webhook management and delivery"""
    
    def test_webhook_secret_generation(self):
        """Test webhook secret is secure"""
        from app.api.webhooks import generate_webhook_secret
        
        secret1 = generate_webhook_secret()
        secret2 = generate_webhook_secret()
        
        assert len(secret1) > 30
        assert secret1 != secret2
    
    def test_webhook_signature_generation(self):
        """Test HMAC signature generation"""
        from app.webhooks.delivery import WebhookDeliveryEngine
        from app.database import get_db
        
        db = next(override_get_db())
        engine = WebhookDeliveryEngine(db)
        
        payload = {"test": "data"}
        signature = engine._generate_signature("secret123", payload)
        
        assert signature.startswith("sha256=")
        assert len(signature) > 10


class TestConfigurationVersioning:
    """Test configuration version management"""
    
    def test_content_hash_generation(self):
        """Test content hashing"""
        from app.api.config_versions import calculate_content_hash
        
        content1 = "hostname router1"
        content2 = "hostname router2"
        
        hash1 = calculate_content_hash(content1)
        hash2 = calculate_content_hash(content2)
        
        assert len(hash1) == 64  # SHA256
        assert hash1 != hash2
    
    def test_content_hash_consistency(self):
        """Test hash is consistent"""
        from app.api.config_versions import calculate_content_hash
        
        content = "test content"
        hash1 = calculate_content_hash(content)
        hash2 = calculate_content_hash(content)
        
        assert hash1 == hash2


@pytest.mark.asyncio
class TestAsyncOperations:
    """Test async webhook delivery"""
    
    async def test_webhook_delivery_engine(self):
        """Test webhook delivery engine can be created"""
        from app.webhooks.delivery import WebhookDeliveryEngine
        
        db = next(override_get_db())
        engine = WebhookDeliveryEngine(db)
        
        assert engine.max_retries == 3
        assert engine.timeout == 30
    
    async def test_retry_calculation(self):
        """Test retry backoff calculation"""
        from app.webhooks.delivery import WebhookDeliveryEngine
        
        db = next(override_get_db())
        engine = WebhookDeliveryEngine(db)
        
        retry1 = engine._calculate_next_retry(0)
        retry2 = engine._calculate_next_retry(1)
        retry3 = engine._calculate_next_retry(2)
        
        assert retry1 < retry2 < retry3


def test_integration_full_flow():
    """Integration test: Create config version -> detect change -> trigger event"""
    # This would be a full end-to-end test
    # Skipping for now as it requires full auth setup
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
