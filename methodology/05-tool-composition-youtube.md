# YouTube Script: Pattern 5 — Tool Composition

**Title:** "Your AI Agent Is Using The Wrong Tool — Here's The Fix"  
**Duration:** ~7 minutes  
**Style:** Screen recording + talking head

---

## HOOK (0:00 - 0:30)

[SCREEN: Side-by-side — left: delegate_task for coding, spinning for 10 minutes, garbage output. Right: direct write_file + patch, done in 30 seconds.]

**VILIUS (voiceover):** "Same task. Left: fifteen minutes, garbage output. Right: thirty seconds, working code. The difference isn't the agent. It's the tool. Here's the decision matrix that turns fifteen-minute coding disasters into thirty-second surgical edits."

---

## THE TOOLBOX (0:30 - 2:00)

[SCREEN: Six tool icons appearing — write_file, patch, read_file, search_files, terminal, delegate_task]

**VILIUS (on camera):** "Your agent has a toolbox. write_file for new code. patch for edits. read_file for reading. search_files for finding. terminal for commands. delegate_task for parallel research. The difference between the right tool and the wrong one: thirty seconds versus fifteen minutes."

---

## THE GOLDEN RULE (2:00 - 4:00)

[SCREEN: Big red X over "delegate_task for code"]

**VILIUS (voiceover):** "Never delegate coding to a sub-agent. This was my most expensive lesson. Sub-agents don't know your project. They don't know your conventions. They invent directories, hallucinate APIs, and time out with garbage output."

[SCREEN: Real example — SPFx web part delegation disaster]

**VILIUS (on camera):** "I once delegated an SPFx web part build. The sub-agent invented a directory structure that doesn't exist in SPFx, generated TypeScript that didn't match the framework, and timed out after ten minutes. I spent ninety minutes undoing the damage. After that: direct tools only for coding. Skills for framework-specific work. Three minutes per build."

---

## THE DECISION MATRIX (4:00 - 6:00)

[SCREEN: Tool decision matrix table]

**VILIUS (voiceover):** "Read a file? read_file — not cat. Edit a file? patch — not sed. Create a file? write_file — not echo. Research? delegate_task — not manual browsing. Run a command? terminal — the one thing terminal is actually for."

[SCREEN: When to use each tool, one at a time with examples]

**VILIUS (on camera):** "Here's the test. If your agent is about to spawn a sub-agent, ask: is this research, or is this code? Research: delegate. Code: never delegate. If your agent reaches for terminal to read a file: stop. read_file gives line numbers, pagination, and won't flood your context. Terminal is for commands. That's it."

---

## OUTRO (6:00 - 7:00)

**VILIUS (voiceover):** "Right tool, right job. Next: Orchestration — when the work is too big for one agent, how to split it across multiple agents working in parallel."

**VILIUS (on camera):** "The golden rule one more time: never delegate coding. Write it directly. Test it. Move on."
