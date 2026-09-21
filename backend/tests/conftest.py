"""
Pytest Configuration and Fixtures
Phase 8: Test infrastructure
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.database.models import (
    User, Organization, Device, Configuration,
    Audit, Finding
)
from app.auth.security import get_password_hash, create_access_token


# ============================================================
# Database Fixtures
# ============================================================

@pytest.fixture(scope="function")
def test_db():
    """
    Create test database for each test
    Uses in-memory SQLite for speed
    """
    # Create in-memory database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    yield db
    
    # Cleanup
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def test_client(test_db):
    """
    Create test client with test database
    """
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    
    yield client
    
    app.dependency_overrides.clear()


# ============================================================
# User & Auth Fixtures
# ============================================================

@pytest.fixture(scope="function")
def test_organization(test_db):
    """Create test organization"""
    org = Organization(
        name="Test Organization",
        contact_email="admin@test.com",
        subscription_tier="ENTERPRISE",
        is_active=True
    )
    test_db.add(org)
    test_db.commit()
    test_db.refresh(org)
    return org


@pytest.fixture(scope="function")
def test_user(test_db, test_organization):
    """Create test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("TestPassword123!"),
        full_name="Test User",
        organization_id=test_organization.id,
        role="AUDITOR",
        is_active=True,
        permissions=["audit:read", "device:read", "finding:read"]
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_user(test_db, test_organization):
    """Create admin user"""
    user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("AdminPassword123!"),
        full_name="Admin User",
        organization_id=test_organization.id,
        role="ADMIN",
        is_active=True,
        permissions=["admin"]
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def readonly_user(test_db, test_organization):
    """Create read-only user"""
    user = User(
        email="readonly@example.com",
        username="readonly",
        hashed_password=get_password_hash("ReadPassword123!"),
        full_name="Read Only User",
        organization_id=test_organization.id,
        role="VIEWER",
        is_active=True,
        permissions=["audit:read", "device:read"]
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(test_user):
    """Create authorization headers for test user"""
    token = create_access_token({"sub": test_user.email, "user_id": test_user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def admin_auth_headers(admin_user):
    """Create authorization headers for admin user"""
    token = create_access_token({"sub": admin_user.email, "user_id": admin_user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def readonly_auth_headers(readonly_user):
    """Create authorization headers for readonly user"""
    token = create_access_token({"sub": readonly_user.email, "user_id": readonly_user.id})
    return {"Authorization": f"Bearer {token}"}


# ============================================================
# Entity Fixtures
# ============================================================

@pytest.fixture(scope="function")
def test_device(test_db, test_organization):
    """Create test device"""
    device = Device(
        device_id="DEV-TEST-001",
        organization_id=test_organization.id,
        vendor="cisco",
        model="ISR4451",
        hostname="test-router-01",
        ip_address="192.168.1.1",
        location="Test Lab",
        status="ACTIVE"
    )
    test_db.add(device)
    test_db.commit()
    test_db.refresh(device)
    return device


@pytest.fixture(scope="function")
def test_config(test_db, test_organization):
    """Create test configuration"""
    config = Configuration(
        config_id="CFG-TEST-001",
        filename="test_config.cfg",
        original_filename="router1.cfg",
        file_type=".cfg",
        status="COMPLETED",
        vendor="cisco",
        vendor_confidence=0.95,
        storage_path="/tmp/test_config.cfg",
        organization_id=test_organization.id
    )
    test_db.add(config)
    test_db.commit()
    test_db.refresh(config)
    return config


@pytest.fixture(scope="function")
def test_audit(test_db, test_organization, test_config):
    """Create test audit"""
    audit = Audit(
        audit_id="AUD-TEST-001",
        configuration_id=test_config.id,
        organization_id=test_organization.id,
        status="COMPLETED",
        compliance_score=85.5,
        risk_score=25.0,
        risk_level="MEDIUM",
        passed_count=85,
        failed_count=15,
        warning_count=5
    )
    test_db.add(audit)
    test_db.commit()
    test_db.refresh(audit)
    return audit


@pytest.fixture(scope="function")
def test_finding(test_db, test_organization, test_audit, test_device):
    """Create test finding"""
    finding = Finding(
        finding_id="FND-TEST-001",
        audit_id=test_audit.id,
        organization_id=test_organization.id,
        device_id=test_device.device_id,
        title="SSH version 1 enabled",
        description="Device is using insecure SSH version 1",
        severity="HIGH",
        category="AUTHENTICATION",
        status="OPEN",
        line_number=42,
        config_snippet="ssh version 1",
        rule_id="CIS-1.1",
        framework="CIS"
    )
    test_db.add(finding)
    test_db.commit()
    test_db.refresh(finding)
    return finding


# ============================================================
# Helper Functions
# ============================================================

@pytest.fixture
def sample_cisco_config():
    """Sample Cisco configuration"""
    return """
hostname test-router
!
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
ip access-list standard 100
 permit ip any any
!
line vty 0 4
 transport input ssh
 login local
!
end
"""


@pytest.fixture
def sample_fortinet_config():
    """Sample Fortinet configuration"""
    return """
config system global
    set hostname "test-firewall"
    set admin-sport 8443
end

config firewall policy
    edit 1
        set name "Allow-Web"
        set srcintf "internal"
        set dstintf "wan1"
        set srcaddr "all"
        set dstaddr "all"
        set service "HTTP" "HTTPS"
        set action accept
    next
end
"""
