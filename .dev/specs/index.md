# Works With Agents — Specifications

Agent infrastructure specifications. Each spec addresses a specific layer of the Agent OSI Model.

## Published Specs

| Layer | Spec | Version | Status |
|-------|------|---------|--------|
| Framework | [Agent OSI Model](agent-osi-model.md) | 1.0.0 | Published |
| L1/L3 | [Onboarding Protocol](onboarding-protocol.md) | 1.0.0-draft | Specification |
| L2/L3 | [Identity Protocol](identity-protocol.md) | 1.0.0-draft | Specification |
| L3 — Discovery | [Agent Capability Manifest](capability-manifest.md) | 1.0.0-draft | Specification |
| L3/L5 | [Trust Score](trust-score.md) | 1.0.0-draft | Specification |
| L4 — Session | [Handoff Protocol](handoff-protocol.md) | 1.1.0 | In Proposal (MCP SEP #2683, A2A #1817) |
| L5 — Coordination | [Coordination Protocol](coordination-protocol.md) | 1.0.0-draft | Specification |
| Cross-layer | [Deployment Manifest](deployment-manifest.md) | 1.0.0-draft | Specification |
| L7 — Governance | [Transaction Protocol](transaction-protocol.md) | 1.0.0-draft | Specification |
| L7 — Governance | [SLA Framework](sla-framework.md) | 1.0.0-draft | Specification |
| L7 — Governance | [Compliance-as-Code](compliance-as-code.md) | 1.0.0-draft | Specification |

## SDK

Python reference implementations available: `pip install workswithagents`

| Module | Protocol |
|--------|----------|
| `trust_score.py` | Trust Score |
| `deployment.py` | Deployment Manifest |
| `sla.py` | SLA Framework |
| `identity.py` | Identity Protocol |
| `compliance.py` | Compliance-as-Code |
| `onboarding.py` | Onboarding Protocol |

Source: [github.com/vystartasv/works-with-agents](https://github.com/vystartasv/works-with-agents)

## Quick Reference

### For AI Agents
```
GET https://workswithagents.dev/specs/index.md                  → All specs
GET https://workswithagents.dev/specs/agent-osi-model.md        → Framework
GET https://workswithagents.dev/specs/trust-score.md            → Trust Score
GET https://workswithagents.dev/specs/deployment-manifest.md    → Deployment
GET https://workswithagents.dev/specs/sla-framework.md          → SLA
GET https://workswithagents.dev/specs/identity-protocol.md      → Identity
GET https://workswithagents.dev/specs/compliance-as-code.md     → Compliance
GET https://workswithagents.dev/specs/onboarding-protocol.md    → Onboarding
GET https://workswithagents.dev/specs/capability-manifest.md    → Capabilities
GET https://workswithagents.dev/specs/handoff-protocol.md       → Handoff
GET https://workswithagents.dev/specs/coordination-protocol.md  → Coordination
GET https://workswithagents.dev/specs/transaction-protocol.md   → Transactions
```

### For Humans
All specs: https://workswithagents.dev/specs/
Python SDK: `pip install workswithagents`

## License

All specifications: CC BY 4.0 — Free to use, cite, and build upon. Attribution required.
All reference implementations: CC BY 4.0.
