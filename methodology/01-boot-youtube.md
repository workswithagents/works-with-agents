# YouTube Script: Pattern 1 — Boot

**Title:** "Your AI Agent Is Wasting 15 Minutes Every Session — Here's The Fix"  
**Duration:** ~8 minutes  
**Style:** Screen recording + talking head intercuts

---

## HOOK (0:00 - 0:45)

[SCREEN: Terminal showing an agent session. Red text: "python3: command not found" → "test directory not found" → "which branch am I on?"]

**VILIUS (voiceover):** "This was my first month working with AI agents. Every session, the same corrections. Use python3.11, not python3. Tests are in the tests/ directory. Don't commit to main. Fifteen minutes of orientation before a single line of useful work."

[SCREEN: Cut to talking head]

**VILIUS (on camera):** "I tracked it. Over a month of daily sessions, I spent seven hours just orienting my agent. That's almost a full workday. And the fix? It takes ten minutes. One file. I'll show you."

---

## THE PROBLEM (0:45 - 2:00)

[SCREEN: Split screen — left side shows clean project, right side shows agent making wrong assumptions]

**VILIUS (voiceover):** "Here's what happens. You open a terminal, you type a prompt, and the agent has zero context. It doesn't know what project it's in. It doesn't know your Python version. It doesn't know your test conventions. It guesses. And guesses wrong."

[SCREEN: List of common agent mistakes scrolling — wrong Python, wrong test runner, wrong git branch, invented directories, deployment scares]

**VILIUS (voiceover):** "The agent isn't stupid. You just haven't told it anything. And that's what most people get wrong — they treat agents like search engines. Type a query, get an answer, move on. But agents are collaborators. And collaborators need onboarding."

---

## THE SOLUTION: AGENTS.md (2:00 - 4:30)

[SCREEN: VS Code open, creating a new file called AGENTS.md]

**VILIUS (on camera):** "The fix is a single file called AGENTS.md. It sits in your project root. Most AI coding tools read it automatically when you start a session. It's the source of truth for your project — the agent's onboarding document."

[SCREEN: AGENTS.md being filled in, line by line]

**VILIUS (voiceover):** "Five things go in this file. One — what the project is. One sentence. Two — the exact stack. Not 'Python' — 'Python 3.11 at /opt/homebrew/bin/python3.11'. Give the agent the exact path. Three — conventions. Exact commands for testing, linting, committing. Four — key files. So the agent knows where things are without asking. Five — autonomy rules. When should the agent ask permission, and when should it just proceed?"

[SCREEN: Highlight each section as it's described]

---

## THE TEMPLATE (4:30 - 5:30)

[SCREEN: Full AGENTS.md template displayed]

**VILIUS (voiceover):** "Here's the template. Fill in five fields — project name, language path, three conventions, three key files, one autonomy rule. Save it. Ten minutes. That's the entire boot pattern."

[SCREEN: Template collapses to a single card showing "5 fields, 10 minutes"]

**VILIUS (on camera):** "If you want to automate this — and you should, because environments change — I've included a Python script in the course materials that discovers your environment and generates AGENTS.md automatically. Run it after you update Python, switch Node versions, or restructure your directories."

---

## BEFORE AND AFTER (5:30 - 6:45)

[SCREEN: Split screen — left is "Before Boot" showing agent corrections, right is "After Boot" showing agent getting everything right]

**VILIUS (voiceover):** "Here's what this looks like in practice. Before boot — every session, I corrected the Python version four times, the test directory three times, the git workflow twice. Fifteen minutes of orientation."

[SCREEN: Timer counting up — 15 minutes wasted per session]

**VILIUS (voiceover):** "After boot — the agent reads AGENTS.md, uses the right Python, runs the right tests, commits to a feature branch. Zero corrections. Thirty seconds of orientation."

[SCREEN: Timer showing 30 seconds → 14.5 minutes of productive work]

**VILIUS (on camera):** "Over a month — that's seven hours reclaimed. Seven hours of actual work that would have been spent correcting an agent that didn't have context."

---

## THE SELF-TEST (6:45 - 7:30)

[SCREEN: Fresh terminal session starting]

**VILIUS (voiceover):** "Here's how you know it worked. Start a fresh session. Ask your agent: what Python version should I use for this project? If it answers from memory — from AGENTS.md — you did it right. If it guesses, your AGENTS.md isn't specific enough, or your tool isn't reading it."

[SCREEN: Agent responds correctly — "Python 3.11 at /opt/homebrew/bin/python3.11"]

**VILIUS (on camera):** "One more thing. If you work in a regulated industry — finance, healthcare, government — add a compliance boundaries section. 'Never access patient-data directory.' 'Never commit credentials.' State the rules upfront. Your agent won't enforce them by itself — that comes in Pattern 9 — but the boundaries make violations harder and give you a clear reference when reviewing."

---

## OUTRO (7:30 - 8:00)

[SCREEN: Works With Agents logo + "10 Patterns" overview]

**VILIUS (voiceover):** "AGENTS.md is the foundation. It gives your agent static knowledge — what the project is, how to work in it. In the next module, we add dynamic knowledge — skills. Reusable procedures your agent loads on demand. When it's done a task before, it doesn't figure it out again from scratch. It loads the skill."

[SCREEN: Call to action — "Download the Boot template at workswithagents.com/learn"]

**VILIUS (on camera):** "Try this today. Ten minutes. AGENTS.md in your project root. Start a fresh session and ask your agent what Python version to use. If you're still correcting it after that — send me a message. But you won't be."

---

## PRODUCTION NOTES

- **B-roll needed:** Terminal sessions showing before/after agent behaviour, VS Code editing AGENTS.md
- **Graphics:** The "5 fields, 10 minutes" card, timer comparison graphic, compliance boundaries callout
- **Music:** Minimal, ambient — don't compete with the explanation
- **Captions:** Yes — the terminal demonstrations need them for the commands
