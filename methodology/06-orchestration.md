# Pattern 6: Orchestration — Multi-Agent Workflows

**Time to read:** 14 minutes  
**Time to apply:** 30 minutes to set up first orchestration  
**Prerequisites:** Patterns 1-5, especially Tool Composition

---

## What Most People Do Wrong

They use one agent for everything. Code, research, review, deployment — all in a single conversation. The agent's context fills with intermediate outputs. Research results mix with code snippets. The agent slows down, makes more mistakes, and eventually hits context limits.

Orchestration is the solution: splitting complex work across specialist agents working in parallel, each with its own context window, each focused on one thing.

---

## The Pattern

### When to Orchestrate

Don't orchestrate everything. Single-agent work is faster for simple tasks. Orchestrate when:

- The work has 3+ independent streams (research A + build B + review C — no dependencies between them)
- A task would flood your main context with intermediate data (code review of a 500-line PR, deep research across 10 sources)
- You need different expertise for different parts (SPFx specialist + API specialist + DevOps specialist)
- The task is reasoning-heavy and would slow down your main workflow

### The Three-Agent Pattern

The most common orchestration pattern: three agents, three jobs, parallel execution.

```
Main Agent (you)
├── Research Agent  → "Research rate limiting strategies. Return structured comparison."
├── Review Agent    → "Review PR #47. Check for security issues, missing tests, API consistency."
└── Build Agent     → "Set up project skeleton: src/, tests/, pyproject.toml, CI config."
```

Each agent gets:
1. A **specific goal** — not "work on the project" but "implement rate limiting for the /v1/chat endpoint"
2. **Relevant context** — not the entire conversation, but the specific files, constraints, and conventions the agent needs
3. **The right tools** — research agents get `web_search`, review agents get `read_file` + `terminal`, build agents get the full toolkit

Results come back as summaries. You review, integrate, and move on.

### The Specialist Agent Pattern

Beyond parallel execution, orchestration enables specialists. A general agent can do anything adequately. A specialist agent with the right skills and tools does one thing exceptionally well.

Example specialists from actual usage:

| Specialist | Role | Skills loaded | Typical task |
|-----------|------|---------------|--------------|
| SPFx Builder | SharePoint Framework web parts | `spfx-local`, `spfx-heft-build-breakfix` | Scaffold, build, fix, test web parts |
| Code Reviewer | Quality gates | `requesting-code-review`, `systematic-debugging` | Review PRs for security, tests, conventions |
| Researcher | Deep market/technical research | Deep web search, source analysis | Competitor analysis, technology evaluation |
| Documentator | User guides, API docs | Context gathering, doc templates | Generate README, API reference, getting-started |
| Debugger | Root cause analysis | `systematic-debugging`, `python-debugpy` | Diagnose build failures, trace bugs to source |

The key: each specialist has access to skills the general agent doesn't. The SPFx specialist loads `spfx-heft-build-breakfix` with all 6 known failure modes and their fixes. A general agent would diagnose from scratch every time.

### Context Packing

The biggest orchestration mistake: sending too little context. An agent that doesn't know your project structure, conventions, or constraints will invent its own — and get everything wrong.

Good context packing:
```
Goal: Review PR #47 for security issues and test coverage.
Context: Project uses FastAPI + SQLite. Tests in tests/ with pytest.
Conventions: Run tests with `python3.11 -m pytest -n 4 -v`. 
Key files: api/main.py, src/auth.py, tests/test_auth.py.
PR adds OAuth2 flow. Check: token validation, refresh mechanism, CSRF protection.
```

Bad context packing:
```
Goal: Review PR #47.
```

The difference: the first agent produces a review that matches your project. The second agent reviews against generic standards and misses project-specific issues entirely.

---

## Real Examples

### Parallel Build + Research

A real example from building the Knowledge Platform:

```
Task 1 (Research Agent): "Research FastAPI rate limiting libraries — slowapi, fastapi-limiter, custom middleware. Return comparison with pros/cons, token overhead, and production readiness."

Task 2 (Build Agent): "Create src/rate_limit.py with TokenBucket implementation. Follow existing patterns in api/main.py. Include type hints and docstrings."

Both run in parallel. Total time: 4 minutes (the longer of the two). Sequential: 8+ minutes.
```

### Specialist SPFx Workflow

```
Main Agent: "Build a SharePoint web part for employee directory."
→ Spawns SPFx Specialist with spfx-local skill
→ Specialist scaffolds, builds, fixes build errors using spfx-heft-build-breakfix
→ Returns: working web part file + build verification

Main Agent: "Review the web part for accessibility."
→ Spawns Code Reviewer with requesting-code-review skill
→ Reviewer checks: ARIA labels, keyboard navigation, colour contrast
→ Returns: 3 issues found, 2 suggestions
```

The main agent never touched SPFx specifics or accessibility standards — it orchestrated specialists who already have that expertise.

---

## Common Pitfalls

| Pitfall | What happens | Fix |
|---------|--------------|-----|
| **Orchestrating everything** | 2-minute task spawns 3 agents — slower than doing it directly | Orchestrate when 3+ independent streams or context-flooding risk |
| **Too little context** | Agent invents conventions, gets everything wrong | Pack the specific files, constraints, and conventions the agent needs |
| **Too much context** | Agent's context filled with irrelevant history | Only include what's relevant to the specific task |
| **No specialist skills** | General agent fumbles specialist tasks | Build specialists with focused skill sets for recurring complex tasks |
| **Waiting for unnecessary results** | Main workflow blocks on research that isn't needed yet | Fire research agents early, collect results later |
| **Micro-managing agents** | Reviewing every sub-agent step instead of the summary | Trust the agent. Review the output, not the process. |

---

## Try It Now

1. **Find a parallel opportunity.** Next time you have a research task + a build task that don't depend on each other — run them in parallel.
2. **Create one specialist.** What task do you delegate repeatedly? Build a skill for it. Load that skill on a specialist agent.
3. **Pack better context.** Next delegation, include: goal, stack, conventions, key files, specific constraints. Compare the output quality.

**Time investment: 5 minutes to set up parallel execution. Return: 2-3x throughput on multi-stream work.**

---

## What's Next

Pattern 7: **Pipelines** — Agents that run while you sleep. Cron jobs, scheduled builds, monitoring — zero human intervention. This is where agent work becomes infrastructure.

---

*Pattern 6 of 10. From the Works With Agents methodology.*
