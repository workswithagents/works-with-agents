# YouTube Script: Pattern 4 — Decision Protocols

**Title:** "The One Word That Makes AI Agents 10x Faster"  
**Duration:** ~8 minutes  
**Style:** Screen recording + talking head

---

## HOOK (0:00 - 0:35)

[SCREEN: Terminal — agent asking "Should I commit?" "Should I run tests?" "Should I deploy?" rapid-fire]

**VILIUS (voiceover):** "Should I commit? Should I create a PR? Should I deploy? Should I — NO. This was my sessions before decision protocols. Eight interruptions per task. Four angry corrections. Every single time."

[SCREEN: Same task, agent just executes silently — writes, tests, commits, PRs — done]

**VILIUS (on camera):** "After decision protocols: one word. 'Proceed.' The agent handles everything. Zero interruptions. Zero corrections. Here's how."

---

## THE MICROMANAGEMENT TRAP (0:35 - 1:45)

[SCREEN: Split screen — left: user constantly typing approvals, right: work piling up]

**VILIUS (voiceover):** "The trap: either you let the agent do anything — deployment scares, overwritten files, broken builds. Or you approve every decision — and you're not collaborating with an agent, you're operating a slow command line."

[SCREEN: Three tiers graphic appearing — Green, Amber, Red]

**VILIUS (voiceover):** "The fix is three zones. Green: proceed without asking. Amber: proceed but tell me. Red: never without explicit approval. Write these down, save them to memory, and the agent follows them every session."

---

## THE THREE ZONES (1:45 - 4:30)

[SCREEN: Green zone — tests, file reads, searches, non-destructive commands]

**VILIUS (on camera):** "Green zone. Writing new files, running tests, linting, searching code, committing to feature branches. Actions where being wrong doesn't cause damage. Worst case: a file in the wrong place, a test that fails. All recoverable."

[SCREEN: Amber zone — file edits, package installs, PR creation, staging deploys]

**VILIUS (voiceover):** "Amber zone. Modifying existing files, installing dependencies, creating pull requests, staging deployments. The agent proceeds — you don't approve every one — but it tells you what it did. You spot-check. This is where the speed comes from."

[SCREEN: Red zone — production deploys, destructive DB ops, emails, payments, production secrets]

**VILIUS (voiceover):** "Red zone. Production deployment. Destructive database operations. Sending emails. Posting to social media. Modifying payments. Accessing production secrets. Anything with regulatory impact. The agent must never do these without explicit approval. Ever."

---

## THE PROCEED PROTOCOL (4:30 - 6:00)

[SCREEN: User typing "Proceed" → agent executes full multi-step task without pausing]

**VILIUS (on camera):** "Here's the highest-leverage protocol I use. One word: 'Proceed.' It elevates Green and Amber to full autonomy. The agent works through an entire task list without pausing once."

[SCREEN: Before/After comparison]

**VILIUS (voiceover):** "Before: eight interruptions, four corrections per task. After: zero. I type 'Proceed,' come back in fifteen minutes, and the feature is done with passing tests. This one protocol saved me more time than everything else combined."

---

## TRUST CALIBRATION (6:00 - 7:00)

[SCREEN: Timeline — Week 1 restrictive → Month 2 autonomous]

**VILIUS (voiceover):** "Start restrictive. Week one, everything in Amber requires approval. You're learning the agent's judgment. Week two, move proven actions to Green. Week three, introduce 'Proceed' for small task lists. By month two, the agent runs autonomously on well-defined work."

[SCREEN: Key point: "Trust is earned, not granted"]

**VILIUS (on camera):** "Every mistake resets the calibration. Not all the way back — but you tighten the relevant zone. The agent deployed to staging without tests? Amber zone for deploys gets approval required for two weeks. It's a feedback loop, not a grudge."

---

## OUTRO (7:00 - 8:00)

[SCREEN: Works With Agents logo]

**VILIUS (voiceover):** "Decision protocols give your agent boundaries. In the next module: Tool Composition — the agent knows when to act, but does it know which tool to use? The difference between the right tool and the wrong one is the difference between 30 seconds and 15 minutes."

[SCREEN: Call to action]

**VILIUS (on camera):** "Write your three zones right now. Green, Amber, Red. Save them to memory. Add the Proceed protocol. Next session, give your agent a multi-step task and say 'Proceed.' You'll never go back."
