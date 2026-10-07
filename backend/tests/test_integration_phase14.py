import pytest
from app.models.policy import ReliabilityPolicy
from app.services.policy_service import PolicyEvaluationService

def test_integration_phase14(db):
    db.query(ReliabilityPolicy).delete()
    db.commit()
    # Setup Policy
    policy = ReliabilityPolicy(
        name="Production ML Changes",
        scope="GLOBAL",
        priority=100,
        rules=[
            {"type": "VALIDATION_REQUIRED", "value": "PASS", "severity": "BLOCK"},
            {"type": "REGRESSION_REQUIRED", "value": "PASS", "severity": "BLOCK"},
            {"type": "RISK_MAX", "value": "MODERATE", "severity": "BLOCK"},
            {"type": "HUMAN_APPROVAL_REQUIRED", "value": "PASS", "severity": "REVIEW_REQUIRED"}
        ]
    )
    db.add(policy)
    db.commit()

    svc = PolicyEvaluationService(db)

    # 1. Fully compliant production change -> ALLOW
    ctx1 = {
        "validation_status": "PASS",
        "regression_status": "PASS",
        "risk_level": "LOW",
        "human_approval": "PASS"
    }
    res1 = svc.evaluate_action("DEPLOYMENT", "deploy-1", context=ctx1)
    assert res1["result"] == "ALLOW"

    # 2. High-risk change -> BLOCK
    ctx2 = {
        "validation_status": "PASS",
        "regression_status": "PASS",
        "risk_level": "HIGH",
        "human_approval": "PASS"
    }
    res2 = svc.evaluate_action("DEPLOYMENT", "deploy-2", context=ctx2)
    assert res2["result"] == "BLOCK"

    # 3. Valid change missing approval -> REVIEW_REQUIRED
    ctx3 = {
        "validation_status": "PASS",
        "regression_status": "PASS",
        "risk_level": "MODERATE",
        "human_approval": "FAIL"
    }
    res3 = svc.evaluate_action("DEPLOYMENT", "deploy-3", context=ctx3)
    assert res3["result"] == "REVIEW_REQUIRED"

    # 4. Failed regression -> BLOCK
    ctx4 = {
        "validation_status": "PASS",
        "regression_status": "FAIL",
        "risk_level": "LOW",
        "human_approval": "PASS"
    }
    res4 = svc.evaluate_action("DEPLOYMENT", "deploy-4", context=ctx4)
    assert res4["result"] == "BLOCK"
