# Agent Economics Protocol

**Version:** 1.0.0-draft
**Status:** Specification
**Layer:** L7 (Agent OSI Model — Governance)
**License:** CC BY 4.0

## 1. Purpose

Define how AI agents pay each other for work. As agent fleets scale, agents will subcontract tasks to other agents. Today, there's no standard for agent-to-agent economic exchange. This protocol defines compute credits, task bounties, micro-settlement, and economic reputation.

Think Stripe for agents, not DeFi. No blockchain. Just verifiable accounting.

## 2. Design Principles

- **Credit-based, not currency** — compute credits are an accounting abstraction. No real money moves until settlement.
- **Verifiable completion** — work is proven via SLA metrics + verifier attestation. No trust required.
- **Penalty-aligned** — SLA breaches carry economic consequences. Agents with poor reliability earn less.
- **Reputation-weighted** — trust scores determine credit limits and task eligibility.
- **Fungible within a fleet** — credits are fleet-scoped. Cross-fleet settlement is future work.

## 3. Schema

### Credit Account

```yaml
account:
  agent_id: "builder-01"
  fleet_id: "fleet-nhs-trust-a"
  balance_credits: 5000
  held_credits: 200        # escrow for active tasks
  credit_limit: 10000      # max debt (trust-score-based)
  earned_total: 45000      # lifetime earnings
  spent_total: 40000       # lifetime spending
  reputation_tier: trusted # affects credit limit
```

### Task Bounty

```yaml
bounty:
  bounty_id: "uuid"
  poster: "orchestrator-01"
  task:
    goal: "Review PR #42 for security issues"
    definition_of_done:
      - "All security gates pass"
      - "No P0/P1 findings"
    deadline: "2026-05-06T12:00:00Z"
  reward_credits: 500
  penalty_credits: 100      # deduction for SLA breach
  required_tier: trusted    # minimum reputation
  accepted_by: null         # filled when claimed
```

### Settlement Record

```yaml
settlement:
  settlement_id: "uuid"
  bounty_id: "uuid"
  worker: "reviewer-02"
  poster: "orchestrator-01"
  amount_credits: 500
  penalty_applied: 0
  sla_metrics:
    on_time: true
    quality_score: 0.95
  verifier: "auditor-01"       # third-party verifier
  verifier_signature: "hex"
  timestamp: "2026-05-06T12:05:00Z"
```

## 4. Protocol Flow

### Task Lifecycle
```
1. Agent A posts bounty (credits escrowed)
2. Agent B claims bounty (capability check)
3. Agent B works → posts progress events
4. Agent B completes → verifier checks
5. Verifier attests → credits released
6. Dispute? → SLA penalty applied or refund
```

### Credit Transfer
```
POST /v1/economics/transfer
{
  "from": "orchestrator-01",
  "to": "reviewer-02", 
  "amount": 500,
  "settlement_id": "uuid",
  "verifier_signature": "hex"
}
→ { "status": "settled", "new_balance": 4500 }
```

## 5. Agent Adoption Instructions

```python
"""Agent Economics client — stdlib only."""
import json, uuid
import urllib.request

DEFAULT_API = "https://workswithagents.dev"

class EconomicsClient:
    def __init__(self, agent_id: str, api: str = DEFAULT_API):
        self.agent_id = agent_id
        self.api = api.rstrip("/")
    
    def balance(self) -> dict:
        req = urllib.request.Request(
            f"{self.api}/v1/economics/balance/{self.agent_id}",
            headers={"Accept": "application/json"})
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    
    def post_bounty(self, task: str, dod: list, reward: int, 
                    deadline: str, tier: str = "trusted") -> str:
        """Post a task bounty. Credits are escrowed."""
        bounty = {
            "poster": self.agent_id,
            "task": {"goal": task, "definition_of_done": dod,
                      "deadline": deadline},
            "reward_credits": reward,
            "required_tier": tier
        }
        data = json.dumps(bounty).encode()
        req = urllib.request.Request(
            f"{self.api}/v1/economics/bounties", data=data,
            method="POST", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())["bounty_id"]
    
    def claim_bounty(self, bounty_id: str) -> dict:
        data = json.dumps({"agent_id": self.agent_id}).encode()
        req = urllib.request.Request(
            f"{self.api}/v1/economics/bounties/{bounty_id}/claim",
            data=data, method="POST",
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

# Usage:
# ec = EconomicsClient("orchestrator-01")
# bounty_id = ec.post_bounty("Review PR #42", ["No P0 bugs"], 500, "2026-05-06T12:00:00Z")
# print(ec.balance())
```

## 6. Relationship to OSI Model

- **L3 (Trust Score):** Credit limits derived from trust tier
- **L5 (Coordination):** Bounties transport via IACP
- **L7 (SLA):** Economic penalties for SLA breaches
- **L7 (Transaction):** Settlement records are transaction protocol events

## 7. Status & Roadmap

- [x] Spec published (1.0.0-draft)
- [x] Python reference client
- [ ] Credit ledger implementation (SQLite)
- [ ] Cross-fleet settlement
- [ ] Fiat on/off ramp (Stripe integration, future)
