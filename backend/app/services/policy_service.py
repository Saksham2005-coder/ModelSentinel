from sqlalchemy.orm import Session
from app.models.policy import ReliabilityPolicy, PolicyEvaluation
import datetime
from typing import List, Dict, Any, Optional

class PolicyEvaluationService:
    def __init__(self, db: Session):
        self.db = db

    def evaluate_action(
        self,
        target_type: str,
        target_id: str,
        environment: Optional[str] = None,
        model_id: Optional[str] = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        
        if context is None:
            context = {}
            
        policies = self.get_applicable_policies(environment, model_id)
        
        if not policies:
            return {
                "result": "ALLOW",
                "matched_policy": None,
                "rule_results": [],
                "blocking_rules": [],
                "warnings": [],
                "evaluated_at": datetime.datetime.utcnow().isoformat()
            }
            
        # Select highest priority policy based on precedence
        # Environment > Model > Global
        matched_policy = policies[0]
        
        rule_results = []
        blocking_rules = []
        result = "ALLOW"
        
        for rule in matched_policy.rules:
            rule_eval = self._evaluate_rule(rule, context)
            rule_results.append(rule_eval)
            if not rule_eval["passed"]:
                blocking_rules.append(rule_eval)
                if result == "ALLOW":
                    result = "REVIEW_REQUIRED"
                if rule.get("severity", "REVIEW_REQUIRED") == "BLOCK":
                    result = "BLOCK"
                    
        evaluation = PolicyEvaluation(
            policy_id=matched_policy.id,
            target_type=target_type,
            target_id=target_id,
            result=result,
            rule_results=rule_results
        )
        self.db.add(evaluation)
        self.db.commit()
        self.db.refresh(evaluation)
        
        return {
            "result": result,
            "matched_policy": matched_policy.name,
            "rule_results": rule_results,
            "blocking_rules": blocking_rules,
            "warnings": [],
            "evaluated_at": evaluation.evaluated_at.isoformat()
        }

    def get_applicable_policies(self, environment: Optional[str], model_id: Optional[str]) -> List[ReliabilityPolicy]:
        query = self.db.query(ReliabilityPolicy).filter(ReliabilityPolicy.enabled == True)
        all_policies = query.all()
        
        env_policies = []
        model_policies = []
        global_policies = []
        
        for p in all_policies:
            if p.scope == "ENVIRONMENT" and environment and p.environment == environment:
                env_policies.append(p)
            elif p.scope == "MODEL" and model_id and p.model_id == model_id:
                model_policies.append(p)
            elif p.scope == "GLOBAL":
                global_policies.append(p)
                
        # Sort each list by priority descending
        env_policies.sort(key=lambda x: x.priority, reverse=True)
        model_policies.sort(key=lambda x: x.priority, reverse=True)
        global_policies.sort(key=lambda x: x.priority, reverse=True)
        
        # Precedence: Environment > Model > Global
        if env_policies:
            return env_policies
        if model_policies:
            return model_policies
        return global_policies

    def _evaluate_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        rule_type = rule.get("type")
        required_val = rule.get("value")
        operator = rule.get("operator", "=")
        
        actual_val = None
        passed = True
        
        if rule_type == "VALIDATION_REQUIRED":
            actual_val = context.get("validation_status")
            passed = (actual_val == "PASS" or actual_val == True)
        elif rule_type == "REGRESSION_REQUIRED":
            actual_val = context.get("regression_status")
            passed = (actual_val == "PASS" or actual_val == True)
        elif rule_type == "REGRESSION_PASS_RATE":
            actual_val = context.get("regression_pass_rate", 0)
            passed = self._compare_numeric(actual_val, operator, float(str(required_val).strip('%')))
        elif rule_type == "RISK_MAX":
            actual_val = context.get("risk_level", "LOW")
            passed = self._compare_risk(actual_val, required_val)
        elif rule_type == "CI_REQUIRED":
            actual_val = context.get("ci_status")
            passed = (actual_val != None)
        elif rule_type == "CI_PASS_REQUIRED":
            actual_val = context.get("ci_status")
            passed = (actual_val == "PASS")
        elif rule_type == "HUMAN_APPROVAL_REQUIRED":
            actual_val = context.get("human_approval")
            passed = (actual_val == "PASS" or actual_val == True)
        elif rule_type == "POST_DEPLOYMENT_VERIFICATION_REQUIRED":
            actual_val = context.get("post_deployment_verification")
            passed = (actual_val == "PASS" or actual_val == True)
        elif rule_type == "DEPLOYMENT_HEALTH_REQUIRED":
            actual_val = context.get("deployment_health")
            passed = (actual_val == "HEALTHY")
        else:
            passed = False
            actual_val = f"Unknown rule type: {rule_type}"
            
        return {
            "type": rule_type,
            "required": required_val,
            "operator": operator,
            "actual": actual_val,
            "passed": passed
        }
        
    def _compare_numeric(self, actual, operator, required):
        if actual is None:
            return False
        if operator == "=": return actual == required
        if operator == ">": return actual > required
        if operator == ">=": return actual >= required
        if operator == "<": return actual < required
        if operator == "<=": return actual <= required
        return False

    def _compare_risk(self, actual_risk, max_risk):
        levels = {"LOW": 1, "MODERATE": 2, "HIGH": 3, "CRITICAL": 4}
        return levels.get(actual_risk, 4) <= levels.get(max_risk, 1)

