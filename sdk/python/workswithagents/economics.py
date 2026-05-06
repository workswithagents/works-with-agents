"""
Agent Economics Protocol client.
Zero dependencies. Copy-pasteable.

Usage:
    from workswithagents.economics import EconomicsClient
    
    ec = EconomicsClient("orchestrator-01")
    balance = ec.balance()
    bounty_id = ec.post_bounty("Review PR #42", ["No P0 bugs"], 500, "2026-05-06T12:00:00Z")
"""

import json
import urllib.request
import urllib.error

DEFAULT_API = "https://workswithagents.dev"


class EconomicsClient:
    """Agent Economics Protocol client — compute credits, bounties, settlement."""

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

    def balance(self) -> dict:
        """Get agent credit balance and account info."""
        return self._request("GET", f"/v1/economics/balance/{self.agent_id}")

    def post_bounty(
        self,
        task: str,
        dod: list,
        reward: int,
        deadline: str,
        tier: str = "trusted",
    ) -> dict:
        """Post a task bounty. Credits are escrowed."""
        return self._request(
            "POST",
            "/v1/economics/bounties",
            {
                "poster": self.agent_id,
                "task": {
                    "goal": task,
                    "definition_of_done": dod,
                    "deadline": deadline,
                },
                "reward_credits": reward,
                "required_tier": tier,
            },
        )

    def claim_bounty(self, bounty_id: str) -> dict:
        """Claim an available bounty."""
        return self._request(
            "POST",
            f"/v1/economics/bounties/{bounty_id}/claim",
            {"agent_id": self.agent_id},
        )

    def list_bounties(self, status: str = "open") -> list:
        """List available bounties."""
        return self._request(
            "GET", f"/v1/economics/bounties?status={status}"
        )

    def settle(self, bounty_id: str, outcome: str, metrics: dict = None) -> dict:
        """Settle a completed bounty."""
        return self._request(
            "POST",
            f"/v1/economics/bounties/{bounty_id}/settle",
            {
                "worker": self.agent_id,
                "outcome": outcome,
                "metrics": metrics or {},
            },
        )
