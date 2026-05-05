# Agent Transaction Protocol (ATP) — Layer 7 Governance

**Version:** 1.0.0-draft
**Status:** Specification
**Layer:** 7 — Governance (Agent OSI Model)
**License:** CC BY 4.0

---

## 1. Purpose

The Agent Transaction Protocol defines guarantees for autonomous agent actions. When an agent says "I'll deploy this," what actually happens? Did it deploy? Did it deploy only once? Can it undo? Who's accountable?

Message queues solved this for distributed systems (at-least-once, at-most-once, exactly-once delivery). This protocol solves it for agent *actions* — the things agents DO, not just the messages they send.

---

## 2. The Problem

**Without guarantees:**

| Scenario | What happens today | What should happen |
|----------|-------------------|-------------------|
| Agent deploys to production | "I think it deployed" — no confirmation | Confirmation with deployment ID, rollback available |
| Agent charges a customer | No idempotency — double charge possible | Idempotency key ensures single charge |
| Agent deletes data | No undo — data is gone | Soft delete with recovery window |
| Agent A and Agent B both act | No trace of who did what | Every action attributed to a specific agent and session |
| Compliance audit | "Trust us, the agents did the right thing" | Immutable audit trail of every action |

---

## 3. Design Principles

- **Intent before action.** Every action is logged BEFORE execution (intent) and AFTER (confirmation). If the agent crashes mid-action, we know it intended to do something.
- **Idempotency by default.** Every action carries a unique idempotency key. Replaying the same key produces the same result.
- **Rollback where possible.** Every action declares whether it's reversible and provides a rollback hook if so.
- **Attribution always.** Every action carries agent_id, session_id, and human_approver (if required).
- **Compliance-readable.** Actions are logged in a format that auditors can query without understanding agent internals.

---

## 4. Action Lifecycle

```
INTENDED → APPROVED (if required) → EXECUTING → COMPLETED | FAILED | ROLLED_BACK
                                                       ↓
                                                  ROLLING_BACK → ROLLED_BACK
```

| State | Meaning |
|-------|---------|
| **INTENDED** | Agent declared intent. Logged. Not yet executed. |
| **APPROVED** | Human or compliance gate approved. Ready to execute. |
| **EXECUTING** | Action is in progress. |
| **COMPLETED** | Action succeeded. Confirmation logged. |
| **FAILED** | Action failed. Error logged. May be retried with same idempotency key. |
| **ROLLING_BACK** | Undo in progress. |
| **ROLLED_BACK** | Undo complete. System returned to pre-action state. |

---

## 5. Guarantee Levels

Actions declare one of three guarantee levels:

### 5.1 Best-Effort (ATP-1)

"Try to do this. If it fails, log it and move on."

**Use for:** Non-critical actions. Research queries. Health checks. Logging.

**Characteristics:**
- No idempotency required (but recommended)
- No rollback
- Fire-and-forget
- Logged but not guaranteed

**Example:** Agent queries a search API. If it fails, it tries a different API.

### 5.2 At-Least-Once (ATP-2)

"This must happen. Retry until it does."

**Use for:** Deployments. Data writes. Notifications. Any action where doing it twice is safe (idempotent) or where NOT doing it is worse than doing it twice.

**Characteristics:**
- Idempotency key REQUIRED
- Automatic retry with exponential backoff
- Rollback optional
- Confirmation logged on success

**Example:** Agent deploys a web part to SharePoint. If the deploy fails (network timeout), retry with same idempotency key.

### 5.3 Exactly-Once (ATP-3)

"This must happen exactly once. If it can't, roll back everything."

**Use for:** Billing. Data deletion. Compliance-significant actions. Regulated industry operations.

**Characteristics:**
- Idempotency key REQUIRED
- Pre-action snapshot (state before change)
- Rollback hook REQUIRED
- Human approval REQUIRED (Layer 7 governance gate)
- Immutable audit trail entry
- SLO: 99.9% exactly-once guarantee

**Example:** Agent processes a payment. Before charging: snapshot balance. After charging: log transaction with idempotency key. If anything fails: rollback via refund hook.

---

## 6. Action Schema

