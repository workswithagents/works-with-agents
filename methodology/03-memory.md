# Pattern 3: Memory — Never Re-Explain Yourself

**Time to read:** 16 minutes  
**Time to apply:** 30 minutes to set up, ongoing  
**Prerequisites:** Patterns 1 (Boot) and 2 (Skills)

---

## What Most People Do Wrong

They treat every session as a blank slate. The agent asks: "What Python version?" They answer. Next session: "What Python version?" Again. Session three: same question.

This isn't the agent being forgetful. It's the agent having no memory. You haven't given it any.

Here's what this looks like over time:

```
Week 1: 3 sessions — 3 times explaining Python path, test command, project structure
Week 2: 4 sessions — 4 times explaining the same things, plus 2 corrections about preferences
Week 3: You start pre-empting. "Before we start: python3.11, tests/ directory, don't commit to main."
Week 4: You write a sticky note on your monitor: "REMEMBER TO TELL AGENT THESE 6 THINGS"
```

That sticky note is memory. But it's in the wrong place — it should be in the agent.

By the end of this module, you'll have:

- An agent that remembers your preferences across every session
- Zero re-explanation of environment facts (Python version, paths, conventions)
- A system for saving correction-based knowledge immediately — not "I'll document that later"
- The ability to search across past sessions for what you solved before

---

## The Pattern

### What Memory Looks Like

Memory isn't a database. It's a text stream injected into every future session — the agent reads it before it reads your message. Think of it as a persistent preamble that grows over time.

Good memory entries:
```
Python: python3.11 at /opt/homebrew/bin/python3.11. pip3.11 at /opt/homebrew/lib/python3.11/site-packages.
User prefers concise responses, not verbose explanations.
Project uses pytest with xdist for parallel test runs: `pytest -n 4 -v`.
When user says "Proceed," work through all items without pausing for approval.
Never use vim/nano — use write_file for editing.
```

Bad memory entries:
```
We worked on the API yesterday. (Too vague — which API? What did we do?)
Task: finish the rate limiter. (Task progress — belongs in a session tracker, not memory)
The build failed and we fixed it. (What failed? What was the fix? Save it as a skill, not a memory.)
```

### The Memory Rules

Three rules for what goes into memory:

**1. Save corrections.** When you correct the agent, save the correction. *"No, use python3.11 not python3"* → memory entry: "Python: python3.11 at /opt/homebrew/bin/python3.11." The most valuable memory prevents you from having to correct the agent twice.

**2. Save preferences.** Communication style, autonomy level, tool choices. *"Keep responses concise"* is a memory worth more than 50 lines of project detail — it affects every interaction.

**3. Save environment facts.** Versions, paths, dependencies. Things that would take 15 seconds to rediscover but accumulate to hours over a year.

**Do NOT save:** Task progress, session outcomes, temporary state, raw data, "we worked on X yesterday." Those belong in session history or project tracking — not in persistent memory that gets injected into every turn.

### The Correction Protocol

This is the most important habit in the methodology. It takes 10 seconds and compounds massively:

```
Agent: *does something wrong*
You: "No, use python3.11."
Agent: *uses python3.11*
You: "Remember that. Python 3.11 at /opt/homebrew/bin/python3.11."
Agent: *saves to memory*
```

That's it. The agent saves the fact. Next session, it knows. You never correct this again.

After a month of following this protocol, my agent stopped asking basic questions entirely. Python version? In memory. Test command? In memory. Preferred tools? In memory. Communication style? In memory. The correction rate dropped from ~6 per session to ~0.5.

### What to Save Immediately vs. What to Defer

| Situation | Action |
|-----------|--------|
| Agent uses wrong Python version | **Save immediately.** This will happen again. |
| Agent asks a question you've answered before | **Save the answer.** The question itself tells you what's missing from memory. |
| Agent invents a directory that doesn't exist | **Save the correct directory structure.** |
| Agent writes code in a style you don't like | **Save the preference.** "Prefer list comprehensions over map/filter." |
| Agent solves a complex task | **Save as a skill,** not a memory. Skills are for procedures. |
| Agent hits an error and finds a fix | **Save as a skill pitfall.** Memory is for facts, skills are for procedures. |
| You complete a feature | Don't save — that's task state, not memory. Log it in your project tracker. |

