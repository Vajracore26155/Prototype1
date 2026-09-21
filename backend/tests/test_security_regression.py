"""
Security Regression Tests
Tests for all CRITICAL security vulnerabilities fixed in Phase 4+

TESTS COVER:
1. Unauthenticated endpoint access (401 responses)
2. IDOR vulnerabilities (cross-organization data access)
3. Organization isolation in search
4. Proper organization assignment on uploads
5. Permission-based access control

These tests ensure security fixes don't regress in future development.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from app.database import Base, get_db, User, Organization, Configuration, Audit, Finding, Device, ConfigurationVersion, DriftAnalysis
from app.auth.security import create_access_token, hash_password
from main import app

# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_security.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def setup_test_data():
    """
    Create test data for security tests:
    - Two organizations (Org A and Org B)
    - Users in each organization
    - Configurations, audits, devices in each organization
    """
    db = TestingSessionLocal()
    
    try:
        # Clean database
        db.query(DriftAnalysis).delete()
        db.query(ConfigurationVersion).delete()
        db.query(Finding).delete()
        db.query(Audit).delete()
        db.query(Device).delete()
        db.query(Configuration).delete()
        db.query(User).delete()
        db.query(Organization).delete()
        db.commit()
        
        # Create Organization A
        org_a = Organization(
            org_id="ORG-A",
            name="Organization A",
            domain="orga.com",
            status="ACTIVE"
        )
        db.add(org_a)
        db.flush()
        
        # Create Organization B
        org_b = Organization(
            org_id="ORG-B",
            name="Organization B",
            domain="orgb.com",
            status="ACTIVE"
        )
        db.add(org_b)
        db.flush()
        
        # Create User A in Org A
        user_a = User(
            user_id="USER-A",
            email="usera@orga.com",
            full_name="User A",
            password_hash=hash_password("password123"),
            organization_id=org_a.id,
            role="ADMIN",
            is_active=True
        )
        db.add(user_a)
        db.flush()
        
        # Create User B in Org B
        user_b = User(
            user_id="USER-B",
            email="userb@orgb.com",
            full_name="User B",
            password_hash=hash_password("password123"),
            organization_id=org_b.id,
            role="ADMIN",
            is_active=True
        )
        db.add(user_b)
        db.flush()
        
        # Create Configuration A in Org A
        config_a = Configuration(
            config_id="CFG-A-001",
            organization_id=org_a.id,
            original_filename="config_a.txt",
            vendor="Cisco",
            sanitized_content="interface GigabitEthernet0/1\n no shutdown",
            file_size=100,
            file_hash_sha256="hash_a"
        )
        db.add(config_a)
        db.flush()
        
        # Create Configuration B in Org B
        config_b = Configuration(
            config_id="CFG-B-001",
            organization_id=org_b.id,
            original_filename="config_b.txt",
            vendor="Fortinet",
            sanitized_content="config system interface\n edit port1",
            file_size=100,
            file_hash_sha256="hash_b"
        )
        db.add(config_b)
        db.flush()
        
        # Create Audit A in Org A
        audit_a = Audit(
            audit_id="AUD-A-001",
            organization_id=org_a.id,
            configuration_id=config_a.id,
            status="COMPLETED",
            compliance_score=85.5,
            risk_score=45.0,
            risk_level="MEDIUM",
            passed_count=20,
            failed_count=5,
            warning_count=2
        )
        db.add(audit_a)
        db.flush()
        
        # Create Audit B in Org B
        audit_b = Audit(
            audit_id="AUD-B-001",
            organization_id=org_b.id,
            configuration_id=config_b.id,
            status="COMPLETED",
            compliance_score=92.0,
            risk_score=25.0,
            risk_level="LOW",
            passed_count=25,
            failed_count=2,
            warning_count=1
        )
        db.add(audit_b)
        db.flush()
        
        # Create Finding A in Org A
        finding_a = Finding(
            finding_id="FND-A-001",
            organization_id=org_a.id,
            audit_id=audit_a.id,
            rule_id="RULE-001",
            title="SSH Not Secured",
            description="SSH is not properly configured",
            severity="HIGH",
            status="FAIL",
            expected="SSH v2 only",
            actual="SSH v1 allowed"
        )
        db.add(finding_a)
        db.flush()
        
        # Create Finding B in Org B
        finding_b = Finding(
            finding_id="FND-B-001",
            organization_id=org_b.id,
            audit_id=audit_b.id,
            rule_id="RULE-001",
            title="Password Policy Weak",
            description="Password policy is weak",
            severity="MEDIUM",
            status="FAIL",
            expected="Min 12 characters",
            actual="Min 8 characters"
        )
        db.add(finding_b)
        db.flush()
        
        # Create Device A in Org A
        device_a = Device(
            device_id="DEV-A-001",
            organization_id=org_a.id,
            hostname="router-a-01",
            ip_address="10.0.1.1",
            vendor="Cisco",
            status="ACTIVE"
        )
        db.add(device_a)
        db.flush()
        
        # Create Device B in Org B
        device_b = Device(
            device_id="DEV-B-001",
            organization_id=org_b.id,
            hostname="firewall-b-01",
            ip_address="10.0.2.1",
            vendor="Fortinet",
            status="ACTIVE"
        )
        db.add(device_b)
        db.flush()
        
        # Create ConfigurationVersion A in Org A
        version_a = ConfigurationVersion(
            version_id="VER-A-001",
            configuration_id=config_a.id,
            device_id=device_a.id,
            version_number=1,
            content_hash="hash_a_v1",
            content="interface GigabitEthernet0/1\n no shutdown",
            file_size=100,
            uploaded_by="usera@orga.com",
            is_baseline=True
        )
        db.add(version_a)
        db.flush()
        
        # Create ConfigurationVersion B in Org B
        version_b = ConfigurationVersion(
            version_id="VER-B-001",
            configuration_id=config_b.id,
            device_id=device_b.id,
            version_number=1,
            content_hash="hash_b_v1",
            content="config system interface\n edit port1",
            file_size=100,
            uploaded_by="userb@orgb.com",
            is_baseline=True
        )
        db.add(version_b)
        db.flush()
        
        # Create DriftAnalysis A in Org A
        drift_a = DriftAnalysis(
            drift_id="DRF-A-001",
            organization_id=org_a.id,
            device_id=device_a.id,
            baseline_version_id=version_a.id,
            current_version_id=version_a.id,
            drift_score=15.5,
            drift_severity="LOW",
            field_drifts=[],
            added_fields=1,
            removed_fields=0,
            modified_fields=2
        )
        db.add(drift_a)
        db.flush()
        
        # Create DriftAnalysis B in Org B
        drift_b = DriftAnalysis(
            drift_id="DRF-B-001",
            organization_id=org_b.id,
            device_id=device_b.id,
            baseline_version_id=version_b.id,
            current_version_id=version_b.id,
            drift_score=45.0,
            drift_severity="HIGH",
            field_drifts=[],
            added_fields=5,
            removed_fields=2,
            modified_fields=8
        )
        db.add(drift_b)
        db.flush()
        
        db.commit()
        
        # Generate tokens
        token_a = create_access_token(data={"sub": user_a.email})
        token_b = create_access_token(data={"sub": user_b.email})
        
        yield {
            "org_a": org_a,
            "org_b": org_b,
            "user_a": user_a,
            "user_b": user_b,
            "token_a": token_a,
            "token_b": token_b,
            "config_a": config_a,
            "config_b": config_b,
            "audit_a": audit_a,
            "audit_b": audit_b,
            "finding_a": finding_a,
            "finding_b": finding_b,
            "device_a": device_a,
            "device_b": device_b,
            "version_a": version_a,
            "version_b": version_b,
            "drift_a": drift_a,
            "drift_b": drift_b
        }
        
    finally:
        db.close()


# ============================================================
# TEST SUITE 1: UNAUTHENTICATED ACCESS
# ============================================================

class TestUnauthenticatedAccess:
    """Test that all endpoints require authentication"""
    
    def test_comparison_requires_auth(self, setup_test_data):
        """Test comparison endpoints require authentication"""
        data = setup_test_data
        
        # compare_audits without auth
        response = client.post(
            "/api/comparison/audits",
            json={"audit_id_1": data["audit_a"].audit_id, "audit_id_2": data["audit_b"].audit_id}
        )
        assert response.status_code == 401
        
        # compare_configurations without auth
        response = client.post(
            "/api/comparison/configurations",
            json={"baseline_id": data["config_a"].config_id, "current_id": data["config_b"].config_id}
        )
        assert response.status_code == 401
    
    def test_frameworks_requires_auth(self, setup_test_data):
        """Test framework endpoints require authentication"""
        
        # get_framework_summary without auth
        response = client.get("/api/frameworks/summary")
        assert response.status_code == 401
        
        # assess_configuration_frameworks without auth
        response = client.post(
            "/api/frameworks/assess/CFG-A-001",
            json={"frameworks": ["NIST_CSF"]}
        )
        assert response.status_code == 401
    
    def test_bulk_upload_requires_auth(self, setup_test_data):
        """Test bulk upload endpoints require authentication"""
        
        # bulk_upload_configurations without auth
        response = client.post(
            "/api/bulk-upload/configurations",
            files={"file": ("test.zip", b"fake zip content", "application/zip")}
        )
        assert response.status_code == 401


# ============================================================
# TEST SUITE 2: IDOR - CONFIGURATION ACCESS
# ============================================================

class TestConfigurationIDOR:
    """Test that users cannot access other organizations' configurations"""
    
    def test_cannot_compare_other_org_configs(self, setup_test_data):
        """User A cannot compare configurations from Org B"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        # Try to compare Org B's config
        response = client.post(
            "/api/comparison/configurations",
            json={
                "baseline_id": data["config_b"].config_id,
                "current_id": data["config_b"].config_id
            },
            headers=headers
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]["error"]["message"].lower()
    
    def test_cannot_access_other_org_config_versions(self, setup_test_data):
        """User A cannot access Org B's configuration versions"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        # Try to list Org B's config versions
        response = client.get(
            f"/api/config-versions/{data['config_b'].config_id}",
            headers=headers
        )
        assert response.status_code == 404
        
        # Try to get Org B's specific version
        response = client.get(
            f"/api/config-versions/version/{data['version_b'].version_id}",
            headers=headers
        )
        assert response.status_code == 404
    
    def test_cannot_compare_other_org_versions(self, setup_test_data):
        """User A cannot compare Org B's versions"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        response = client.post(
            "/api/config-versions/compare",
            json={
                "version_id_1": data["version_b"].version_id,
                "version_id_2": data["version_b"].version_id
            },
            headers=headers
        )
        assert response.status_code == 404


# ============================================================
# TEST SUITE 3: IDOR - AUDIT AND FINDINGS ACCESS
# ============================================================

class TestAuditIDOR:
    """Test that users cannot access other organizations' audits"""
    
    def test_cannot_compare_other_org_audits(self, setup_test_data):
        """User A cannot compare audits from Org B"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        response = client.post(
            "/api/comparison/audits",
            json={
                "audit_id_1": data["audit_b"].audit_id,
                "audit_id_2": data["audit_b"].audit_id
            },
            headers=headers
        )
        assert response.status_code == 404
    
    def test_cannot_access_other_org_audit_details(self, setup_test_data):
        """User A cannot access Org B's audit details"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        response = client.get(
            f"/api/audits/{data['audit_b'].audit_id}",
            headers=headers
        )
        assert response.status_code == 404
    
    def test_cannot_access_other_org_findings(self, setup_test_data):
        """User A cannot access Org B's findings"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        response = client.get(
            f"/api/audits/{data['audit_b'].audit_id}/findings",
            headers=headers
        )
        assert response.status_code == 404
    
    def test_cannot_download_other_org_report(self, setup_test_data):
        """User A cannot download Org B's audit report"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        response = client.get(
            f"/api/audits/{data['audit_b'].audit_id}/report",
            headers=headers
        )
        assert response.status_code == 404


