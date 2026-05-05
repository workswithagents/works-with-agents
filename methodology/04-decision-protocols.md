# Pattern 4: Decision Protocols — Autonomy Without Chaos

**Time to read:** 14 minutes  
**Time to apply:** 20 minutes to write protocols, immediate payoff  
**Prerequisites:** Patterns 1, 2, 3 (Boot, Skills, Memory)

---

## What Most People Do Wrong

They either let the agent do anything — and get deployment scares, overwritten files, and broken builds. Or they micromanage every decision — and get approval fatigue, slow sessions, and an agent that's not an agent, just a slow CLI.

The middle ground is decision protocols: rules the agent follows about when to ask, when to proceed, and when to escalate.

Most people never write these down. They just react: "No, don't do that!" after the fact. This is exhausting and doesn't scale — the agent keeps making the same bad decisions because it has no written rules.

---

## What You'll Learn

- A tiered autonomy system: what the agent can do without asking, what needs approval, what needs escalation
- How to write decision rules that prevent disasters without creating bottlenecks
- Trust calibration: starting restrictive, loosening as the agent proves itself
- The "Proceed" protocol: when to let the agent run unattended

---

## The Pattern

### Tier 1: Green Zone — Proceed Without Asking

What the agent can do immediately, no questions asked:

- Run tests (`pytest`, `npm test`, etc.)
- Read files to understand the codebase
- Search for files or patterns in code
- Write new files (not overwrite existing ones)
- Commit to a feature branch (not main)
- Run linting and type checking
- Execute non-destructive shell commands (ls, git status, which, etc.)

Your green zone will be different. The key: these are actions where being wrong doesn't cause damage. Worst case: a file ends up in the wrong place, a test fails, a commit needs reverting. All recoverable.

### Tier 2: Amber Zone — Proceed But Report

What the agent can do but should tell you about:

- Modifying existing files with `patch` (targeted edits)
- Running commands that change system state (`pip install`, `npm install`)
- Creating pull requests
- Deploying to staging environments
- Running database migrations on dev databases

The agent proceeds — you don't have to approve every one — but you get a summary so you can spot-check. This is where the 10x speedup comes from: the agent does 90% of the work without blocking on you.

### Tier 3: Red Zone — Must Ask

What the agent must never do without explicit approval:

- Deploying to production
- Running destructive database operations (DROP, TRUNCATE, DELETE without WHERE)
- Sending emails, messages, or notifications to real users
- Posting to social media or public platforms
- Accessing production databases or production API keys
- Modifying payment, billing, or authentication systems
- Any action with regulatory consequences (finance, healthcare data)

These are the boundaries where a mistake isn't just a bad commit — it's a production incident, a compliance violation, or a customer-facing error.

### Writing Your Protocols

Save this to memory so the agent reads it every session:

```
Autonomy protocol:

GREEN (proceed without asking):
- Writing new files, running tests, linting, type checking
- Reading/searching files, exploring the codebase
- Committing to feature branches (never main)
- Non-destructive shell commands

AMBER (proceed but tell me):
- Modifying existing files with targeted edits
- Installing packages or changing dependencies
- Creating pull requests
- Deploying to staging

RED (must ask first):
- Deploying to production
- Destructive database operations
- External communications (email, messages, social)
- Modifying payments, billing, or auth
- Accessing production secrets or APIs
- Anything with regulatory/compliance impact

Special: When I say "Proceed" or "Don't stop until finished" —
elevate all AMBER + GREEN to full autonomy. Work through
everything without pausing. Only stop when done or I interrupt.
```

### The "Proceed" Protocol

This is the single highest-leverage protocol I use. It's a mode switch — one word flips the agent from "ask about everything" to "execute everything."

The memory entry:
```
When user says "Proceed" or "Don't stop until finished," work through all
remaining items without pausing for approval. Commit after each, run tests,
move to next. Only stop when done or user interrupts.
```

When I say "Proceed," the agent handles an entire multi-step build autonomously: create files → run tests → fix failures → commit → next task → repeat. I come back 15 minutes later to a completed feature with passing tests.

### Trust Calibration

Start restrictive. Loosen as confidence grows.

**Week 1:** Everything in Amber zone requires approval. You're learning the agent's judgment.  
**Week 2:** Move frequent, consistently-correct actions to Green. File reads, test runs, simple file writes.  
**Week 3:** Move reliable targeted edits to Amber. The agent's `patch` usage has been clean for 2 weeks.  
**Week 4:** Introduce "Proceed" for small, defined task lists. 3-5 items, all recoverable.  
**Month 2:** Proceed for any task list where all items are in Green/Amber zones.

The key: trust is earned, not granted. Every time the agent makes a good autonomous decision, your confidence increases. Every mistake resets the calibration — not all the way back, but you tighten the relevant zone.

---

## Real Examples

### Before Protocols

```
Me: "Add rate limiting to the LLM proxy."
Agent: *writes code* — good.
Agent: *runs tests* — good.
Agent: "Should I commit this?"
Me: "Yes."
Agent: *commits* — good.
Agent: "Should I deploy to production?"
Me: "NO. Never deploy without asking."
Agent: "Sorry. Should I create a PR?"
Me: "Yes."
Agent: *creates PR* — good.
Agent: "Should I merge?"
Me: "No, that needs review."
Agent: "Should I send an email to the team about the change?"
Me: "NO. Never send emails without asking."

8 interruptions. 4 "NO" corrections. Exhausting.
```

### After Protocols

```
Me: "Add rate limiting to the LLM proxy. Proceed."
Agent: *writes code, runs tests, commits to feature branch, opens PR* — complete.
Me: *comes back 15 minutes later, reviews PR, merges*
```

Zero interruptions. Zero corrections. Because the agent knew: commits go to feature branches, PRs are created automatically, never deploy, never email.

---

## Common Pitfalls

| Pitfall | What happens | Fix |
|---------|--------------|-----|
| **No protocols at all** | Agent asks about everything or assumes everything is fine — both bad | Write them down. Green/Amber/Red. Save to memory. |
| **Everything in Green** | Agent deploys to production without asking | Red zone must include deployment, external actions, destructive operations |
| **Everything in Red** | Agent can't write a file without approval — you're a bottleneck | Most file operations should be Green or Amber. The agent writes files hundreds of times per session. |
| **Protocols too vague** | "Be careful" — meaningless to an agent | Be specific. "Never deploy to production without explicit approval." |
| **No "Proceed" protocol** | Agent asks approval between every step of a multi-step task | Add the Proceed protocol. Single word unlocks full autonomy. |
| **Trust never calibrated** | Week 12, still asking about file writes | Revisit zones monthly. Move proven-safe actions to Green. |

---

## Try It Now

1. **Write your Green/Amber/Red zones.** Use the template above. Customise for your project — your Red zone might include customer data, your Amber zone might include database migrations.

2. **Save the Proceed protocol.** Copy the memory entry above. Customise if needed.

3. **Save to memory.** Both the tiered protocol and the Proceed protocol.

4. **Test in a session.** Give your agent a multi-step task. Say "Proceed." Watch what happens. If it stops to ask about something in Green — update your protocols. If it does something dangerous — tighten your Red zone.

**Time investment: 20 minutes. Return: hundreds of approval interruptions eliminated per month.**

---

## What's Next

Pattern 5: **Tool Composition** — Your agent has a toolbox: terminal commands, file operations, web searches, sub-agents. Using the wrong tool turns a 30-second task into a 15-minute ordeal. We'll go through the decision matrix for every tool type.

---

*Pattern 4 of 10. From the Works With Agents methodology.*
