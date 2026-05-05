# The Agent OSI Model — A Layered Architecture for AI Agent Infrastructure

**Version:** 1.0.0
**Status:** Published
**Author:** Works With Agents (Vilius Vystartas)
**License:** CC BY 4.0 — Free to use, cite, and build upon. Attribution required.

---

## Why This Exists

The OSI model didn't create networking. It created the **vocabulary** that made networking a discipline. Before OSI, engineers said "the connection is broken" — after OSI, they said "Layer 2 link is down." Precision replaced ambiguity. Debugging became systematic.

AI agents have no equivalent.

When an agent fails today, we say "the agent broke." That's useless. Did its model crash (Layer 1)? Did it lose auth (Layer 2)? Did it hand off corrupted state (Layer 4)? Did two agents conflict over a file (Layer 5)? Did it violate a compliance rule (Layer 7)?

This model gives the agent ecosystem a shared language. Each layer has one clear responsibility. Each layer has a defined interface to the layers above and below. Problems can be isolated. Solutions can be targeted. Infrastructure can be built to address specific layers.

**This is a framework document, not a standard.** It describes what exists and what's missing. It's designed to be understood by both AI agents (machine-readable structure, served via llms.txt) and humans (clear naming, concrete examples).

---

## The Seven Layers

```
┌─────────────────────────────────────────────────┐
│ L7  GOVERNANCE    Audit · Compliance · Sign-off  │  ← "Is this safe?"
├─────────────────────────────────────────────────┤
│ L6  VERIFICATION  Testing · Evaluation · Gates   │  ← "Does this work?"
├─────────────────────────────────────────────────┤
│ L5  COORDINATION  Consensus · Distribution ·     │
│                   Conflict Resolution            │  ← "How do agents work together?"
├─────────────────────────────────────────────────┤
│ L4  SESSION       Handoff · State · Context      │  ← "How does an agent continue?"
├─────────────────────────────────────────────────┤
│ L3  DISCOVERY     Registry · Capabilities ·      │
│                   Service Location               │  ← "How do agents find each other?"
├─────────────────────────────────────────────────┤
│ L2  COMMUNICATION Messaging · Auth · API         │  ← "How do agents talk?"
├─────────────────────────────────────────────────┤
│ L1  EXECUTION     Hardware · Runtime · Tools     │  ← "What runs the agent?"
└─────────────────────────────────────────────────┘
```

---

## Layer 1 — Execution

**Responsibility:** What runs the agent. Hardware, model runtime, and tool execution environment.

**Boundary:** Layer 1 provides compute. Layer 2 uses it. Layer 1 doesn't know about messaging — it just runs.

**What's in this layer:**
- Hardware specifications (RAM, GPU, disk)
- Model runtime (oMLX, llama.cpp, vLLM)
- Model configuration (quantization, context length, temperature)
- Tool execution sandbox (terminal, file I/O, browser)

**What's NOT in this layer:**
- How agents communicate (→ L2)
- Which agent does what (→ L5)
- Whether the model's output is correct (→ L6)

**Infrastructure:** Blueprint Registry (workswithagents.io) — verified LLM configurations matched to specific hardware. "This Qwen2.5-8B model in Q4 quantization on an M4 Mac with 24GB RAM gets 22 tokens/sec. Verified."

**Interface to L2:** Layer 1 provides a running agent process. Layer 2 provides communication channels for that process.

---

## Layer 2 — Communication

**Responsibility:** How agents talk to each other and to external services. Messaging protocol, authentication, and API contracts.

**Boundary:** Layer 2 moves messages. Layer 3 decides who to send them to. Layer 2 doesn't know about service discovery — it just delivers.

**What's in this layer:**
- Agent-to-agent messaging (A2A, MCP, WebSocket, gRPC)
- Authentication and authorization (API keys, OAuth, credential management)
- API contracts (OpenAPI 3.1, JSON Schema)
- Transport security (TLS 1.3, mTLS)

**What's NOT in this layer:**
- Finding services to talk to (→ L3)
- What to say or when (→ L5)
- Whether the message content is compliant (→ L7)

**Infrastructure:**
- Credential Proxy — agent-safe credential store (no Touch ID, works from cron)
- A2A Protocol — Google's Agent-to-Agent communication
- MCP — Anthropic's Model Context Protocol for tool calling
- OpenAPI 3.1 — machine-readable API contracts

**Interface to L3:** Layer 2 provides authenticated channels. Layer 3 provides the addresses.

---

## Layer 3 — Discovery

**Responsibility:** How agents find each other and find services. Registry, capability advertisement, and service location.

**Boundary:** Layer 3 maps names to addresses. Layer 4 uses those addresses to establish sessions. Layer 3 doesn't maintain state — it just provides location.

