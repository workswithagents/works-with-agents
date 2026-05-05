"""
Compliance-as-Code — L7 Governance
Turn regulation into executable validation rules for AI agents.

Usage:
    from workswithagents import ComplianceEngine
    
    ce = ComplianceEngine()
    
    # Load regulation pack
    dtac = ce.load("dtac-v2.1")
    
    # Validate an action before execution
    result = dtac.validate({
        "guarantee_level": "atp-3",
        "reversible": True,
        "compliance": {"audit_trail_id": "audit-123", "sign_off_required": True},
        "data_classification": "confidential"
    })
    
    if result.passed:
        execute(action)
    else:
        print(result.violations)  # ["DTAC-2.1.3: Missing clinical_safety_ref"]
"""

import json
import urllib.request
import urllib.error
from typing import Optional, List, Dict

DEFAULT_API = "https://workswithagents.dev"


class ComplianceResult:
    """Result of a compliance validation."""
    def __init__(self, passed: bool, violations: List[str], 
                 evidence_required: List[dict]):
        self.passed = passed
        self.violations = violations
        self.evidence_required = evidence_required
    
    def __repr__(self):
        return f"ComplianceResult(passed={self.passed}, violations={len(self.violations)})"


class RegulationPack:
    """A loaded regulation rule set for validation."""
    
    def __init__(self, name: str, rules: dict, api_url: str):
        self.name = name
        self.rules = rules
        self.api = api_url
    
    def validate(self, action: dict) -> ComplianceResult:
        """Validate an action against this regulation pack."""
        violations = []
        evidence_required = []
        
        for rule in self.rules.get("rules", []):
            # Check if rule triggers for this action
            if not self._triggered(rule, action):
                continue
            
            # Run validation checks
            for check in rule.get("validation", []):
                field_value = self._get_field(action, check["field"])
                operator = check["operator"]
                expected = check.get("value")
                
                passed = self._check(field_value, operator, expected)
                if not passed:
                    violations.append(f"{rule['id']}: {check['message']}")
            
            # Collect evidence requirements
            if rule.get("evidence"):
                evidence_required.extend(rule["evidence"])
        
        return ComplianceResult(
            passed=len(violations) == 0,
            violations=violations,
            evidence_required=evidence_required
        )
    
    def _triggered(self, rule: dict, action: dict) -> bool:
        """Check if this rule's trigger conditions match the action."""
        trigger = rule.get("trigger", {})
        if not trigger:
            return True  # No trigger = always check
        
        # Check events
        events = trigger.get("events", [])
        if events and action.get("verb") not in events:
            if action.get("verb") not in events:
                # Also check if any trigger event matches
                return False
        
        # Check data classification
        classifications = trigger.get("data_classification", [])
        if classifications:
            action_class = action.get("data_classification", "internal")
            if action_class not in classifications:
                return False
        
        return True
    
    def _get_field(self, obj: dict, field: str) -> any:
        """Get nested field value using dot notation: 'compliance.audit_trail_id'."""
        parts = field.split(".")
        current = obj
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current
    
    def _check(self, actual: any, operator: str, expected: any) -> bool:
        """Evaluate a validation check."""
        if operator == "equals":
            return actual == expected
        elif operator == "exists":
            return actual is not None and actual != ""
        elif operator == "in":
            return actual in (expected if isinstance(expected, list) else [expected])
        elif operator == "not_in":
            return actual not in (expected if isinstance(expected, list) else [expected])
        elif operator == "greater_than":
            return actual > expected if actual is not None else False
        elif operator == "less_than":
            return actual < expected if actual is not None else False
        return False


class ComplianceEngine:
    """Load regulation packs and validate actions."""
    
    def __init__(self, api_url: str = DEFAULT_API):
        self.api = api_url.rstrip("/")
        self._cache: Dict[str, RegulationPack] = {}
    
    def load(self, regulation: str) -> RegulationPack:
        """Load a regulation pack by name (e.g., 'dtac-v2.1', 'gdpr')."""
        if regulation in self._cache:
            return self._cache[regulation]
        
        rules = self._request("GET", f"/v1/compliance/packs/{regulation}")
        pack = RegulationPack(regulation, rules, self.api)
        self._cache[regulation] = pack
        return pack
    
    def list_packs(self) -> list:
        """List all available regulation packs."""
        return self._request("GET", "/v1/compliance/packs")
    
    def validate(self, regulation: str, action: dict) -> ComplianceResult:
        """Load regulation and validate action in one call."""
        pack = self.load(regulation)
        return pack.validate(action)
    
    def applicable(self, fleet_id: str) -> list:
        """Get regulations applicable to a fleet."""
        return self._request("GET", f"/v1/compliance/applicable?fleet_id={fleet_id}")
    
    def evidence(self, regulation: str, fleet_id: str, 
                 period: str) -> dict:
        """Generate compliance evidence for an assessment period."""
        return self._request("POST", "/v1/compliance/evidence", {
            "regulation": regulation,
            "fleet_id": fleet_id,
            "period": period
        })
    
    def _request(self, method: str, path: str, data: Optional[dict] = None) -> dict:
        url = f"{self.api}{path}"
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, method=method)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return {"error": e.code, "message": e.read().decode()}


# Convenience function for inline validation
def safe_execute(action: dict, regulations: List[str], 
                 api_url: str = DEFAULT_API) -> bool:
    """
    Validate an action against multiple regulations before executing.
    Returns True if all pass, False if any violate.
    
    Usage:
        if safe_execute(my_action, ["dtac-v2.1", "gdpr"]):
            execute(my_action)
        else:
            escalate_to_human()
    """
    engine = ComplianceEngine(api_url)
    for reg in regulations:
        result = engine.validate(reg, action)
        if not result.passed:
            return False
    return True