```yaml
atp_version: "1.0.0-draft"
action_id: "act-20260505-001"
idempotency_key: "deploy-project-dashboard-v3"
guarantee_level: "atp-2"        # atp-1 | atp-2 | atp-3

# Who
agent_id: "hermes-spfx-builder"
session_id: "sess-abc123"
fleet_id: "works-with-agents-fleet-1"
human_approver: null             # required for ATP-3

# What
action:
  verb: "deploy"
  target: "sharepoint-app-catalog"
  description: "Deploy SPFx web part 'ProjectDashboard' v3.2.1 to production app catalog"
  parameters:
    package_path: "/build/project-dashboard.sppkg"
    tenant: "contoso.sharepoint.com"
    site: "/sites/appcatalog"
    
# Safety
reversible: true
rollback:
  verb: "remove"
  description: "Remove deployed package from app catalog"
  parameters:
    package_id: "project-dashboard"
    tenant: "contoso.sharepoint.com"

# Timing
created_at: "2026-05-05T21:00:00Z"
deadline: "2026-05-05T21:05:00Z"  # action fails if not completed by deadline
retry_policy:
  max_retries: 3
  backoff: "exponential"          # exponential | linear | fixed
  initial_delay_seconds: 2
  max_delay_seconds: 60

# Compliance (Layer 7)
compliance:
  audit_trail_id: "audit-20260505-001"
  regulation_refs: []             # e.g., ["GDPR-Art-17", "DTAC-2.1.3"]
  data_classification: "internal" # public | internal | confidential | restricted
  sign_off_required: false
  sign_off_by: null
  evidence_required: false

# Result (populated after execution)
result:
  state: "COMPLETED"
  completed_at: "2026-05-05T21:01:15Z"
  duration_seconds: 75
  retry_count: 1
  confirmation:
    package_id: "project-dashboard-v3.2.1"
    deployed_to: "https://contoso.sharepoint.com/sites/appcatalog"
  error: null
```

---

## 7. Audit Trail

Every action produces an immutable audit trail entry:

```yaml
audit_entry:
  audit_id: "audit-20260505-001"
  action_id: "act-20260505-001"
  timestamp: "2026-05-05T21:01:15Z"
  agent_id: "hermes-spfx-builder"
  session_id: "sess-abc123"
  verb: "deploy"
  target: "sharepoint-app-catalog"
  guarantee_level: "atp-2"
  result_state: "COMPLETED"
  duration_seconds: 75
  human_approver: null
  regulation_refs: []
  hash: "sha256:a1b2c3d4..."    # hash of entire action record for tamper detection
  previous_hash: "sha256:..."   # chain to previous entry (append-only log)
```

**Queryable by:**
- Agent ID (what did agent X do?)
- Time range (what happened between 2pm and 3pm?)
- Verb (show all "deploy" actions)
- Regulation ref (show all GDPR-relevant actions)
- Guarantee level (show all ATP-3 actions that required human approval)

---

## 8. Integration with Other Layers

| Layer | How ATP is used |
|-------|----------------|
| L1 (Execution) | Actions execute on Layer 1 resources |
| L2 (Communication) | ATP actions may trigger L2 messages (notify on complete) |
| L3 (Discovery) | Agent identity and capability from L3 |
| L4 (Session) | Session ID links action to the handoff chain |
| L5 (Coordination) | Coordination decisions logged as ATP actions |
| L6 (Verification) | Test results logged as ATP actions for audit |
| L7 (Governance) | **This is Layer 7.** ATP is the governance execution layer. |

---

## 9. Regulated Industry Extension (ATP-R)

For NHS, financial services, and government:

**Additional fields:**
```yaml
compliance:
  regulation_refs: ["DTAC-2.1.3", "GDPR-Art-32"]
  dpia_ref: "DPIA-2026-001"           # Data Protection Impact Assessment
  clinical_safety_ref: "CS-2026-042"   # NHS clinical safety case
  smr_accountable: "john.smith@nhs.uk" # Senior Managers Regime (FCA)
  gds_assessment_ref: "GDS-Alpha-2026"  # Government Digital Service
  retention_policy: "7_years"           # How long audit trail is kept
  deletion_policy: "hard_delete_30d"    # When action data is purged
```

---

## 10. Implementation Notes

### Minimum viable implementation

1. **Intent log** — simple SQLite table. Log every action BEFORE execution.
2. **Idempotency keys** — UUID per action. Check before executing.
3. **Confirmation log** — update intent record after execution.
4. **Query endpoint** — GET /v1/audit?agent_id=X&time_from=Y

That's 200 lines of Python. Full protocol is 500 lines.

### Integration with existing systems

- **Hermes agents:** Add `--audit` flag to terminal() calls. Actions logged automatically.
- **Cron jobs:** Each cron run is an ATP action. Success/failure logged.
- **Deployments:** Deploy actions get ATP-2 guarantees with idempotency.
- **Regulated environments:** ATP-3 for all compliance-significant actions.

---

## 11. Status & Roadmap

| Component | Status |
|-----------|--------|
| Protocol spec | Draft 1.0.0 |
| Action schema | Complete |
| Guarantee levels (ATP-1,2,3) | Defined |
| Audit trail schema | Defined |
| Regulated extension (ATP-R) | Draft |
| Reference implementation | Not yet built |
| Audit trail API | Not yet built |

**Next:** Build the audit trail as a SQLite table + query API. Integrate with Hermes terminal() tool for automatic action logging.

---

*This document is part of the Agent OSI Model framework. See the OSI Model document for the full 7-layer architecture.*
