# Works With Agents — Module 1: What AI Agents Actually Are

> **Tier:** Foundation (Free)
> **Format:** Written guide + YouTube video script
> **Time:** ~30 minutes
> **Goal:** Student understands what an AI agent is, sees a real one working, and wants Module 2

---

## Lesson 1.1: The 30-Second Definition

An AI agent is a program that:

1. **Gets a task** — you tell it what to do in plain English
2. **Thinks** — it plans how to accomplish it
3. **Acts** — it uses tools (terminal, browser, APIs) to do the work
4. **Checks** — it verifies the result and fixes mistakes
5. **Reports** — it tells you what happened

**Not:** A chatbot you have to babysit. **Not:** An "AI assistant" that needs you to copy-paste. An agent works *while you do something else*.

> "If you have to watch it, it's a tool. If it reports back when done, it's an agent."

---

## Lesson 1.2: Real Agent in Action (Live Demo)

Let me show you a real agent working. This agent:

- Runs unattended every hour
- Reads medical research papers
- Extracts relevant findings
- Writes a summary
- Sends it to a Telegram channel

**What you'll see:**
```
[09:00] Agent: Starting KAT6A research scan...
[09:00] Agent: Searching PubMed for new papers...
[09:01] Agent: Found 3 new papers this week
[09:02] Agent: Reading paper 1: "KAT6A mutations in neurodevelopment..."
[09:03] Agent: Extracting key findings...
[09:04] Agent: Paper 1 done. Moving to paper 2.
[09:05] Agent: All 3 papers processed.
[09:05] Agent: Writing summary...
[09:06] Agent: ✅ Summary sent to Telegram.
[09:06] Agent: Next scan in 1 hour. Going to sleep.
```

**This ran while its creator was making coffee.** That's the difference between an agent and a chatbot.

---

## Lesson 1.3: The Agent Spectrum

Not all agents are created equal. Here's the spectrum:

| Level | Name | Example | You do | Agent does |
|-------|------|---------|--------|------------|
| 1 | **Assisted** | ChatGPT, Copilot | Define task, review output, copy-paste | Generate text |
| 2 | **Semi-autonomous** | Claude Code, Codex | Define task, review PR | Write code, run tests, open PR |
| 3 | **Autonomous** | Cron agents, pipelines | Define task once | Run forever, self-heal, report |
| 4 | **Orchestrated** | Multi-agent systems | Define system architecture | Delegate, review, escalate, learn |

Most people are stuck at Level 1. This course takes you to Level 3. Level 4 is the advanced track.

---

## Lesson 1.4: What Agents Can Do (That You're Not Doing)

Real things agents do TODAY:

### For Developers
- ✅ Review every PR automatically (not just when you remember)
- ✅ Write unit tests for code you haven't touched in months
- ✅ Monitor error logs and open tickets with diagnostics
- ✅ Update dependencies and run the test suite overnight
- ✅ Generate documentation from code comments

### For Knowledge Workers
- ✅ Scan 100 research papers, find the 3 relevant ones
- ✅ Monitor competitors' websites for changes
- ✅ Draft weekly status reports from your commit history
- ✅ Transcribe meetings, extract action items, create tickets
- ✅ Track regulatory changes in your industry

### For Everyone
- ✅ Morning briefing: weather, calendar, news, traffic
- ✅ Weekly household reset reminders
- ✅ "Find me the cheapest flights to X in next 3 months"
- ✅ "Summarize this 50-page PDF and tell me if section 4.2 matters"

**The agent does the boring part. You do the thinking part.**

---

## Lesson 1.5: The 3 Things You Need

To run your own agent, you need exactly three things:

| Component | Options | Cost |
|-----------|---------|------|
| **A brain** (LLM) | Free: oMLX + local models. Cheap: DeepSeek API. Best: Claude. | £0-£20/mo |
| **A home** (runtime) | Your laptop (free), a cheap VPS (£5/mo), a Raspberry Pi | £0-£5/mo |
| **A task** (prompt) | You'll write this in Module 2 | Free |

That's it. £0-£25/month to have an AI employee working 24/7.

---

## Lesson 1.6: Why Now?

Three things changed in 2025-2026 that made agents possible:

1. **Models got good enough** — They can now plan, use tools, and recover from errors. 2023 models couldn't do this.
2. **Tools got standardized** — Every agent framework uses the same pattern: think → act → observe → repeat. The "tool calling" API is universal.
3. **Cost collapsed** — Local 8B models run on a MacBook. API calls cost fractions of a penny. The economics finally work.

> "In 2023, an agent that ran 24/7 cost £500/month. Today it costs £0."

---

## Module 1 Action Item

Before Module 2, do this (**10 minutes**):

1. Open ChatGPT/Claude and type: *"You are an AI agent. I need you to plan how you would monitor a website for changes and notify me. Don't do it — just write the plan. Include: what tools you'd need, how often you'd check, what you'd do if the site is down, and how you'd notify me."*
2. Read its response. Notice: it can PLAN agent behavior even though it can't EXECUTE it (yet).
3. Write down: "One thing I do weekly that I wish an agent could do for me."

**Next: Module 2 — Setting Up Your First Agent** (available in the Builder tier)

---

## YouTube Script Notes

**Title:** "What AI Agents Actually Are (In 10 Minutes)"

**Hook (0:00-0:30):**
"Last week, an AI agent reviewed 37 code changes, found 3 bugs, and opened fix PRs — while I was asleep. It cost me £0.47 in API credits. If you're still copy-pasting into ChatGPT, you're doing it wrong. Here's what AI agents actually are."

**Structure:**
1. (0:30-1:30) The 30-second definition with visual
2. (1:30-3:30) Live demo of the KAT6A research agent
3. (3:30-5:00) The agent spectrum (1-4) with visuals
4. (5:00-7:00) 5 things agents can do that you're not doing
5. (7:00-8:30) The 3 things you need (LLM, runtime, task)
6. (8:30-9:30) Why now (2025-2026 inflection point)
7. (9:30-10:00) CTA: "Module 2 shows you how to set up your first agent. Link in description."

**B-roll ideas:**
- Terminal recording of agent running
- Screen recording of Telegram notification arriving
- Architecture diagram (simple: brain → tools → output)
- Side-by-side: "You copy-pasting" vs "Agent running unattended"