**What's in this layer:**
- Agent capability manifest (what can this agent do?)
- Service registry (where is the FactBase? Where is the build server?)
- Skill discovery (what skills exist for this task?)
- Documentation discovery (llms.txt, OpenAPI specs)
- Health/status broadcast (is this agent alive? What's its load?)

**What's NOT in this layer:**
- Actually sending messages (→ L2)
- Maintaining session state (→ L4)
- Deciding who does what (→ L5)

**Infrastructure:**
- llms.txt / llms-full.txt — documentation discovery (llmstxt.org standard)
- OpenAPI 3.1 specs — API contract discovery
- Agent Capability Manifest — **NEW** (defined below). Machine-readable declaration of agent capabilities.
- Agent Registry — **PLANNED**. Live directory of running agents and their capabilities.

**Interface to L4:** Layer 3 provides a target agent's address and capabilities. Layer 4 establishes a session with that target.

---

## Layer 4 — Session

**Responsibility:** How an agent's work continues across time boundaries. State transfer, context preservation, and handoff between sessions.

**Boundary:** Layer 4 preserves state when an agent stops. Layer 5 coordinates agents that are running simultaneously. Layer 4 handles *sequential* continuity; Layer 5 handles *parallel* coordination.

**What's in this layer:**
- Session state serialization (what was done, what remains)
- Context preservation (decisions made, assumptions held, pitfalls hit)
- Handoff protocol (structured YAML for agent-to-agent transfer)
- Session resumption (next agent picks up where previous left off)
- Checkpointing (save point for long-running tasks)

**What's NOT in this layer:**
- Agents running at the same time (→ L5)
- Whether the handoff content is correct (→ L6)
- Whether the handoff is compliant (→ L7)

**Infrastructure:**
- Handoff Protocol — structured state transfer between agent sessions. Baseline + Regulated variants. Submitted as extension proposals to MCP (SEP) and Google A2A.
- Context Packer — compresses 2,500-file repos into 8-file context packs for session transfer.

**Interface to L5:** Layer 4 provides a clean session state. Layer 5 uses that state to coordinate parallel work.

---

## Layer 5 — Coordination

**Responsibility:** How agents work together simultaneously. Work distribution, consensus, conflict resolution, and leader election.

**Boundary:** Layer 5 orchestrates the "who does what when." Layer 6 verifies the results. Layer 5 doesn't evaluate quality — it just assigns work.

**What's in this layer:**
- Leader election (which agent coordinates the fleet?)
- Work distribution (which agent gets which task?)
- Work stealing (idle agents pull from busy agents' queues)
- Dependency management (Agent B waits for Agent A's output)
- Conflict resolution (two agents disagree — who wins?)
- Heartbeat / liveness (is this agent still alive?)

**What's NOT in this layer:**
- Whether the work was done correctly (→ L6)
- Whether the work is compliant (→ L7)
- Agent identity or trust (Layer 3 provides identity; Layer 7 evaluates trust)

**Infrastructure:**
- Coordination Protocol — **NEW** (defined below). Leader election, work distribution, conflict resolution for agent fleets.
- Cron Guard — detects when 3+ consecutive cron runs fail. Smoke alarm for the fleet.

**Interface to L6:** Layer 5 delivers completed work. Layer 6 verifies it.

---

## Layer 6 — Verification

**Responsibility:** Whether agent output is correct. Testing, evaluation, quality gates, and regression detection.

**Boundary:** Layer 6 checks quality. Layer 7 checks compliance. A correct answer can still be non-compliant — and vice versa. Layer 6 handles "does it work?" — Layer 7 handles "is it allowed?"

**What's in this layer:**
- Automated testing (unit, integration, end-to-end)
- Agent evaluation (did the agent route correctly? Did it use the right tool?)
- Quality gates (syntax check, lint, type check after every change)
- Regression detection (did the new prompt make things worse?)
- Performance benchmarks (tokens/sec, success rate, latency)

**What's NOT in this layer:**
- Compliance checks (→ L7)
- Who runs the tests (→ L5)
- How test results are communicated (→ L2)

**Infrastructure:**
- Agent Test Suite — 7-test harness for L3 Certified products (discovery, auth, CRUD, error, rate limit, pitfall, skill)
- Quality Gates — syntax check after every file write, test suite after every code change
- Pitfall Registry — shared bug database. Bugs found by one agent, learned by all.

**Interface to L7:** Layer 6 provides verification results. Layer 7 evaluates those results against compliance rules.

---

## Layer 7 — Governance

**Responsibility:** Whether agent actions are safe, compliant, and auditable. Regulatory alignment, sign-off gates, and accountability.

**Boundary:** Layer 7 is the final gate. Nothing reaches production without passing Layer 7 in regulated environments. In unregulated environments, Layer 7 may be minimal or absent.

**What's in this layer:**
- Audit trail (every agent action logged, attributed, queryable)
- Compliance rules (DTAC, FCA, GDS, GDPR, SOC 2 as executable checks)
- Sign-off gates (human approval required for compliance-sensitive actions)
- Data classification (public, internal, confidential, restricted)
- Accountability (which human is responsible for this agent's decisions?)
- Regulatory reporting (automated evidence generation for assessments)

**What's NOT in this layer:**
- Whether the agent works correctly (→ L6)
- How agents coordinate (→ L5)
- Infrastructure health (→ L1-4)

**Infrastructure:**
- Regulated Handoff Protocol — compliance fields added to baseline Handoff: audit trail, sign-off gates, data classification, regulator references
- Compliance-as-Code — **PLANNED**. Machine-readable compliance rules that agents validate against. DTAC, FCA, GDS as executable checks.
- Agent Transaction Protocol — **NEW** (defined below). Idempotency, attribution, rollback for agent actions.

**Interface to the world:** Layer 7 is the boundary between the agent system and the regulatory environment. It translates agent actions into compliance evidence.

---

## How to Use This Model

### For debugging

| Symptom | Layer to check |
|---------|---------------|
| Agent won't start | L1 (runtime, hardware) |
| Agent can't authenticate | L2 (auth, tokens) |
| Agent can't find a service | L3 (discovery, registry) |
| Agent lost context after restart | L4 (handoff, state) |
| Two agents overwrote the same file | L5 (coordination, locking) |
| Agent produces wrong output | L6 (verification, testing) |
| Compliance officer blocked deployment | L7 (governance, audit) |

### For infrastructure building

Don't build everything at once. Target specific layers:

| If you're building... | Focus on... |
|----------------------|-------------|
| A local AI agent | L1 (runtime), L2 (auth), L4 (handoff) |
| A multi-agent fleet | + L3 (discovery), L5 (coordination) |
| An enterprise deployment | + L6 (verification), L7 (governance) |
| A regulated industry deployment | All 7 layers, with L7 as the hard requirement |

### For standards

This model helps identify where standards are needed. Each layer that lacks a standard is a gap — and an opportunity:

| Layer | Standard | Status |
|-------|----------|--------|
| L1 | Blueprint Registry (verified configs) | ✅ Live |
| L2 | MCP, A2A, OpenAPI 3.1 | ✅ Existing |
| L3 | llms.txt, Agent Capability Manifest | ✅ Live / **NEW** |
| L4 | Handoff Protocol | ✅ In proposal (MCP SEP #2683, A2A #1817) |
| L5 | Coordination Protocol | **NEW** — defined below |
| L6 | Agent Test Suite | ✅ Spec written |
| L7 | Regulated Handoff, Compliance-as-Code | ⚠️ Planned |

---

## Machine-Readable Format

This model is available as structured YAML for agent consumption:

```yaml
agent_osi_version: "1.0.0"
layers:
  - id: 1
    name: "Execution"
    responsibility: "Hardware, model runtime, tool execution"
    interface_up: "Provides running agent process"
    infrastructure: ["Blueprint Registry (workswithagents.io)"]
    status: "live"
  - id: 2
    name: "Communication"
    responsibility: "Agent messaging, authentication, API contracts"
    interface_up: "Provides authenticated channels"
    infrastructure: ["Credential Proxy", "MCP", "A2A", "OpenAPI 3.1"]
    status: "live"
  - id: 3
    name: "Discovery"
    responsibility: "Agent registry, capability advertisement, service location"
    interface_up: "Provides target agent address and capabilities"
    infrastructure: ["llms.txt", "Agent Capability Manifest", "Agent Registry (planned)"]
    status: "partial"
  - id: 4
    name: "Session"
    responsibility: "State transfer, context preservation, handoff between sessions"
    interface_up: "Provides clean session state"
    infrastructure: ["Handoff Protocol", "Context Packer"]
    status: "in_proposal"
  - id: 5
    name: "Coordination"
    responsibility: "Work distribution, consensus, conflict resolution, leader election"
    interface_up: "Provides completed work"
    infrastructure: ["Coordination Protocol (new)", "Cron Guard"]
    status: "spec_written"
  - id: 6
    name: "Verification"
    responsibility: "Testing, evaluation, quality gates, regression detection"
    interface_up: "Provides verification results"
    infrastructure: ["Agent Test Suite", "Pitfall Registry", "Quality Gates"]
    status: "partial"
  - id: 7
    name: "Governance"
    responsibility: "Audit, compliance, sign-off, regulatory alignment"
    interface_up: "Provides compliance evidence"
    infrastructure: ["Regulated Handoff Protocol", "Compliance-as-Code (planned)"]
    status: "planned"
```

---

## What This Model Is NOT

- **Not a protocol specification.** It describes layers. Individual protocols (Handoff, Coordination, etc.) are defined separately.
- **Not a product.** It's a framework. Works With Agents builds infrastructure for specific layers — but the model itself is free for anyone to use.
- **Not complete.** Layers 3, 5, 6, and 7 need more infrastructure. This document identifies gaps as much as it documents what exists.
- **Not OSI.** The original OSI model has 7 layers for networking. This model has 7 layers for agent infrastructure. The number is the same; the content is entirely different.

---

## Attribution & Reuse

This document is published under CC BY 4.0. Cite as:

> Vystartas, V. (2026). *The Agent OSI Model — A Layered Architecture for AI Agent Infrastructure.* Works With Agents. https://workswithagents.com/agent-osi-model

---

*Infrastructure specs for Layer 3 (Agent Capability Manifest), Layer 5 (Coordination Protocol), and Layer 7 (Agent Transaction Protocol) follow in companion documents.*
