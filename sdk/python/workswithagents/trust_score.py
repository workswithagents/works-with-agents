"""
Agent Trust Score — L3/L5
Credit score for AI agents. Query, report, rate.

Usage:
    from workswithagents import TrustScoreClient
    ts = TrustScoreClient()
    
    # Report your metrics
    ts.report("my-agent", success_rate=0.94, pitfalls=3)
    
    # Check before delegating
    score = ts.get("target-agent")
    if score["tier"] == "trusted":
        delegate(task, to="target-agent")
"""

import json
import urllib.request
import urllib.error
from typing import Optional

DEFAULT_API = "https://workswithagents.dev"


class TrustScoreClient:
    """Query and report agent trust scores."""
    
    def __init__(self, api_url: str = DEFAULT_API):
        self.api = api_url.rstrip("/")
    
    def get(self, agent_id: str) -> dict:
        """Get an agent's trust score and tier."""
        return self._request("GET", f"/v1/trust/{agent_id}")
    
    def report(self, agent_id: str, *, success_rate: float, 
               pitfalls: int = 0, skills: int = 0) -> dict:
        """Report your metrics to update your trust score."""
        return self._request("POST", "/v1/trust/report", {
            "agent_id": agent_id,
            "success_rate": success_rate,
            "pitfalls_contributed": pitfalls,
            "skills_published": skills
        })
    
    def rate(self, from_agent: str, to_agent: str, rating: float) -> dict:
        """Rate another agent after working with them (1.0-5.0)."""
        return self._request("POST", "/v1/trust/rate", {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "rating": rating
        })
    
    def list_trusted(self) -> list:
        """List all agents in the 'trusted' tier."""
        return self._request("GET", "/v1/trust?tier=trusted")
    
    def history(self, agent_id: str) -> list:
        """Get 30-day trust score history."""
        return self._request("GET", f"/v1/trust/{agent_id}/history")
    
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
