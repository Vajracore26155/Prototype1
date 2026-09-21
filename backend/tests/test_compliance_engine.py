"""
Unit Tests: Compliance Evaluation Engine
Phase 8: Framework engine testing
"""
import pytest
from app.compliance.evaluator import ComplianceEvaluator
from app.compliance.framework_engine import FrameworkEngine


class TestComplianceEvaluator:
    """Test compliance evaluation logic"""
    
    @pytest.fixture
    def evaluator(self):
        """Create evaluator instance"""
        return ComplianceEvaluator()
    
    def test_evaluate_rule_pass(self, evaluator):
        """Test rule evaluation - pass case"""
        rule = {
            "rule_id": "CIS-1.1",
            "title": "Enable SSH version 2",
            "check": "ssh_version >= 2",
            "severity": "HIGH"
        }
        
        config = {
            "ssh_version": 2
        }
        
        result = evaluator.evaluate_rule(rule, config)
        
        assert result["status"] == "PASS"
        assert result["severity"] == "HIGH"
    
    def test_evaluate_rule_fail(self, evaluator):
        """Test rule evaluation - fail case"""
        rule = {
            "rule_id": "CIS-1.1",
            "title": "Enable SSH version 2",
            "check": "ssh_version >= 2",
            "severity": "HIGH"
        }
        
        config = {
            "ssh_version": 1
        }
        
        result = evaluator.evaluate_rule(rule, config)
        
        assert result["status"] == "FAIL"
    
    def test_calculate_compliance_score(self, evaluator):
        """Test compliance score calculation"""
        results = [
            {"status": "PASS", "severity": "HIGH"},
            {"status": "PASS", "severity": "MEDIUM"},
            {"status": "FAIL", "severity": "HIGH"},
            {"status": "FAIL", "severity": "LOW"}
        ]
        
        score = evaluator.calculate_compliance_score(results)
        
        assert 0 <= score <= 100
        assert score == 50  # 2 pass, 2 fail
    
    def test_weighted_compliance_score(self, evaluator):
        """Test weighted scoring by severity"""
        results = [
            {"status": "PASS", "severity": "CRITICAL", "weight": 4},
            {"status": "FAIL", "severity": "LOW", "weight": 1}
        ]
        
        score = evaluator.calculate_weighted_score(results)
        
        # Should be higher than 50% due to weighting
        assert score > 50


class TestFrameworkEngine:
    """Test compliance framework engine"""
    
    @pytest.fixture
    def engine(self):
        """Create framework engine instance"""
        return FrameworkEngine()
    
    def test_load_framework(self, engine):
        """Test loading compliance framework"""
        framework = engine.load_framework("CIS")
        
        assert framework is not None
        assert "rules" in framework
        assert len(framework["rules"]) > 0
    
    def test_get_applicable_rules(self, engine):
        """Test getting applicable rules for device"""
        device_info = {
            "vendor": "cisco",
            "device_type": "router"
        }
        
        rules = engine.get_applicable_rules("CIS", device_info)
        
        assert isinstance(rules, list)
        assert len(rules) > 0
    
    def test_evaluate_framework(self, engine):
        """Test complete framework evaluation"""
        config = {
            "hostname": "router1",
            "ssh_version": 2,
            "enable_secret": True
        }
        
        result = engine.evaluate_framework("CIS", config)
        
        assert "compliance_score" in result
        assert "findings" in result
        assert 0 <= result["compliance_score"] <= 100


class TestRuleEngine:
    """Test rule evaluation engine"""
    
    def test_simple_comparison(self):
        """Test simple comparison rules"""
        from app.compliance.evaluator import evaluate_expression
        
        assert evaluate_expression("ssh_version >= 2", {"ssh_version": 2}) is True
        assert evaluate_expression("ssh_version >= 2", {"ssh_version": 1}) is False
    
    def test_boolean_logic(self):
        """Test boolean logic in rules"""
        from app.compliance.evaluator import evaluate_expression
        
        context = {"ssh_enabled": True, "ssh_version": 2}
        
        assert evaluate_expression(
            "ssh_enabled == True and ssh_version >= 2",
            context
        ) is True
    
    def test_string_matching(self):
        """Test string matching in rules"""
        from app.compliance.evaluator import evaluate_expression
        
        context = {"hostname": "router-prod-01"}
        
        assert evaluate_expression(
            "'prod' in hostname",
            context
        ) is True


@pytest.mark.asyncio
class TestComplianceIntegration:
    """Test compliance system integration"""
    
    async def test_full_audit_evaluation(self, test_db, test_audit):
        """Test complete audit evaluation"""
        from app.compliance.evaluator import ComplianceEvaluator
        
        evaluator = ComplianceEvaluator()
        
        # Run evaluation
        results = evaluator.evaluate_audit(test_audit.audit_id, test_db)
        
        assert "compliance_score" in results
        assert "findings" in results
        assert "passed" in results
        assert "failed" in results
    
    async def test_multi_framework_evaluation(self, test_db, test_audit):
        """Test evaluation against multiple frameworks"""
        from app.compliance.framework_engine import FrameworkEngine
        
        engine = FrameworkEngine()
        frameworks = ["CIS", "PCI-DSS", "NIST"]
        
        results = {}
        for framework in frameworks:
            results[framework] = engine.evaluate_framework(
                framework,
                {"ssh_version": 2}
            )
        
        assert len(results) == len(frameworks)
        for framework, result in results.items():
            assert "compliance_score" in result