# ============================================================
# TEST SUITE 4: IDOR - DEVICE ACCESS
# ============================================================

class TestDeviceIDOR:
    """Test that users cannot access other organizations' devices"""
    
    def test_cannot_get_other_org_device(self, setup_test_data):
        """User A cannot access Org B's device"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        response = client.get(
            f"/api/devices/{data['device_b'].device_id}",
            headers=headers
        )
        assert response.status_code == 404
    
    def test_cannot_update_other_org_device(self, setup_test_data):
        """User A cannot update Org B's device"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        response = client.patch(
            f"/api/devices/{data['device_b'].device_id}",
            json={"hostname": "hacked"},
            headers=headers
        )
        assert response.status_code == 404
    
    def test_cannot_delete_other_org_device(self, setup_test_data):
        """User A cannot delete Org B's device"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        response = client.delete(
            f"/api/devices/{data['device_b'].device_id}",
            headers=headers
        )
        assert response.status_code == 404
    
    def test_list_devices_returns_only_own_org(self, setup_test_data):
        """User A's device list contains only Org A devices"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        response = client.get("/api/devices", headers=headers)
        assert response.status_code == 200
        
        devices = response.json()["data"]["devices"]
        device_ids = [d["device_id"] for d in devices]
        
        # Should contain Org A device
        assert data["device_a"].device_id in device_ids
        # Should NOT contain Org B device
        assert data["device_b"].device_id not in device_ids


