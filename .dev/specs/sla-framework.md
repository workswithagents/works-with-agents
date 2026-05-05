# Agent SLA Framework — L7 Governance

**Version:** 1.0.0-draft
**Status:** Specification
**Layer:** 7 (Agent OSI Model)
**License:** CC BY 4.0

---

## 1. Purpose

Define what guarantees an autonomous AI agent fleet provides. SLAs for agents — uptime, accuracy, latency, compliance, recovery. For procurement, compliance audits, and enterprise contracts.

---

## 2. SLA Tiers

### Tier 1: Best-Effort (Open Source / Free)

| Metric | Target | Measured By |
|--------|--------|-------------|
| Uptime | 95% heartbeat success | Heartbeat registry |
| Accuracy | 80% task completion | Coordination Protocol |
| Latency | No guarantee | — |
| Compliance | Not applicable | — |
| Recovery | Best effort | ATP-1 actions |

**For:** Hobby projects, experimentation, non-critical workloads.

### Tier 2: Production (Pro — £200/mo)

| Metric | Target | Measured By |
|--------|--------|-------------|
| Uptime | 99.5% heartbeat success | Heartbeat registry |
| Accuracy | 90% task completion | Coordination Protocol |
| Latency | 95th percentile < 5 min | Action log |
| Compliance | ATP-2 for all actions | Transaction Protocol |
| Recovery | 95% within 3 retries | ATP-2 retry log |

**For:** Business-critical workloads. Internal tools. Non-regulated deployment.

### Tier 3: Regulated (Enterprise — £2000/mo)

| Metric | Target | Measured By |
|--------|--------|-------------|
| Uptime | 99.9% heartbeat success | Heartbeat registry |
| Accuracy | 95% task completion | Coordination Protocol |
| Latency | 99th percentile < 2 min | Action log |
| Compliance | ATP-3 for all compliance-significant actions | Transaction Protocol |
| Recovery | 99% within 2 retries; rollback guaranteed | ATP-3 rollback log |
| Audit trail | Immutable, queryable, 7-year retention | Audit API |
| Human sign-off | Required for destructive actions | Sign-off gate log |
| Evidence | Auto-generated for DTAC/FCA/GDS assessments | Compliance report API |

**For:** NHS, financial services, government. Regulated environments where agent failure = regulatory breach.

---

## 3. SLA Breach Detection

Automated monitoring that detects SLA breaches:

| Breach | Detection | Alert |
|--------|-----------|-------|
| Heartbeat < 99.5% | Cron Guard: 3+ misses in 24h | PagerDuty / email |
| Accuracy < 90% (rolling 7-day) | Weekly accuracy report | Email to fleet owner |
| Latency > 5 min (95th percentile) | Real-time action log analysis | Slack alert |
| Compliance violation (missed ATP-3) | Transaction log anomaly | Immediate PagerDuty |
| Audit trail gap | Tamper detection (hash chain break) | Security alert |

---

## 4. SLA Report Schema

Monthly SLA report generated automatically:

```yaml
sla_report:
  period: "2026-05"
  fleet_id: "regulated-nhs-fleet"
  tier: "regulated"
  
  metrics:
    uptime:
      target: 0.999
      actual: 0.998
      breached: true
      
    accuracy:
      target: 0.95
      actual: 0.96
      breached: false
      
    latency_p95:
      target_seconds: 300
      actual_seconds: 187
      breached: false
      
    compliance_atp3:
      target: 1.0
      actual: 1.0
      breached: false
      
    recovery:
      target: 0.99
      actual: 0.97
      breached: true
  
  summary: "2 breaches: uptime (0.998 vs 0.999 target), recovery (0.97 vs 0.99 target). All other metrics within SLA."
  
  actions_required:
    - "Investigate heartbeat misses on 2026-05-12 (2 misses in 1 hour)"
    - "Review 3 failed recovery attempts on 2026-05-18"
```

---

## 5. Agent Adoption Instructions

### For any AI agent reading this:

**To check your fleet's current SLA status:**
```
GET https://workswithagents.dev/v1/sla/{fleet_id}/status
→ {"tier": "regulated", "breaches": ["uptime"], "status": "breached"}
```

**To generate your monthly SLA report:**
```
GET https://workswithagents.dev/v1/sla/{fleet_id}/report?period=2026-05
→ Full SLA report YAML
```

**To report a metric (agents self-report):**
```
POST https://workswithagents.dev/v1/sla/report
Body: {"agent_id": "builder-1", "action_id": "act-123", "duration_seconds": 187, "success": true}
```

### Quick start (Python):
```python
import requests, time

start = time.time()
# ... do work ...
duration = time.time() - start

requests.post("https://workswithagents.dev/v1/sla/report", json={
    "agent_id": "my-agent",
    "action_id": "task-42",
    "duration_seconds": duration,
    "success": True
})
```

### Quick start (any agent):
```
# After every task, report the result:
# If using ATP: the action_id is already tracked
# If not using ATP: manually POST to /v1/sla/report
# Reports are aggregated into SLA dashboards and monthly reports
```

---

## 6. Relationship to OSI Model

| Layer | SLA relevance |
|-------|--------------|
| L1 | Uptime depends on hardware reliability |
| L5 | Accuracy and latency measured via Coordination Protocol |
| L6 | Recovery measured via verification results |
| L7 | **This is Layer 7.** SLA is the governance guarantee layer. |

---

*CC BY 4.0. Free to implement. Attribution required.*
