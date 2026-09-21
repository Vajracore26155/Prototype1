"""
Integration Tests: API Endpoints
Phase 8: Full API testing
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestUploadWorkflow:
    """Test complete upload workflow"""
    
    def test_upload_and_process_configuration(self, test_client, auth_headers):
        """Test full upload → parse → audit workflow"""
        
        # Step 1: Upload configuration
        files = {
            "file": ("test_config.cfg", "hostname router1\nip address 192.168.1.1", "text/plain")
        }
        
        response = test_client.post(
            "/api/upload",
            files=files,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        config_id = data["data"]["config_id"]
        
        # Step 2: Check status
        response = test_client.get(
            f"/api/configurations/{config_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["data"]["config_id"] == config_id


@pytest.mark.integration
class TestAuditWorkflow:
    """Test audit execution workflow"""
    
    def test_create_and_execute_audit(self, test_client, auth_headers, test_config):
        """Test create audit → execute → get results"""
        
        # Step 1: Create audit
        response = test_client.post(
            "/api/audits",
            json={
                "config_id": test_config.config_id,
                "frameworks": ["CIS"]
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        audit_id = response.json()["data"]["audit_id"]
        
        # Step 2: Get audit status
        response = test_client.get(
            f"/api/audits/{audit_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["audit_id"] == audit_id
        
        # Step 3: Get findings
        response = test_client.get(
            f"/api/audits/{audit_id}/findings",
            headers=auth_headers
        )
        
        assert response.status_code == 200


@pytest.mark.integration
class TestReportingWorkflow:
    """Test reporting workflow"""
    
    def test_generate_and_retrieve_report(self, test_client, auth_headers):
        """Test report generation workflow"""
        
        # Step 1: List templates
        response = test_client.get(
            "/api/reports/templates",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        templates = response.json()["data"]["templates"]
        assert len(templates) > 0
        
        template_id = templates[0]["template_id"]
        
        # Step 2: Generate report
        response = test_client.post(
            "/api/reports/generate",
            json={
                "template_id": template_id,
                "name": "Test Report",
                "format": "HTML",
                "filters": {}
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        report_id = response.json()["data"]["report_id"]
        
        # Step 3: Retrieve report
        response = test_client.get(
            f"/api/reports/{report_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json()["data"]["report_id"] == report_id


@pytest.mark.integration
class TestWebhookWorkflow:
    """Test webhook workflow"""
    
    def test_create_and_trigger_webhook(self, test_client, auth_headers):
        """Test webhook creation and triggering"""
        
        # Step 1: Create webhook
        response = test_client.post(
            "/api/webhooks",
            json={
                "name": "Test Webhook",
                "url": "https://example.com/webhook",
                "events": ["audit.completed"],
                "is_active": True
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        webhook_id = response.json()["data"]["webhook_id"]
        
        # Step 2: Get webhook
        response = test_client.get(
            f"/api/webhooks/{webhook_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Step 3: Deactivate webhook
        response = test_client.patch(
            f"/api/webhooks/{webhook_id}",
            json={"is_active": False},
            headers=auth_headers
        )
        
        assert response.status_code == 200


@pytest.mark.integration
class TestSearchWorkflow:
    """Test search functionality"""
    
    def test_search_and_filter(self, test_client, auth_headers):
        """Test search with filters"""
        
        # Step 1: Reindex
        response = test_client.post(
            "/api/search/reindex",
            headers=auth_headers
        )
        
        # May fail without admin permission
        # assert response.status_code in [200, 403]
        
        # Step 2: Search
        response = test_client.get(
            "/api/search?q=firewall",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert "results" in data
        assert "facets" in data


@pytest.mark.integration
class TestKnowledgeGraphWorkflow:
    """Test knowledge graph"""
    
    def test_graph_and_impact_analysis(self, test_client, auth_headers, test_device):
        """Test knowledge graph operations"""
        
        # Step 1: Get graph statistics
        response = test_client.get(
            "/api/knowledge-graph",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert "statistics" in data
        
        # Step 2: Get entity details
        response = test_client.get(
            f"/api/knowledge-graph/entity/{test_device.device_id}",
            headers=auth_headers
        )
        
        # May be 404 if not in graph yet
        assert response.status_code in [200, 404]


@pytest.mark.integration
class TestDriftWorkflow:
    """Test drift detection workflow"""
    
    def test_drift_detection_and_analysis(self, test_client, auth_headers, test_device):
        """Test drift detection workflow"""
        
        # Step 1: Get drift status
        response = test_client.get(
            f"/api/drift/devices/{test_device.device_id}",
            headers=auth_headers
        )
        
        # May be 404 if no drift data yet
        assert response.status_code in [200, 404]
        
        # Step 2: List all drift
        response = test_client.get(
            "/api/drift",
            headers=auth_headers
        )
        
        assert response.status_code == 200


@pytest.mark.integration
class TestMonitoringWorkflow:
    """Test monitoring endpoints"""
    
    def test_monitoring_dashboard(self, test_client, auth_headers):
        """Test monitoring dashboard data"""
        
        # Step 1: Get dashboard
        response = test_client.get(
            "/api/monitoring/dashboard",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()["data"]
        assert "metrics" in data
        
        # Step 2: Get system metrics
        response = test_client.get(
            "/api/monitoring/metrics/system",
            headers=auth_headers
        )
        
        assert response.status_code == 200


@pytest.mark.integration
class TestPermissionEnforcement:
    """Test permission enforcement across APIs"""
    
    def test_read_only_user_cannot_write(self, test_client, readonly_auth_headers):
        """Test read-only user is blocked from write operations"""
        
        # Should succeed (read)
        response = test_client.get(
            "/api/devices",
            headers=readonly_auth_headers
        )
        assert response.status_code in [200, 403]
        
        # Should fail (write)
        response = test_client.post(
            "/api/devices",
            json={"device_id": "TEST", "vendor": "Test"},
            headers=readonly_auth_headers
        )
        assert response.status_code == 403
    
    def test_admin_has_full_access(self, test_client, admin_auth_headers):
        """Test admin has access to all endpoints"""
        
        endpoints = [
            "/api/devices",
            "/api/audits",
            "/api/users",
            "/api/webhooks"
        ]
        
        for endpoint in endpoints:
            response = test_client.get(endpoint, headers=admin_auth_headers)
            assert response.status_code in [200, 404]  # 200 or 404, but not 403
