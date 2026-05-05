"""
Agent SLA Framework — L7 Governance
Define and track Service Level Agreements for agent fleets.

Usage:
    from workswithagents import SLAMetrics
    
    sla = SLAMetrics("my-fleet", tier="production")
    
    # Report after each task
    sla.report("my-agent", "task-42", duration_seconds=187, success=True)
    
    # Check SLA status
    status = sla.status()  # {breaches: [], status: "ok"}
    
    # Generate monthly report
    report = sla.report_monthly("2026-05")
"""

import json
import time
import urllib.request
import urllib.error
from typing import Optional

DEFAULT_API = "https://workswithagents.dev"


class SLAMetrics:
    """Track and report SLA metrics for agent fleets."""
    
    TIERS = {
        "best_effort": {
            "uptime": 0.95,
            "accuracy": 0.80
        },
        "production": {
            "uptime": 0.995,
            "accuracy": 0.90,
            "latency_p95": 300,       # seconds
            "recovery": 0.95
        },
        "regulated": {
            "uptime": 0.999,
            "accuracy": 0.95,
            "latency_p99": 120,       # seconds
            "compliance": 1.0,        # all ATP-3 actions must pass
            "recovery": 0.99,
            "audit_retention_days": 2555  # 7 years
        }
    }
    
    def __init__(self, fleet_id: str, tier: str = "production", 
                 api_url: str = DEFAULT_API):
        self.fleet_id = fleet_id
        self.tier = tier
        self.api = api_url.rstrip("/")
        self.targets = self.TIERS.get(tier, self.TIERS["production"])
    
    def report(self, agent_id: str, action_id: str, *,
               duration_seconds: float, success: bool,
               guarantee_level: Optional[str] = None) -> dict:
        """Report a completed action for SLA tracking."""
        payload = {
            "fleet_id": self.fleet_id,
            "agent_id": agent_id,
            "action_id": action_id,
            "duration_seconds": duration_seconds,
            "success": success,
            "timestamp": int(time.time())
        }
        if guarantee_level:
            payload["guarantee_level"] = guarantee_level
        
        return self._request("POST", "/v1/sla/report", payload)
    
    def status(self) -> dict:
        """Get current SLA status — breaches and metrics."""
        return self._request("GET", f"/v1/sla/{self.fleet_id}/status")
    
    def report_monthly(self, period: str) -> dict:
        """Generate monthly SLA report (format: '2026-05')."""
        return self._request("GET", 
            f"/v1/sla/{self.fleet_id}/report?period={period}")
    
    def check_breach(self, metric: str, actual: float) -> Optional[str]:
        """Check if a metric breaches its target. Returns breach message or None."""
        target = self.targets.get(metric)
        if target is None:
            return None
        if actual < target:
            return f"{metric}: {actual:.3f} < target {target:.3f}"
        return None
    
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