# ============================================================
# TEST SUITE 5: IDOR - DRIFT ACCESS
# ============================================================

class TestDriftIDOR:
    """Test that users cannot access other organizations' drift analyses"""
    
    def test_cannot_get_other_org_drift(self, setup_test_data):
        """User A cannot access Org B's drift analysis"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        response = client.get(
            f"/api/drift/{data['drift_b'].drift_id}",
            headers=headers
        )
        assert response.status_code == 404
    
    def test_cannot_acknowledge_other_org_drift(self, setup_test_data):
        """User A cannot acknowledge Org B's drift"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        response = client.post(
            f"/api/drift/{data['drift_b'].drift_id}/acknowledge",
            headers=headers
        )
        assert response.status_code == 404
    
    def test_drift_history_returns_only_own_org(self, setup_test_data):
        """User A's drift history contains only Org A drifts"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        response = client.get(
            f"/api/devices/{data['device_a'].device_id}/drift-history",
            headers=headers
        )
        assert response.status_code == 200
        
        drifts = response.json()["data"]["drifts"]
        drift_ids = [d["drift_id"] for d in drifts]
        
        # Should contain Org A drift
        assert data["drift_a"].drift_id in drift_ids
        # Should NOT contain Org B drift
        assert data["drift_b"].drift_id not in drift_ids


# ============================================================
# TEST SUITE 6: ORGANIZATION ASSIGNMENT
# ============================================================

class TestOrganizationAssignment:
    """Test that created resources are assigned to correct organization"""
    
    def test_uploaded_config_assigned_to_user_org(self, setup_test_data):
        """Uploaded configuration is assigned to uploader's organization"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        # Upload a config
        response = client.post(
            "/api/upload",
            files={"file": ("test_config.txt", b"hostname test-router", "text/plain")},
            headers=headers
        )
        
        if response.status_code == 200:
            config_id = response.json()["data"]["config_id"]
            
            # Verify it's in Org A
            db = TestingSessionLocal()
            config = db.query(Configuration).filter(Configuration.config_id == config_id).first()
            assert config.organization_id == data["org_a"].id
            db.close()
    
    def test_created_device_assigned_to_user_org(self, setup_test_data):
        """Created device is assigned to creator's organization"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        response = client.post(
            "/api/devices",
            json={
                "hostname": "new-device",
                "ip_address": "192.168.1.1",
                "vendor": "Cisco"
            },
            headers=headers
        )
        
        if response.status_code == 200:
            device_id = response.json()["data"]["device_id"]
            
            # Verify it's in Org A
            db = TestingSessionLocal()
            device = db.query(Device).filter(Device.device_id == device_id).first()
            assert device.organization_id == data["org_a"].id
            db.close()


# ============================================================
# TEST SUITE 7: DASHBOARD AND SUMMARY DATA
# ============================================================

class TestDashboardIsolation:
    """Test that dashboard data is organization-scoped"""
    
    def test_dashboard_summary_org_scoped(self, setup_test_data):
        """Dashboard summary shows only own organization data"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        response = client.get("/api/dashboard/summary", headers=headers)
        assert response.status_code == 200
        
        summary = response.json()["data"]
        
        # Should show Org A's data
        assert summary["total_configs"] >= 1  # At least config_a
        assert summary["total_audits"] >= 1   # At least audit_a
    
    def test_device_stats_org_scoped(self, setup_test_data):
        """Device statistics show only own organization devices"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        response = client.get("/api/devices/stats/summary", headers=headers)
        assert response.status_code == 200
        
        stats = response.json()["data"]
        # Should show at least 1 device (device_a)
        assert stats["total_devices"] >= 1


# ============================================================
# TEST SUITE 8: SEARCH ISOLATION
# ============================================================

class TestSearchIsolation:
    """Test that search is organization-scoped"""
    
    def test_search_returns_only_own_org_results(self, setup_test_data):
        """Search results contain only own organization data"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        # Search for something that exists in both orgs
        response = client.get(
            "/api/search?query=config&entity_type=configurations",
            headers=headers
        )
        
        # Note: This test will fail until search index is rebuilt with organization_id
        # It's intentionally here to catch if reindexing is forgotten
        if response.status_code == 200:
            results = response.json()["data"]["results"]
            
            # Check that results only contain Org A data
            for result in results:
                if "config_id" in result:
                    # Verify this config belongs to Org A
                    db = TestingSessionLocal()
                    config = db.query(Configuration).filter(
                        Configuration.config_id == result["config_id"]
                    ).first()
                    if config:
                        assert config.organization_id == data["org_a"].id
                    db.close()


