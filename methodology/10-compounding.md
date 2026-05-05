# Pattern 10: Compounding — Agents That Get Better Every Session

**Time to read:** 14 minutes  
**Time to apply:** Ongoing — this pattern emerges from the other 9  
**Prerequisites:** Patterns 1-9

---

## What This Pattern Is

Patterns 1-9 are techniques. Compounding is the system they create together. It's what happens when your agent:

- Boots with full project context (Pattern 1)
- Loads the right skill for the job (Pattern 2)
- Remembers your preferences and corrections (Pattern 3)
- Knows when to act and when to ask (Pattern 4)
- Uses the right tool for each task (Pattern 5)
- Orchestrates parallel work across specialists (Pattern 6)
- Runs pipelines while you're away (Pattern 7)
- Retries failures and self-heals (Pattern 8)
- Verifies every output before you see it (Pattern 9)

And then — this is the compounding part — saves what it learned so next session is better.

---

## The Feedback Loop

Every agent session produces three types of value:

1. **The task output** — the code, the research, the deployment. The visible result.
2. **The corrections** — things you fixed: "use python3.11," "tests are in tests/," "don't commit to main." These become memory (Pattern 3).
3. **The discoveries** — procedures that worked, errors that were fixed, patterns that emerged. These become skills (Pattern 2).

Most people only get the task output. The corrections and discoveries evaporate when the session ends. Compounding captures all three.

### The Loop in Action

```
Session 1: Agent sets up a new Python project. 45 minutes. 6 corrections.
  → Corrections saved to memory (Python path, test command, test directory)
  → Procedure saved as skill (python-project-bootstrap)

Session 2: Agent sets up a new Python project. Loads skill. Uses correct paths from memory. 10 minutes. 0 corrections.
  → Agent discovers a faster way to configure CI. Patches the skill.

Session 3: Agent sets up a new Python project. Updated skill. Still 10 minutes. 0 corrections.
  → Agent notices 3 errors that took 5 minutes to debug. Adds pitfalls to skill.

Session 12: Agent sets up a new Python project. Skill now has 8 steps, 6 pitfalls, CI config, and release checklist. 3 minutes. 0 errors. 0 corrections.
  → Sessions 2-12 each made the skill better. The 3-minute project setup is the accumulation of 12 sessions of improvements.
```

This is compounding. The task didn't change. The agent's capability did. Every session adds to the skill, the memory, and the protocols — and every future session benefits from every past improvement.

### The Compounding Maths

Conservative estimate: each session saves 1 piece of knowledge (a correction, a pitfall, a faster approach). That knowledge is available in every future session.

```
Month 1: 20 sessions × 1 saved discovery = 20 pieces of knowledge
Month 2: 20 sessions × 1 saved discovery = 20 more (40 total available)
Month 3: 20 sessions × 1 saved discovery = 20 more (60 total available)
```

After 5 months: 100 pieces of cumulative knowledge. The agent isn't starting from zero — it's starting from 100 things it already knows, and it adds one more every session.

This is why my skill library reached 153 in 5 months. Not through discipline — through compounding. Every session added something. Most additions were small (a single pitfall, a single trigger keyword). But they accumulated.

---

## The Compounding System

The 9 patterns create a system where compounding is automatic:

| Pattern | What it compounds | How |
|---------|------------------|-----|
| Boot | Project context | AGENTS.md stays current, agent always knows the environment |
| Skills | Procedures | Skills grow with new steps and pitfalls every use |
| Memory | Facts and preferences | Every correction added, never repeated |
| Decision Protocols | Trust and autonomy | Green zone expands as trust is earned |
| Tool Composition | Efficiency | Right tool choices become automatic |
| Orchestration | Throughput | Specialists get better at their domains |
| Pipelines | Automation | More pipelines = less manual triggers |
| Resilience | Reliability | Self-healing catalogue grows with each fixed error |
| Verify | Quality | Review feedback tightens protocols and skills |

