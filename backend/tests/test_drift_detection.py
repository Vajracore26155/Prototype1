"""
Unit Tests: Drift Detection System
Phase 8: Configuration drift testing
"""
import pytest
from datetime import datetime, timedelta

from app.drift.detector import DriftDetector
from app.drift.differ import ConfigDiffer


class TestConfigDiffer:
    """Test configuration diffing"""
    
    @pytest.fixture
    def differ(self):
        """Create differ instance"""
        return ConfigDiffer()
    
    def test_no_changes(self, differ):
        """Test identical configurations"""
        config1 = "hostname router1\nip address 192.168.1.1"
        config2 = "hostname router1\nip address 192.168.1.1"
        
        diff = differ.compute_diff(config1, config2)
        
        assert diff["total_changes"] == 0
        assert len(diff["additions"]) == 0
        assert len(diff["deletions"]) == 0
    
    def test_additions(self, differ):
        """Test detecting additions"""
        config1 = "hostname router1"
        config2 = "hostname router1\nip address 192.168.1.1"
        
        diff = differ.compute_diff(config1, config2)
        
        assert diff["total_changes"] > 0
        assert len(diff["additions"]) == 1
        assert "ip address" in diff["additions"][0]
    
    def test_deletions(self, differ):
        """Test detecting deletions"""
        config1 = "hostname router1\nip address 192.168.1.1"
        config2 = "hostname router1"
        
        diff = differ.compute_diff(config1, config2)
        
        assert diff["total_changes"] > 0
        assert len(diff["deletions"]) == 1
        assert "ip address" in diff["deletions"][0]
    
    def test_modifications(self, differ):
        """Test detecting modifications"""
        config1 = "hostname router1\nip address 192.168.1.1"
        config2 = "hostname router2\nip address 192.168.1.1"
        
        diff = differ.compute_diff(config1, config2)
        
        assert diff["total_changes"] > 0
        assert len(diff["modifications"]) > 0


class TestDriftDetector:
    """Test drift detection logic"""
    
    @pytest.fixture
    def detector(self):
        """Create detector instance"""
        return DriftDetector()
    
    def test_calculate_drift_score_no_drift(self, detector):
        """Test drift score with no changes"""
        diff = {
            "total_changes": 0,
            "additions": [],
            "deletions": [],
            "modifications": []
        }
        
        score = detector.calculate_drift_score(diff)
        
        assert score == 0.0
    
    def test_calculate_drift_score_minor_drift(self, detector):
        """Test drift score with minor changes"""
        diff = {
            "total_changes": 2,
            "additions": ["line1"],
            "deletions": ["line2"],
            "modifications": []
        }
        
        score = detector.calculate_drift_score(diff)
        
        assert 0 < score < 50
    
    def test_calculate_drift_score_major_drift(self, detector):
        """Test drift score with major changes"""
        diff = {
            "total_changes": 50,
            "additions": ["line" + str(i) for i in range(20)],
            "deletions": ["line" + str(i) for i in range(20)],
            "modifications": ["line" + str(i) for i in range(10)]
        }
        
        score = detector.calculate_drift_score(diff)
        
        assert score >= 50
    
    def test_detect_critical_drift(self, detector):
        """Test detection of critical changes"""
        diff = {
            "deletions": [
                "no ip access-list standard 100",
                "no firewall enable"
            ],
            "additions": []
        }
        
        is_critical = detector.is_critical_drift(diff)
        
        assert is_critical is True
    
    def test_detect_non_critical_drift(self, detector):
        """Test detection of non-critical changes"""
        diff = {
            "modifications": [
                "hostname router1 -> hostname router2"
            ]
        }
        
        is_critical = detector.is_critical_drift(diff)
        
        assert is_critical is False


@pytest.mark.asyncio
class TestDriftAnalysis:
    """Test drift analysis workflow"""
    
    async def test_analyze_device_drift(self, test_db, test_device):
        """Test drift analysis for device"""
        from app.drift.detector import DriftDetector
        from app.database import ConfigurationVersion
        
        detector = DriftDetector()
        
        # Create baseline version
        baseline = ConfigurationVersion(
            version_id="VER-001",
            device_id=test_device.device_id,
            organization_id=1,
            version_number=1,
            configuration_text="hostname router1\nip address 192.168.1.1",
            change_summary="Initial configuration",
            is_baseline=True,
            created_by="system"
        )
        test_db.add(baseline)
        
        # Create current version
        current = ConfigurationVersion(
            version_id="VER-002",
            device_id=test_device.device_id,
            organization_id=1,
            version_number=2,
            configuration_text="hostname router2\nip address 192.168.1.2",
            change_summary="Updated configuration",
            is_baseline=False,
            created_by="admin"
        )
        test_db.add(current)
        test_db.commit()
        
        # Analyze drift
        result = detector.analyze_drift(baseline, current)
        
        assert result is not None
        assert "drift_score" in result
        assert "changes" in result
        assert result["drift_score"] > 0
    
    async def test_drift_detection_threshold(self, test_db, test_device):
        """Test drift detection threshold"""
        from app.drift.detector import DriftDetector
        
        detector = DriftDetector(threshold=30.0)
        
        # Test below threshold
        minor_diff = {
            "total_changes": 2,
            "additions": ["line1"],
            "deletions": []
        }
        assert detector.exceeds_threshold(minor_diff) is False
        
        # Test above threshold
        major_diff = {
            "total_changes": 50,
            "additions": ["line" + str(i) for i in range(30)],
            "deletions": ["line" + str(i) for i in range(20)]
        }
        assert detector.exceeds_threshold(major_diff) is True


class TestDriftNotifications:
    """Test drift notification system"""
    
    def test_generate_drift_alert(self):
        """Test drift alert generation"""
        from app.drift.detector import DriftDetector
        
        detector = DriftDetector()
        
        drift_data = {
            "device_id": "DEV-001",
            "drift_score": 75.0,
            "changes": {
                "deletions": ["no firewall enable"],
                "additions": []
            }
        }
        
        alert = detector.generate_alert(drift_data)
        
        assert alert is not None
        assert "severity" in alert
        assert alert["severity"] == "HIGH"
    
    def test_drift_alert_severity_levels(self):
        """Test different alert severity levels"""
        from app.drift.detector import DriftDetector
        
        detector = DriftDetector()
        
        # Low severity
        low_drift = {"drift_score": 15.0, "changes": {"total_changes": 1}}
        alert_low = detector.generate_alert(low_drift)
        assert alert_low["severity"] == "LOW"
        
        # High severity
        high_drift = {"drift_score": 80.0, "changes": {"total_changes": 100}}
        alert_high = detector.generate_alert(high_drift)
        assert alert_high["severity"] == "HIGH"