### Structured Memory: Beyond Free Text

As your agent grows, flat text memory hits limits. You end up with 200 entries and the agent can't find the right one at the right time.

The solution is structured memory — a lightweight database of typed facts:

```
Entity: python3.11
  Attribute: path
  Value: /opt/homebrew/bin/python3.11
  Category: env

Entity: testing
  Attribute: framework
  Value: pytest
  Category: preference

Entity: user
  Attribute: communication_style
  Value: concise, no filler
  Category: preference
```

This is what the FactBase pattern does (part of the Knowledge Platform at workswithagents.dev). Entity-attribute-value triples, queryable by category. Your agent can ask: "What Python version?" → query `entity=python3.11, attribute=version` → immediate answer.

You don't need to build this from scratch. Most good agent tools have structured memory built in. The point is: as your memory grows beyond 50 entries, structure it. Otherwise you're just building a bigger sticky note.

---

## Real Examples

### The Python Version Problem (Solved)

**Before memory:** Every session for 3 weeks: "Use python3.11." Agent uses python3. Correction. Repeat. ~2 minutes per session × ~15 sessions = 30 minutes of correction over 3 weeks.

**After memory:** Saved once: "Python: python3.11 at /opt/homebrew/bin/python3.11." Agent never asks again. Zero corrections on Python version in the 5 months since.

### The "Proceed" Protocol

I have a workflow where I tell the agent "Proceed" and it works through an entire task list without pausing for approval between steps. This wasn't the agent's default behaviour — agents tend to ask for confirmation at every step.

I saved it: *"When user says 'Proceed' or 'Don't stop until finished,' work through all remaining items without pausing for approval. Commit after each, run tests, move to next. Only stop when done or user interrupts."*

Now every session, the agent reads this. The first time I say "Proceed," it knows exactly what to do. No explanation. No negotiation. Just execution.

### Memory vs. Skills: The Distinction

A common mistake: saving everything to memory when it should be a skill.

```
Memory: "SPFx builds fail when Node version is wrong."
Skill: SPFx build diagnosis — check Node version, check SPFx version, check SCSS resolution, check TypeScript, check webpack memory, check manifest schema. For each failure: exact error signature and fix.
```

Memory says *that* something exists. Skills say *how* to handle it. If you find yourself saving multi-step procedures to memory, stop — that's a skill.

---

## Common Pitfalls

| Pitfall | What happens | Fix |
|---------|--------------|-----|
| **Saving task state to memory** | Memory cluttered with "we're working on X" — agent gets confused, context bloated | Memory = durable facts. Task state = project tracker. Never mix them. |
| **Not saving corrections** | You correct the same thing sessions later | Every correction → memory entry. Immediately. 10 seconds now saves 2 minutes later. |
| **Over-saving** | Memory at 95% capacity, mostly noise | Be selective. "Will this matter in 3 months?" If no, don't save it. |
| **Saving procedures as memory** | Memory has a 10-step deployment checklist | That's a skill. Skills are for procedures. Memory is for facts. |
| **Vague entries** | "We use pytest" — which version? Which flags? | Be specific. "pytest with xdist: `pytest -n 4 -v`." |
| **Never reviewing memory** | 200 entries, 40 are stale, agent reads obsolete facts every session | Monthly review: delete stale entries, update changed facts, structure as it grows. |

---

## Try It Now

1. **Audit your last 3 sessions.** What questions did the agent ask that you've answered before? Those are memory gaps.

2. **Save 5 memory entries right now.** Python version, test command, preferred tools, communication style, one project convention. Use the format: `[Topic]: [specific fact].`

3. **Adopt the correction protocol.** Next time you correct your agent on anything, end with: "Remember that." Save it to memory immediately.

4. **Start a fresh session tomorrow.** Count how many fewer corrections you need. If it's not fewer, your memory entries aren't specific enough or your tool isn't loading them.

**Time investment: 2 minutes per correction. Return: zero re-explanation, forever.**

---

## What's Next

Pattern 4: **Decision Protocols** — Memory tells the agent what it knows. Decision protocols tell it what it can do without asking. When to proceed, when to pause, when to escalate. This is where autonomy begins — and where most people get stuck in micromanagement loops.

---

*Pattern 3 of 10. From the Works With Agents methodology — developed through 5 months of agent-assisted development.*
