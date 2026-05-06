# Agent Coordination Protocol (ACP) — Layer 5

**Version:** 1.0.0-draft
**Status:** Specification
**Layer:** 5 — Coordination (Agent OSI Model)
**License:** CC BY 4.0

---

## 1. Purpose

The Agent Coordination Protocol defines how multiple AI agents work together simultaneously. It handles four concerns:

1. **Leader Election** — which agent coordinates the fleet?
2. **Work Distribution** — which agent gets which task?
3. **Conflict Resolution** — when agents disagree, who wins?
4. **Liveness** — is this agent still alive?

---

## 2. Design Principles

- **Eventual consistency over strong consistency.** Agents operate in different sessions with different context windows. Perfect real-time consensus is impossible. Good-enough coordination with recovery is achievable.
- **Push, don't poll.** Agents notify each other of state changes. No polling loops burning tokens.
- **Graceful degradation.** If the coordinator dies, the fleet continues with reduced coordination. No single point of failure that halts all work.
- **Agent-agnostic.** Works with any agent framework (Hermes, Claude Code, Codex, Copilot). No framework-specific dependencies.
- **Minimal overhead.** Coordination messages are small (under 500 tokens). The protocol doesn't burn the context it's trying to save.

---

## 3. Protocol Components

### 3.1 Leader Election

**Problem:** When multiple agents can make coordination decisions, who's in charge? Without a leader, agents either duplicate work or deadlock waiting for decisions.

**Design:** Raft-inspired but simplified. No log replication — just leadership.

```
State: LEADER | FOLLOWER | CANDIDATE

Heartbeat interval: 30s
Election timeout: 60-90s (randomized per agent to prevent split votes)
Leader lease: 120s (leader must refresh via heartbeat)

Flow:
1. FOLLOWER → No heartbeat for election_timeout → becomes CANDIDATE
2. CANDIDATE → Broadcasts "elect me" → 
   a. Receives majority votes → becomes LEADER
   b. Receives heartbeat from another leader → becomes FOLLOWER
   c. Timeout with no majority → new election
3. LEADER → Sends heartbeat every 30s → 
   Followers reset their election timeout on each heartbeat
```

**Leader responsibilities:**
- Maintain work queue and agent status
- Assign tasks to agents
- Resolve conflicts when agents disagree
- Detect dead/stuck agents

**What the leader does NOT do:**
- Execute other agents' tasks
- Override L6 verification or L7 governance
- Own shared resources (locking is separate)

**Leader failure:** If the leader dies, followers detect heartbeat timeout (60-90s) and trigger a new election. During the election gap, agents continue executing assigned tasks but new assignments pause. Maximum coordination downtime: ~90 seconds.

### 3.2 Work Distribution

**Problem:** A task arrives. Which agent handles it?

**Design:** Capability-weighted work queue with work stealing.

```
Task lifecycle:
1. SUBMITTED — task created, not yet assigned
2. ASSIGNED — assigned to a specific agent
3. IN_PROGRESS — agent acknowledged and started working
4. COMPLETED — agent finished successfully
5. FAILED — agent reported failure
6. TIMED_OUT — agent didn't respond within deadline
7. STOLEN — another agent took over after timeout
```

**Assignment algorithm:**
```
Input: Task with required capabilities
Output: Agent ID or null (no capable agent available)

1. Filter agents by:
   a. Capability match (agent can do this type of work)
   b. Health (agent is alive and responsive)
   c. Load (agent has capacity — not at max_concurrent_tasks)

2. Rank remaining agents by:
   a. Success rate for this capability (higher = better)
   b. Current load (lower = better)
   c. Trust score (higher = better, from Layer 3 discovery)

3. Assign to top-ranked agent

4. If no agent available → queue task, retry on next agent heartbeat
```

**Work stealing:**
```
When: Agent A is idle (no tasks in queue)
Action: Agent A queries registry for overloaded agents (load > 80%)
Target: Steals the oldest pending task from the most overloaded agent
Constraint: Agent A must have matching capabilities for the stolen task
```

### 3.3 Conflict Resolution

**Problem:** Two agents make conflicting decisions about the same resource. Agent A writes to file X. Agent B writes to file X at the same time. Who wins?

**Design:** Last-write-wins with audit trail. Conflicts are rare. Perfect resolution is expensive. Logging the conflict is mandatory.

```
Conflict types and resolution:

FILE CONFLICT (two agents write to same file):
  Last write wins. Both writes logged.
  Previous version preserved in .agent-conflicts/ directory.
  Alert raised if file differs by >10% (possible corruption).

DECISION CONFLICT (two agents disagree on approach):
  If leader exists → leader decides.
  If no leader → first decision wins, second is logged as dissent.
  Dissent logged to audit trail for human review.

RESOURCE CONFLICT (two agents claim same resource):
  Leader arbitrates → assigns to agent with higher trust score.
  If no leader → first claim wins, second is queued.
  Resource released after task completes or timeout.

DEPENDENCY CONFLICT (Agent B starts before Agent A finishes):
  Agent B detects dependency unmet → waits or steals.
  If deadline would be missed → escalates to leader.
  Leader may reassign or extend deadline.
```

