"""
Agent Onboarding Protocol — L1/L3
Productize the creation of new specialist AI agents.

Usage:
    from workswithagents import OnboardingClient
    
    ob = OnboardingClient()
    
    # Interview — define the new agent
    interview = ob.interview(
        name="hermes-nhs-auditor",
        purpose="Audit agent actions for NHS DTAC compliance",
        capabilities=["audit:compliance", "generate:evidence"],
        skills=["compliance-as-code"]
    )
    
    # Generate agent files
    ob.generate(interview["interview_id"])
    
    # Run calibration
    cal = ob.calibrate(interview["interview_id"])
    
    # If passes, register in fleet
    if cal["passed"]:
        reg = ob.register(interview["interview_id"])
        print(f"New agent: {reg['agent_id']}")
"""

import json
import urllib.request
import urllib.error
from typing import Optional, List

DEFAULT_API = "https://workswithagents.dev"


class OnboardingClient:
    """Create and calibrate new specialist AI agents."""
    
    def __init__(self, api_url: str = DEFAULT_API):
        self.api = api_url.rstrip("/")
    
    def interview(self, name: str, purpose: str, *,
                  capabilities: List[str],
                  skills: Optional[List[str]] = None,
                  tools: Optional[List[str]] = None,
                  fleet: Optional[str] = None,
                  constraints: Optional[List[str]] = None,
                  benchmarks: Optional[List[dict]] = None) -> dict:
        """Start onboarding interview — define the new agent."""
        payload = {
            "agent_name": name,
            "purpose": purpose,
            "capabilities": capabilities,
        }
        if skills:
            payload["skills"] = skills
        if tools:
            payload["tools"] = tools
        if fleet:
            payload["fleet"] = fleet
        if constraints:
            payload["constraints"] = constraints
        if benchmarks:
            payload["benchmarks"] = benchmarks
        
        return self._request("POST", "/v1/onboard/interview", payload)
    
    def generate(self, interview_id: str) -> dict:
        """Generate agent files from interview: prompt, manifest, calibration tasks."""
        return self._request("POST", f"/v1/onboard/{interview_id}/generate")
    
    def calibrate(self, interview_id: str) -> dict:
        """Run calibration tasks. Returns per-task results."""
        return self._request("POST", f"/v1/onboard/{interview_id}/calibrate")
    
    def benchmark(self, interview_id: str) -> dict:
        """Run full benchmark suite. Returns {passed, metrics}."""
        return self._request("POST", f"/v1/onboard/{interview_id}/benchmark")
    
    def register(self, interview_id: str) -> dict:
        """Register the calibrated agent in the capability registry."""
        return self._request("POST", f"/v1/onboard/{interview_id}/register")
    
    def full_onboard(self, name: str, purpose: str, *,
                     capabilities: List[str],
                     **kwargs) -> dict:
        """
        Full onboarding pipeline: interview → generate → calibrate → register.
        Returns the new agent_id if all steps pass.
        """
        # 1. Interview
        result = self.interview(name, purpose, capabilities=capabilities, **kwargs)
        iid = result.get("interview_id")
        if not iid:
            return {"error": "Interview failed", "details": result}
        
        # 2. Generate
        gen = self.generate(iid)
        if gen.get("error"):
            return {"error": "Generation failed", "details": gen}
        
        # 3. Calibrate
        cal = self.calibrate(iid)
        if not cal.get("passed"):
            return {
                "error": "Calibration failed", 
                "results": cal,
                "next": "Review calibration failures and retry"
            }
        
        # 4. Register
        reg = self.register(iid)
        return reg
    
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
