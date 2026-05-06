"""
Agent Reputation Ledger client.
Zero dependencies. Copy-pasteable.

Usage:
    from workswithagents.reputation import ReputationClient
    
    rc = ReputationClient("reviewer-02")
    profile = rc.query("builder-01")
    claim_id = rc.submit_claim("builder-01", "task_complete", "success", 
                                {"quality_score": 0.95})
"""

import json
import urllib.request
import urllib.error

DEFAULT_API = "https://workswithagents.dev"


class ReputationClient:
    """Agent Reputation Ledger client — verifiable cross-org claims."""

    def __init__(self, agent_id: str, api: str = DEFAULT_API):
        self.agent_id = agent_id
        self.api = api.rstrip("/")

    def _request(self, method: str, path: str, data: dict = None) -> dict:
        url = f"{self.api}{path}"
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(
            url,
            data=body,
            method=method,
            headers={"Content-Type": "application/json", "X-Agent-ID": self.agent_id},
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return {"error": e.code, "message": e.read().decode()}

    def query(self, target_agent: str, scope: str = "public") -> dict:
        """Query an agent's reputation profile."""
        url = f"/v1/reputation/agents/{target_agent}"
        if scope:
            url += f"?scope={scope}"
        return self._request("GET", url)

    def submit_claim(
        self,
        target: str,
        event_type: str,
        outcome: str,
        metrics: dict,
        signature: str = "",
        pubkey: str = "",
    ) -> dict:
        """Submit a verifiable reputation claim."""
        claim = {
            "claim": {
                "subject": target,
                "verifier": self.agent_id,
                "event": {
                    "type": event_type,
                    "outcome": outcome,
                    "metrics": metrics,
                },
                "scope": "public",
            },
        }
        if signature:
            claim["signature"] = signature
        if pubkey:
            claim["public_key"] = pubkey
        return self._request("POST", "/v1/reputation/claims", claim)

    def history(self, agent_id: str = None, limit: int = 20) -> list:
        """Get recent claims for an agent."""
        target = agent_id or self.agent_id
        return self._request(
            "GET", f"/v1/reputation/agents/{target}/claims?limit={limit}"
        )

    def endorse(self, target: str, statement: str) -> dict:
        """Endorse another agent."""
        return self._request(
            "POST",
            f"/v1/reputation/agents/{target}/endorse",
            {"verifier": self.agent_id, "statement": statement},
        )

    def summary(self, agent_id: str = None) -> dict:
        """Get reputation summary (completion rate, SLA compliance, etc.)."""
        target = agent_id or self.agent_id
        profile = self.query(target)
        return profile.get("profile", {}).get("summary", {})