Each pattern feeds the others. A correction (Memory) becomes a pitfall in a skill (Skills). A skill that handles a task reliably earns Green zone status (Decision Protocols). A Green zone task gets automated as a pipeline (Pipelines). The pipeline that self-heals (Resilience) and verifies its output (Verify) creates a fully autonomous workflow — and when it discovers a new edge case, it patches the skill, and the loop continues.

---

## What Compounding Looks Like Over Time

### Week 1
- Agent needs 6 corrections per session
- You explain every procedure
- Every session feels like starting over
- You wonder if this is actually faster

### Month 1
- Corrections down to 2 per session
- Agent loads skills for common tasks
- AGENTS.md provides project context automatically
- You notice sessions are faster but can't quantify it yet

### Month 2
- Corrections down to 0.5 per session
- Agent creates its own skills from discoveries
- Decision protocols mean agent proceeds without approval on most tasks
- You're getting more done in less time — measurable improvement

### Month 3
- Corrections: essentially zero
- Agent runs pipelines autonomously — you wake up to results
- Specialists handle domain-specific work without guidance
- Review time is the bottleneck, not agent capability

### Month 5
- 153 skills, 100+ memory entries, full autonomy protocols
- Agent handles 90% of routine work without intervention
- Your role shifts from operator to reviewer
- You spend more time deciding what to build than telling the agent how to build it

This isn't a projection — it's what actually happened building 111 SPFx web parts and 5 backend services over 5 months. The first month was slow. By month 3, the agent was doing more work than I was. By month 5, I was mostly reviewing, not building.

---

## Anti-Patterns That Kill Compounding

| Anti-pattern | What it does | Fix |
|-------------|-------------|-----|
| **"I'll document it later"** | Discovery lost. Next session, same problem. | Save immediately. 10 seconds now = 2 minutes later. |
| **Starting fresh every session** | All cumulative knowledge inaccessible | Boot, Memory, and Skills make knowledge persistent. Use them. |
| **Skipping the post-task patch** | Skill stays stale. Agent follows outdated procedure. | 60 seconds after every complex task: does the skill need updating? |
| **Not reviewing agent output** | Quality degrades slowly. Errors compound. | Pattern 9: review cadence keeps quality trending up. |
| **Treating agents as tools, not collaborators** | You do the thinking, agent does the typing. No compounding possible. | The agent can save its own discoveries if you let it. Encourage it. |

---

## Try It Now

1. **End your next session with this question:** "What did you learn in this session that should be saved?" The agent will list: corrections that should become memory, procedures that should become skills, pitfalls that should be patched.

2. **One save per session.** Every session, save at least one thing — a memory entry, a skill patch, a decision protocol update. At 20 sessions per month, that's 20 improvements per month.

3. **Look back after 2 weeks.** Compare your first sessions to now. Count the corrections. Measure the task completion time. The improvement is invisible day-to-day but undeniable over weeks.

**Time investment: 2 minutes per session to save what was learned. Return: exponential capability growth over months.**

---

## The 10 Patterns — Complete

You now have the full methodology. A quick review of every pattern and its role:

1. **Boot** — Project context the agent reads automatically
2. **Skills** — Reusable procedures loaded on demand
3. **Memory** — Durable facts, preferences, and corrections
4. **Decision Protocols** — Autonomy boundaries: what to do, what to ask
5. **Tool Composition** — Right tool for each job
6. **Orchestration** — Parallel work across specialist agents
7. **Pipelines** — Scheduled autonomous work
8. **Resilience** — Retry, self-heal, never quit on transient failures
9. **Verify** — Automated gates + human review
10. **Compounding** — The system: each session makes the next better

The patterns build on each other. Start with Boot and Skills. Add Memory and Protocols. Then Orchestration and Pipelines. Resilience and Verify complete the safety net. And Compounding — that's not a thing you implement. It's what happens when the other 9 are in place.

---

*Pattern 10 of 10. From the Works With Agents methodology — 111 SPFx web parts, 5 backend services, 153 skills, built over 5 months by one developer and an agent that got better every session.*
