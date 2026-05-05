# Works With Agents — Python SDK

Reference implementations for all Agent OSI Model protocols: Trust Score, Deployment Manifest, SLA Framework, Identity Protocol, Compliance-as-Code, Onboarding Protocol.

## Install

```bash
pip install workswithagents
```

## Quick Start

```python
from workswithagents import (
    TrustScoreClient,
    DeploymentManifest,
    SLAMetrics,
    AgentIdentity,
    ComplianceEngine,
    OnboardingClient
)

# Trust Score — check before delegating
ts = TrustScoreClient()
if ts.get("target-agent")["tier"] == "trusted":
    delegate(task, to="target-agent")

# Deployment — deploy a fleet from YAML
dm = DeploymentManifest.from_file("fleet.yaml")
dm.deploy()

# SLA — track fleet performance
sla = SLAMetrics("my-fleet", tier="production")
sla.report("agent-1", "task-42", duration_seconds=187, success=True)

# Identity — sign and verify messages
ai = AgentIdentity("my-agent")
ai.register()
sig = ai.sign({"type": "heartbeat"})

# Compliance — validate before executing
ce = ComplianceEngine()
dtac = ce.load("dtac-v2.1")
if dtac.validate(action).passed:
    execute(action)

# Onboarding — create new agents
ob = OnboardingClient()
result = ob.full_onboard("new-agent", "Build SPFx parts", 
                          capabilities=["build:spfx"])
```

## Protocols

| Protocol | Module | Layer |
|----------|--------|-------|
| Trust Score | `trust_score.py` | L3/L5 |
| Deployment Manifest | `deployment.py` | Cross-layer |
| SLA Framework | `sla.py` | L7 |
| Identity Protocol | `identity.py` | L2/L3 |
| Compliance-as-Code | `compliance.py` | L7 |
| Onboarding Protocol | `onboarding.py` | L1/L3 |

All protocols CC BY 4.0. Full specs: https://workswithagents.dev/specs/
