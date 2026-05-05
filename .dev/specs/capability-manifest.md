# Agent Capability Manifest — Layer 3 Discovery

**Version:** 1.0.0-draft
**Status:** Specification
**Layer:** 3 — Discovery (Agent OSI Model)
**License:** CC BY 4.0

---

## 1. Purpose

The Agent Capability Manifest is a machine-readable declaration of what an AI agent can do. It's the agent equivalent of `package.json` — a self-describing document that tells other agents and orchestration systems:

- **What this agent can do** (capabilities)
- **How well it does it** (performance metrics)
- **What it needs** (resource requirements)
- **How to reach it** (endpoint)
- **Whether it's alive** (status)

---

## 2. Why This Exists

**Problem:** Before delegating work to an agent, you need to know if it CAN do the work. Today, this knowledge is hardcoded ("the SPFx builder handles SPFx builds") or convention-based. When an agent dies and a replacement spawns, nobody knows what the replacement can do without manual reconfiguration.

**Solution:** Every agent publishes a Capability Manifest at a known location. Orchestrators and other agents query the manifest to discover capabilities. The registry keeps it current via heartbeat.

---

## 3. Manifest Schema

### 3.1 Full Manifest

```yaml
manifest_version: "1.0.0-draft"
agent_id: "hermes-spfx-builder"
agent_type: "hermes"
fleet_id: "works-with-agents-fleet-1"

# What this agent can do
capabilities:
  - action: "build"
    target: "spfx"
    description: "Build and bundle SharePoint Framework web parts"
    tools_used: ["node", "gulp", "heft", "npm"]
    success_rate: 0.94
    avg_duration_seconds: 180
    max_concurrent: 3
    
  - action: "deploy"
    target: "sharepoint"
    description: "Deploy SPFx packages to SharePoint app catalog"
    tools_used: ["m365-cli", "pnppm"]
    success_rate: 0.87
    avg_duration_seconds: 45
    max_concurrent: 1
    
  - action: "test"
    target: "spfx"
    description: "Run SPFx test suite"
    tools_used: ["jest", "gulp"]
    success_rate: 0.77
    avg_duration_seconds: 60
    max_concurrent: 5
    
  - action: "fix"
    target: "build"
    description: "Diagnose and fix build errors"
    tools_used: ["terminal", "search_files", "patch"]
    success_rate: 0.91
    avg_duration_seconds: 300
    max_concurrent: 2

# What this agent needs
resources:
  min_tokens_per_task: 5000
  max_tokens_per_task: 100000
  preferred_model: "qwen2.5-8b-oq4"
  required_tools: ["terminal", "file", "search"]
  required_skills: ["spfx-local", "spfx-heft-build-breakfix"]

# How to reach this agent
endpoint:
  protocol: "acp"              # Agent Coordination Protocol
  address: "agent://spfx-builder.internal:8782"
  health_check: "agent://spfx-builder.internal:8782/health"
  
# Current status
status:
  state: "healthy"            # healthy | degraded | busy | stuck | offline
  load: 0.67                  # 0.0 to 1.0
  current_tasks: 2
  max_tasks: 3
  uptime_seconds: 86400
  last_heartbeat: "2026-05-05T21:00:00Z"
  trust_score: 0.92           # 0.0 to 1.0 — see Agent Trust Framework

# Performance history (rolling 7-day window)
metrics:
  tasks_completed: 147
  tasks_failed: 9
  avg_completion_seconds: 195
  pitfalls_reported: 3
  skills_published: 2
  peer_rating: 4.2            # 1.0 to 5.0 — from other agents
```

### 3.2 Minimal Manifest

For simple agents, only `agent_id` and `capabilities` are required:

```yaml
manifest_version: "1.0.0-draft"
agent_id: "hermes-research-basic"
capabilities:
  - action: "research"
    target: "general"
    success_rate: 0.85
```

---

## 4. Discovery Flow

```
1. Agent A starts → publishes manifest to registry
2. Agent A sends heartbeat every 30s → updates status.load, status.current_tasks
3. Orchestrator needs "build spfx" capability
4. Orchestrator queries registry → returns [Agent A (0.94 success, 0.67 load), Agent C (0.82, 0.10)]
5. Orchestrator selects Agent C (lower load, acceptable success rate)
6. Orchestrator delegates task to Agent C via Layer 5 Coordination Protocol
7. Agent C completes task → registry updates metrics
```

---

## 5. Registry API

### 5.1 Register Agent

```
POST /v1/agents/register
Body: Full Capability Manifest YAML
Response: 201 Created + agent_id
```

### 5.2 Query by Capability

```
GET /v1/agents?action=build&target=spfx
Response:
{
  "agents": [...],
  "count": 2,
  "recommended": "hermes-spfx-builder"  // highest success + lowest load
}
```

### 5.3 Update Status (via Heartbeat)

```
POST /v1/agents/{agent_id}/heartbeat
Body: Heartbeat payload (load, current_tasks, status)
Response: 200 OK
```

### 5.4 Deregister

```
DELETE /v1/agents/{agent_id}
Response: 204 No Content
// Automatic after 3 missed heartbeats (90s)
```

---

## 6. Trust Score Calculation

The `trust_score` (0.0 to 1.0) is computed from:

| Signal | Weight | Source |
|--------|--------|--------|
| Task success rate | 30% | Capability metrics |
| Pitfall contribution count | 20% | Pitfall Registry |
| Skill quality (reuse count) | 20% | Skill Registry |
| Peer rating | 15% | Agent-to-agent feedback |
| Uptime consistency | 15% | Heartbeat history |

**Formula:**
```
trust_score = 0.30 × success_rate 
            + 0.20 × min(pitfalls_reported / 10, 1.0)
            + 0.20 × min(skills_published / 5, 1.0)
            + 0.15 × (peer_rating / 5.0)
            + 0.15 × uptime_percentage
```

---

## 7. Relationship to Other Layers

| Layer | How Capability Manifest is used |
|-------|-------------------------------|
| L2 (Communication) | Manifest includes endpoint address for messaging |
| L4 (Session) | Not directly used — handoff is capability-agnostic |
| L5 (Coordination) | Work distribution uses capability matching + load + trust |
| L6 (Verification) | Success rate in manifest is updated by verification results |
| L7 (Governance) | Trust score may gate which agents can handle regulated tasks |

---

## 8. Status & Roadmap

| Component | Status |
|-----------|--------|
| Manifest schema | Draft 1.0.0 |
| Registry API | Spec written, not yet implemented |
| Trust score algorithm | Draft |
| Reference client library | Not yet built |
| Agent Registry on workswithagents.dev | Planned |

**Next:** Build the Agent Registry API on workswithagents.dev. Minimal: register, query, heartbeat, deregister.

---

*This document is part of the Agent OSI Model framework. See Layer 5 (Coordination Protocol) for how manifests are used in work distribution.*
