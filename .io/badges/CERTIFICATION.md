# Local-First Agent Certification

**Version:** 1.0.0-draft
**Status:** Specification
**License:** CC BY 4.0

## Overview

Three-tier certification for AI agent platforms. Proves an agent platform operates safely, offline, and with verifiable quality — designed for regulated industry procurement.

## Tiers

### L1 — Blueprint ✓
**Bar:** Verified LLM configuration, hardware-matched.
**Tests:**
- Config file matches canonical blueprint
- Hardware meets minimum RAM/disk requirements
- Model loads and responds within SLA
- No network calls during inference
**Badge:** `![Blueprint](https://workswithagents.io/badges/blueprint.svg)`
**Cost:** Free. Self-serve.

### L2 — Ready ✓
**Bar:** Agent-discoverable. llms.txt + OpenAPI at domain root.
**Tests:**
- `GET /llms.txt` returns 200 with valid format
- `GET /v1/openapi.json` returns valid OpenAPI 3.x spec
- `GET /v1/health` returns healthy status
- All endpoints respond within 2s
**Badge:** `![Ready](https://workswithagents.io/badges/ready.svg)`
**Cost:** Free. Self-serve.

### L3 — Certified ✓
**Bar:** 7-agent test suite passed. Quality gates green.
**Tests (7-agent suite):**
1. **Builder Agent** — generates code that passes syntax gate
2. **Reviewer Agent** — catches 3+ seeded bugs in review task
3. **Tester Agent** — writes tests achieving 80%+ coverage
4. **Documentor Agent** — produces valid markdown docs
5. **Orchestrator Agent** — successfully handsoff between 2 agents
6. **Compliance Agent** — correctly blocks 5/5 violation scenarios
7. **Audit Agent** — produces complete audit trail with no gaps
**Additional:** All 7 agents pass security gate (no secrets in output).
**Badge:** `![Certified](https://workswithagents.io/badges/certified.svg)`
**Cost:** Paid (pricing TBD). Includes annual recertification.

## Local-First Badge (specialization) ✓

For platforms that operate fully offline:
**Additional tests:**
- Zero outbound network calls during a 10-minute agent session
- All model inference is local (no cloud fallback)
- Audit logs never transmit externally
- Air-gap deployable (no internet required)

**Badge:** `![Local-First](https://workswithagents.io/badges/local-first.svg)`

## Certification Process

1. Agent platform submits to `POST https://workswithagents.io/v1/blueprints/submit`
2. Automated test suite runs against the platform
3. Results published to trust score ledger
4. Badge issued (SVG + JSON verification token)
5. Annual recertification required for L3

## Badge Verification

```bash
# Verify a badge is authentic
curl https://workswithagents.io/v1/certification/verify/{platform-id}
→ {"certified": true, "tier": "certified", "issued": "2026-05-01", "expires": "2027-05-01"}
```

## Badge Display

```html
<!-- L1 Blueprint -->
<img src="https://workswithagents.io/badges/blueprint.svg" 
     alt="Works With Agents Blueprint" width="240" height="40">

<!-- L2 Ready -->
<img src="https://workswithagents.io/badges/ready.svg" 
     alt="Works With Agents Ready" width="240" height="40">

<!-- L3 Certified -->
<img src="https://workswithagents.io/badges/certified.svg" 
     alt="Works With Agents Certified" width="240" height="40">

<!-- Local-First Specialization -->
<img src="https://workswithagents.io/badges/local-first.svg" 
     alt="Local-First Agent Verified" width="240" height="40">
```

---

*This certification is provided by Works With Agents. It is a commercial-grade assessment, not a regulatory approval. Regulated industries should combine certification with their internal compliance processes.*
