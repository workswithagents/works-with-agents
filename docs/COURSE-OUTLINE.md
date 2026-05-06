# Works With Agents — Course Outline

**The Missing Manual for Working with AI Agents**

10 modules. Self-paced. Free and open. Each module includes vocabulary, curated resources, and hands-on exercises. No login required.

---

## Phase 1: Foundation (Modules 1–3)

### Module 1: Boot
The first session. Minimum viable agent configuration. What must be in place before session 2.

**Vocabulary:** AGENTS.md, system prompt, environment config, initial memory

**Resources:** Boot skill reference, Methodology overview, Knowledge Platform llms.txt

**Learn:**
- AGENTS.md — your agent's source of truth
- Environment configuration that sticks
- Initial memory: what the agent needs to know before it starts

### Module 2: Skills — Knowledge That Compounds
Reusable procedural knowledge. Build once, load on demand.

**Vocabulary:** skill, skill library, trigger keyword, skill authoring

**Resources:** Skill Registry, Skill specification, Example skills (spfx-local, systematic-debugging)

**Learn:**
- Creating your first reusable skill
- When to load vs. when to skip
- Skill library organisation for teams

### Module 3: Memory — The Agent That Remembers
Durable context across sessions. Never re-explain.

**Vocabulary:** session memory, durable memory, fact, memory compaction, Honcho

**Resources:** FactBase API, Memory architecture spec, Memory pattern

**Learn:**
- Session memory vs. durable memory
- What to save and what to let go
- Memory architecture: facts, preferences, corrections
- Search and retrieval patterns

---

## Phase 2: Autonomy (Modules 4–5)

### Module 4: Decision Protocols — Autonomy Without Chaos
Rules your agent follows. No approval bottlenecks.

**Vocabulary:** decision protocol, micromanagement trap, trust calibration, destructive guard

**Resources:** Decision Protocols spec, Decision protocol pitfalls, Blueprint Registry

**Learn:**
- The micromanagement trap
- Writing effective decision rules
- When to ask vs. when to decide
- Trust calibration: start tight, loosen over time

### Module 5: Tool Composition — The Right Instrument
Tool selection is the difference between 30 seconds and 15 minutes.

**Vocabulary:** tool set, tool misuse, delegation, tool budget

**Resources:** Tool Composition spec, Spike skill, Agentic Delegation skill

**Learn:**
- Terminal vs. file operations vs. delegation — when to use which
- Avoiding tool misuse patterns
- Building the right defaults
- Custom tool configuration

---

## Phase 3: Scale (Modules 6–7)

### Module 6: Orchestration — Multi-Agent Workflows
Complex work split across specialist agents working in parallel.

**Vocabulary:** orchestrator, specialist agent, parallel delegation, handoff, agent mesh

**Resources:** Orchestration spec, Agent Orchestrator skill, Agent State DB skill, Bastion Gateway

**Learn:**
- When one agent isn't enough
- Role-based agent design (researcher, builder, reviewer)
- Parallel vs. sequential delegation
- Managing agent communication and handoffs

### Module 7: Pipelines — Agents That Run While You Sleep
Scheduled, event-driven, unattended execution.

**Vocabulary:** cron job, pipeline composition, watchdog, webhook trigger, delivery target

**Resources:** Pipelines spec, Cron Guard skill, Integration Tracker skill, Kanban Orchestrator skill

**Learn:**
- Cron jobs: time-based agent execution
- Build pipelines: from change to deployed
- Monitoring: health checks, alerts, dashboards
- Pipeline composition: chaining agents together

---

## Phase 4: Harden (Modules 8–10)

### Module 8: Resilience — Failure Recovery Without Humans
The agent finds another way.

**Vocabulary:** exponential backoff, circuit breaker, transient error, permanent error, self-healing

**Resources:** Resilience spec, Model Fallback skill, Cron Guard skill, Pitfall Registry

**Learn:**
- Why agents fail and what to do about it
- Retry strategies: exponential backoff, circuit breakers
- Error categorisation: transient vs. permanent
- Self-healing: when the agent fixes its own mistakes

### Module 9: Verify — Trust but Verify
Automated gates + human review. What tests catch and what they miss.

**Vocabulary:** quality gate, syntax gate, visual QA, review cadence, false positive

**Resources:** Verify spec, Screenshot After Changes skill, Pre-Commit Review skill, Project Audit skill

**Learn:**
- Automated testing after every action
- Syntax checking, linting, type checking
- Visual QA for UI changes
- Human review cadence: what to look for, when to intervene

### Module 10: Compounding — Agents That Get Better
The feedback loop. Discoveries become skills. Skills compound.

**Vocabulary:** compounding loop, discovery, skill library growth, compounding maths

**Resources:** Compounding spec, Agent Self-Improver skill, Post-Task Capture skill, FactBase

**Learn:**
- Saving successful approaches as reusable skills
- Pattern recognition across sessions and projects
- Building a learning organisation with agents
- The compounding maths: 1% better each session

---

## Bonus Modules

### B1: Compliance & Security
Enterprise-grade agent infrastructure.

**Vocabulary:** audit trail, credential proxy, air-gapped deployment, regulated workflow, RBAC

**Resources:** Compliance spec, Credential Proxy skill

**Content:** Credential handling, audit trails, regulated workflows (GDPR, NHS DSP, FCA), air-gapped deployments.

### B2: Local-First Agents
On-prem LLMs. Zero cloud dependency.

**Vocabulary:** quantization, GGUF, context window, tokens-per-second, MLX, hardware matching

**Resources:** Blueprint Registry, Bonsai Local Agent skill

**Content:** Hardware matching, local inference setup (oMLX, llama.cpp), context window trade-offs, when local beats cloud.

---

## Access

Free and open. No login. No paywall. Start at https://workswithagents.com/learn.html

- **10 modules** with vocabulary, resources, and exercises
- **2 bonus modules** for enterprise and local-first
- **Agent-readable** at https://workswithagents.dev/llms.txt
- **Newsletter** for updates: https://workswithagents.com/newsletter.html
