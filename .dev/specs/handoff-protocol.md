# Handoff Protocol — Layer 4

**Version:** 1.0.0-draft
**Status:** Specification
**Layer:** 4 — Session (Agent OSI Model)
**License:** CC BY 4.0

## 1. Purpose

Define how one AI agent transfers an in-progress task to another agent — with full context, no data loss, and verifiable acceptance. The Handoff Protocol ensures "what agent A knows, agent B can continue."

MCP (Model Context Protocol) handles agent→tool. IACP handles agent↔agent async messaging. Handoff handles agent→agent task transfer — the moment where one agent's work becomes another agent's responsibility.

## 2. Design Principles

- **Complete context transfer.** No handoff is partial. The receiving agent gets everything the sending agent has about the task.
- **Verifiable acceptance.** The receiving agent confirms it has received, understood, and accepted the handoff. Silent drops are detectable.
- **Attribution preserved.** The handoff chain is auditable — every task knows which agents worked on it and who handed it off to whom.
- **Idempotent replay.** If a handoff is retried (network failure), the receiving agent recognizes duplicates.
- **Framework-agnostic.** Works between any agent frameworks (Hermes, Claude Code, Codex, Copilot).

## 3. Handoff Lifecycle

```
SENDER                    RECEIVER
  |                          |
  |─── Handoff Request ────>|  (task_id, context_pack)
  |                          |
  |<── Ack/Reject ─────────|  (accept + handoff_id, or decline + reason)
  |                          |
  |─── Status Query ──────>|  (optional: "how's it going?")
  |<── Progress Update ────|  (optional: "30% done, 3 pitfalls found")
  |                          |
  |<── Completion Event ───|  (task done, results attached)
  |                          |
```

## 4. Message Format

### Handoff Request

```json
{
  "handoff_id": "uuid-v7",
  "task_id": "original-task-uuid",
  "sender": {
    "agent_id": "builder-01",
    "session_id": "sess-456",
    "identity_sig": "ed25519-hex"
  },
  "context": {
    "task_description": "Build a compliance report for NHS DTAC",
    "workspace_path": "/projects/nhs-audit",
    "state_snapshot": {
      "files_modified": ["report.md", "evidence.json"],
      "branch": "feature/nhs-compliance",
      "last_commit": "abc123"
    },
    "agent_memory": {
      "key_decisions": ["Use ISO 27001 mapping", "Skip clinical safety section"],
      "discovered_pitfalls": [
        "SPFx Heft build fragile on SCSS resolution",
        "Node v18 required for NHS toolkit"
      ],
      "pending_items": ["Review with Pelin", "Attach DPIA appendix"]
    },
    "tools_required": ["terminal", "file", "web", "browser"],
    "constraints": {
      "max_turns": 30,
      "deadline": "2026-05-07T17:00:00Z",
      "compliance_level": "nhs-dtac"
    }
  },
  "quality_checklist": [
    "DPIA referenced where personal data involved",
    "Model Card attached for any LLM usage",
    "No patient data in outputs",
    "Audit trail is complete"
  ]
}
```

### Handoff Response

```json
{
  "handoff_id": "uuid-v7",
  "status": "accepted",
  "receiver": {
    "agent_id": "reviewer-02",
    "session_id": "sess-789",
    "identity_sig": "ed25519-hex"
  },
  "estimated_completion": "2026-05-07T14:00:00Z",
  "queries": [
    "Which DPIA template should I use?"
  ],
  "receiver_context": {
    "available_tools": ["terminal", "file", "web"],
    "model": "DeepSeek-v4-pro",
    "max_context_tokens": 131072
  }
}
```

## 5. Error Conditions

| Condition | Response | Retry |
|-----------|----------|-------|
| Task already completed | `status: already_done` with results | No |
| Task already handed off | `status: duplicate` with original handoff_id | No |
| Insufficient tools | `status: rejected, reason: missing_tools` | Maybe (different agent) |
| Context too large | `status: rejected, reason: context_overflow` | Yes (with compression) |
| Agent busy | `status: queued` with estimated wait | No (poll status) |
| Timeout | No response within TTL | Yes (exponential backoff) |

## 6. Quality Gates

Before accepting a handoff, the receiving agent SHOULD verify:

1. Identity signature is valid
2. Context is complete (no missing sections)
3. Required tools are available
4. Task is within capability (manifest check)
5. No conflicting task already in progress
6. Deadline is achievable

## 7. Security

- All handoffs are signed with Ed25519 identity keys
- Sensitive context fields MAY be encrypted with the receiver's public key
- Handoff audit trail is immutable — every transfer is logged
- Quality checklist provides compliance teams with verifiable governance

## 8. Relationship to Other Protocols

| Protocol | Layer | Relationship |
|----------|-------|--------------|
| Identity Protocol | L2 | Handoff uses identity signatures from Identity Protocol |
| IACP | L5 | Handoff messages are carried over IACP as `intent: handoff` |
| Transaction Protocol | L7 | Handoff acceptance creates a transaction audit entry |
| Compliance-as-Code | L7 | Quality checklist is a Compliance-as-Code rule set |