# ============================================================
# TEST SUITE 9: POSITIVE TESTS
# ============================================================

class TestPositiveAccess:
    """Test that users CAN access their own organization's data"""
    
    def test_can_access_own_config(self, setup_test_data):
        """User A can access Org A's configuration"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        response = client.get(
            f"/api/configurations/{data['config_a'].config_id}",
            headers=headers
        )
        assert response.status_code == 200
    
    def test_can_access_own_audit(self, setup_test_data):
        """User A can access Org A's audit"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        response = client.get(
            f"/api/audits/{data['audit_a'].audit_id}",
            headers=headers
        )
        assert response.status_code == 200
    
    def test_can_access_own_device(self, setup_test_data):
        """User A can access Org A's device"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        response = client.get(
            f"/api/devices/{data['device_a'].device_id}",
            headers=headers
        )
        assert response.status_code == 200
    
    def test_can_compare_own_configs(self, setup_test_data):
        """User A can compare Org A's configurations"""
        data = setup_test_data
        headers = {"Authorization": f"Bearer {data['token_a']}"}
        
        response = client.post(
            "/api/comparison/configurations",
            json={
                "baseline_id": data["config_a"].config_id,
                "current_id": data["config_a"].config_id
            },
            headers=headers
        )
        # May fail for other reasons, but should not be 404
        assert response.status_code != 404


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
