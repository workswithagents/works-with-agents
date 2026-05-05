# Bastion — A Weekend with an AI Agent

**A solo developer spent 3 days hardening a development loop with an AI agent. 111 SPFx web parts were built experimentally. This is what was learned — not what was sold.**

---

## The Developer

Vilius Vystartas — SharePoint/M365 developer, Cardiff UK. One AI agent. One weekend. Goal: see how far an agent-assisted development loop could go in 72 hours.

## The Goal

Build as many SPFx web parts as possible, find the failure modes, and harden the loop. Not a product. An experiment.

## What Actually Happened

Instead of treating the agent as a code generator (prompt → code → copy-paste → fix → repeat), a systematic collaboration approach emerged:

### Before (prompt-and-pray)
- Write a prompt → get code → copy-paste → test → fix → repeat
- Agent forgets everything each session
- Every decision requires human approval
- One error = everything stops

### After (agentic loop)
- **Skills**: Reusable knowledge modules. Agent loads only what's relevant.
- **Memory**: Preferences, corrections, environment facts persisted across sessions.
- **Decision protocols**: Agent decides and executes — no approval bottlenecks.
- **Orchestration**: Complex tasks split into parallel workstreams with specialist sub-agents.
- **Pipelines**: Builds, tests run autonomously. Agent runs while you sleep.
- **Self-improvement**: Successful approaches saved as new skills, compounding.

## What Was Learned

| Discovery | Pattern |
|-----------|---------|
| Skills compound — each solved problem becomes a reusable module | Skills System |
| Memory prevents re-explaining project structure every session | Persistent Memory |
| "Proceed and don't stop" works better than gatekeeping every decision | Decision Protocols |
| Specialist agents (builder, reviewer, researcher) outperform one generalist | Orchestration |
| Cron jobs + health checks = agent runs while you sleep | Pipelines |
| Retry with backoff recovers from most failures without intervention | Resilience |
| Tests after every change catch regressions immediately | Quality Gates |
| Saving discoveries as skills creates a compounding loop | Compounding |

## What Didn't Work

- **Long sessions degrade.** Context pollution is real. Fresh sessions with compressed state work better.
- **Some failures need human judgment.** The loop can't fix everything. Knowing when to intervene is a skill.
- **Tools matter.** The right tool for the job (terminal vs file vs delegation) is the difference between a 30-second fix and a 15-minute dead end.

## The Real Product

The methodology that emerged — 10 patterns for working with AI agents — is what's teachable. Not the web parts. Not the services. The patterns repeat across any project, any agent, any domain.

---

*This was a learning experiment. 111 web parts were built, not shipped. The numbers demonstrate what the loop can do — not a production claim.*
