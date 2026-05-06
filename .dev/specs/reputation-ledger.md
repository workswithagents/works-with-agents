# Agent Reputation Ledger

**Version:** 1.0.0-draft
**Status:** Specification
**Layer:** Cross-layer (L2/L3 Identity + L5 Coordination)
**License:** CC BY 4.0

## 1. Purpose

Define an immutable, cross-organization reputation system for AI agents. Trust scores answer "how reliable is this agent?" Reputation answers "what has this agent actually done, and who verified it?"

Verifiable claims — signed by a verifier, not self-reported — create a tamper-evident history that survives across organizations, model updates, and agent retirements.

## 2. Design Principles

- **Verifiable, not self-reported** — claims must be signed by a third-party verifier (another agent or human).
- **Append-only** — claims are never deleted, only superseded by newer claims.
- **Cross-org queryable** — an agent from Org A can query the reputation of an agent from Org B.
- **Privacy-scoped** — claims have visibility: public, org-only, or private.
- **Not a blockchain** — SQLite-based reference implementation. No consensus, no mining.

## 3. Schema

### Reputation Claim

```yaml
claim:
  claim_id: "uuid-v7"
  subject: "builder-01"          # agent being evaluated
  verifier: "reviewer-02"        # who verified this
  verifier_org: "nhs-trust-a"
  
  event:
    type: task_complete          # task_complete | handoff_complete | sla_breach
    task_id: "uuid"
    outcome: success             # success | partial | failure
    metrics:
      quality_score: 0.95
      on_time: true
      tokens_used: 12000
      gates_passed: 4/4
  
  scope: public                  # public | org | private
  issued_at: "2026-05-06T12:00:00Z"
  expires_at: null               # null = permanent
  
  # Cryptographic proof
  verifier_signature: "hex-ed25519"
  verifier_public_key: "hex-ed25519-pub"
```

### Agent Reputation Profile

```yaml
profile:
  agent_id: "builder-01"
  claims_count: 142
  verifiers_count: 8             # unique verifiers
  orgs_count: 3                  # across 3 organizations
  
  summary:
    task_completion_rate: 0.94
    sla_compliance: 0.97
    avg_quality_score: 0.92
    total_tasks_completed: 134
    total_sla_breaches: 4
  
  endorsements:
    - verifier: "senior-reviewer-01"
      statement: "Consistently produces clean, tested code"
      date: "2026-04-15"
```

## 4. API / Protocol

### Submit a claim
```
POST /v1/reputation/claims
Authorization: Bearer <verifier-token>
{
  "claim": {
    "subject": "builder-01",
    "event": {"type": "task_complete", "outcome": "success", ...},
    "scope": "public"
  },
  "signature": "hex-ed25519"
}
→ { "claim_id": "uuid", "status": "accepted" }
```

### Query agent reputation
```
GET /v1/reputation/agents/builder-01
→ { "profile": {...}, "recent_claims": [...] }

GET /v1/reputation/agents/builder-01?scope=public
→ { "profile": {...} }  # org-only claims excluded
```

### Cross-org query
```
GET /v1/reputation/agents/builder-01?org=nhs-trust-b
→ { "profile": {...} }  # claims visible to requesting org
```

## 5. Agent Adoption Instructions

```python
"""Reputation client — stdlib only."""
import json, uuid
import urllib.request

DEFAULT_API = "https://workswithagents.dev"

class ReputationClient:
    def __init__(self, agent_id: str, api: str = DEFAULT_API):
        self.agent_id = agent_id
        self.api = api.rstrip("/")
    
    def query(self, target_agent: str, scope: str = "public") -> dict:
        """Query an agent's reputation profile."""
        url = f"{self.api}/v1/reputation/agents/{target_agent}"
        if scope:
            url += f"?scope={scope}"
        req = urllib.request.Request(url, headers={
            "X-Agent-ID": self.agent_id,
            "Accept": "application/json"
        })
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    
    def submit_claim(self, target: str, event_type: str,
                     outcome: str, metrics: dict,
                     signature: str, pubkey: str) -> str:
        """Submit a verifiable claim. Requires cryptographic signature."""
        claim = {
            "claim": {
                "subject": target,
                "verifier": self.agent_id,
                "event": {"type": event_type, "outcome": outcome,
                          "metrics": metrics},
                "scope": "public"
            },
            "signature": signature,
            "public_key": pubkey
        }
        data = json.dumps(claim).encode()
        req = urllib.request.Request(
            f"{self.api}/v1/reputation/claims", data=data,
            method="POST", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())["claim_id"]

# Usage:
# rc = ReputationClient("reviewer-02")
# profile = rc.query("builder-01")
# print(f"Completion rate: {profile['profile']['summary']['task_completion_rate']}")
```

## 6. Relationship to OSI Model

- **L2 (Identity):** Claims signed with AgentIdentity keys — cryptographic proof of verifier
- **L3 (Trust Score):** Reputation feeds trust score calculations
- **L5 (Coordination):** IACP messages carry reputation queries between agents
- **L7 (SLA):** SLA breach events become reputation claims

## 7. Status & Roadmap

- [x] Spec published (1.0.0-draft)
- [x] Python reference client
- [ ] SQLite reference implementation
- [ ] Cross-org federation protocol
- [ ] Human endorsement layer (LinkedIn-style recommendations for agents)
- [ ] Reputation token bridging (portable reputation across ecosystems)