### 3.4 Liveness & Heartbeat

**Problem:** How does the fleet know an agent is still working?

**Design:** Heartbeat with grace period.

```
Heartbeat payload:
{
  "agent_id": "hermes-spfx-builder",
  "status": "healthy",          // healthy | degraded | busy | stuck
  "load": 0.67,                 // 0.0 to 1.0
  "current_tasks": ["task-42"],
  "last_completed": "task-41",
  "token_budget_remaining": 35000,
  "timestamp": "2026-05-05T21:00:00Z"
}

Heartbeat interval: 30s
Missed heartbeat threshold: 3 consecutive (90s)
Missed heartbeat action:
  1. Mark agent as "unresponsive"
  2. Reassign its IN_PROGRESS tasks (work stealing)
  3. Alert via Cron Guard
  4. If agent returns → reconcile state (agent reports what it actually completed)
```

---

## 4. Protocol Schema

### 4.1 Heartbeat Message

```yaml
acp_version: "1.0.0-draft"
message_type: "heartbeat"
agent_id: "hermes-spfx-builder"
fleet_id: "works-with-agents-fleet-1"
timestamp: "2026-05-05T21:00:00Z"
status: "healthy"
load: 0.67
current_tasks:
  - id: "task-42"
    status: "IN_PROGRESS"
    started_at: "2026-05-05T20:55:00Z"
    deadline: "2026-05-05T21:10:00Z"
capabilities:
  - action: "build"
    target: "spfx"
    success_rate: 0.94
token_budget_remaining: 35000
```

### 4.2 Task Assignment

```yaml
acp_version: "1.0.0-draft"
message_type: "task_assign"
task_id: "task-43"
from_agent: "hermes-leader"
to_agent: "hermes-spfx-builder"
task:
  action: "build"
  target: "spfx"
  description: "Build web part 'ProjectDashboard' from source"
  context:
    repo: "/Users/vilius/origami-spfx-webparts-lab"
    branch: "feature/project-dashboard"
  deadline: "2026-05-05T21:30:00Z"
  priority: "normal"            # low | normal | high | critical
  idempotency_key: "task-43-v1"
```

### 4.3 Leader Election

```yaml
acp_version: "1.0.0-draft"
message_type: "election_request"
candidate_id: "hermes-leader"
fleet_id: "works-with-agents-fleet-1"
term: 7                        # monotonically increasing
timestamp: "2026-05-05T21:00:00Z"
```

### 4.4 Work Steal

```yaml
acp_version: "1.0.0-draft"
message_type: "work_steal"
from_agent: "hermes-idle-worker"
from_agent_load: 0.0
target_agent: "hermes-spfx-builder"
target_agent_load: 0.95
stolen_tasks: ["task-42"]
timestamp: "2026-05-05T21:00:00Z"
```

---

## 5. Registry Dependencies

The Coordination Protocol depends on Layer 3 (Discovery):

- **Agent Capability Manifest** — needed to match tasks to capable agents
- **Agent Registry** — needed to know which agents exist and their status
- **Heartbeat** — serves both L3 (status broadcast) and L5 (liveness check)

---

## 6. Implementation Notes

### Minimum viable implementation

For a small fleet (2-5 agents), you don't need full leader election with Raft-style consensus. A simpler model works:

1. **Static leader** — designate one agent as coordinator in config
2. **Direct assignment** — leader assigns tasks, no work stealing needed
3. **Heartbeat-only liveness** — if an agent misses 3 heartbeats, leader reassigns
4. **Manual conflict resolution** — conflicts are rare with small fleets; log and alert

Upgrade to full protocol when fleet exceeds 5 agents or when coordination downtime becomes expensive.

### Coordination Registry

The protocol requires a shared state store accessible to all agents. Options:

| Store | Pros | Cons |
|-------|------|------|
| SQLite + WAL (shared filesystem) | Zero setup, fast | Single machine only |
| FactBase API (workswithagents.dev) | Network-accessible, queryable | Adds latency |
| Redis | Battle-tested, pub/sub | Additional infrastructure |
| Custom HTTP API | Tailored to ACP | Build effort |

Recommended: SQLite+WAL for local fleets, FactBase API for distributed fleets.

---

## 7. Status & Roadmap

| Component | Status |
|-----------|--------|
| Protocol spec | Draft 1.0.0 |
| Reference implementation | Not yet built |
| Leader election | Spec complete |
| Work distribution | Spec complete |
| Conflict resolution | Spec complete |
| Liveness / heartbeat | Spec complete |
| Work stealing | Spec complete |
| Registry integration | Depends on L3 Agent Registry |

**Next:** Reference implementation in Python for Hermes agent fleet. Target: 2-3 weeks.

---

*This document is part of the Agent OSI Model framework. See Layer 3 (Agent Capability Manifest) for the discovery mechanism this protocol depends on.*
