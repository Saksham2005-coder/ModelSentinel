import pytest
from app.services.policy_service import PolicyEvaluationService
from app.models.policy import ReliabilityPolicy

def test_policy_engine_validation_rule(db):
    db.query(ReliabilityPolicy).delete()
    db.commit()
    policy = ReliabilityPolicy(
        name="Validation Rule",
        scope="GLOBAL",
        priority=10,
        rules=[{"type": "VALIDATION_REQUIRED", "value": "PASS"}]
    )
    db.add(policy)
    db.commit()

    svc = PolicyEvaluationService(db)
    
    res = svc.evaluate_action("PATCH", "test-id", context={"validation_status": "PASS"})
    assert res["result"] == "ALLOW"
    
    res2 = svc.evaluate_action("PATCH", "test-id", context={"validation_status": "FAIL"})
    assert res2["result"] == "REVIEW_REQUIRED"

def test_policy_engine_risk_rule(db):
    db.query(ReliabilityPolicy).delete()
    db.commit()
    policy = ReliabilityPolicy(
        name="Risk Rule",
        scope="GLOBAL",
        priority=20,
        rules=[{"type": "RISK_MAX", "value": "MODERATE", "severity": "BLOCK"}]
    )
    db.add(policy)
    db.commit()

    svc = PolicyEvaluationService(db)
    
    res = svc.evaluate_action("PATCH", "test-id", context={"risk_level": "LOW"})
    assert res["result"] == "ALLOW"
    
    res2 = svc.evaluate_action("PATCH", "test-id", context={"risk_level": "HIGH"})
    assert res2["result"] == "BLOCK"

def test_policy_engine_precedence(db):
    db.query(ReliabilityPolicy).delete()
    db.commit()
    policy1 = ReliabilityPolicy(name="Global", scope="GLOBAL", priority=30, rules=[{"type": "CI_REQUIRED", "value": "PASS"}])
    policy2 = ReliabilityPolicy(name="Model", scope="MODEL", model_id="m1", priority=40, rules=[{"type": "CI_PASS_REQUIRED", "value": "PASS"}])
    db.add(policy1)
    db.add(policy2)
    db.commit()

    svc = PolicyEvaluationService(db)
    
    res = svc.evaluate_action("DEPLOYMENT", "test-id", model_id="m1", context={"ci_status": "FAIL"})
    assert res["matched_policy"] == "Model"
    assert res["result"] == "REVIEW_REQUIRED"
