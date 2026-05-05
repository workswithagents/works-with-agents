# YouTube Script: Pattern 9 — Verify

**Title:** "Your AI Agent Is Getting It Wrong — Here's How To Catch It"  
**Duration:** ~8 minutes  
**Style:** Screen recording + talking head

---

## HOOK (0:00 - 0:35)

[SCREEN: Agent output: "All tests pass. Deploy complete." User celebrates. Cut to production error: ImportError on a module that doesn't exist.]

**VILIUS (voiceover):** "Agent says tests pass. I celebrate. Production breaks. The agent had imported RateLimiter from fastapi.middleware — a class that doesn't exist. The code parsed, types were clean, tests were internally consistent. But it referenced an invented API. Automated gates: zero issues. Human review: caught in thirty seconds."

[SCREEN: Cut to talking head]

**VILIUS (on camera):** "Verification isn't distrust. It's the fundamental asymmetry: agents generate code faster than you can review it. Without gates, errors compound silently. Here's the system."

---

## TWO LAYERS (0:35 - 3:00)

[SCREEN: Automated gates → Human review. Two-layer diagram.]

**VILIUS (voiceover):** "Two verification layers. Automated gates catch 80% — syntax, lint, types, tests. Run after every change, no human involvement. Human review catches the 20% — design mistakes, security logic, hallucinations. Cadence-based, not everything-every-time."

[SCREEN: Gate order — syntax → lint → types → unit → integration]

**VILIUS (on camera):** "Gate order matters. Don't run integration tests if the code doesn't parse. Each gate is cheaper than the next and catches different problems. Syntax gate alone has saved me from deploying broken code more times than I can count."

---

## HUMAN REVIEW (3:00 - 5:30)

[SCREEN: Review checklist — 8 items]

**VILIUS (voiceover):** "Human review: every PR, read the diff. Daily spot-check: pick one action the agent took, verify it. Weekly audit: review decisions, check for protocol violations. Monthly: recalibrate trust zones."

[SCREEN: Example — agent hallucinates API, caught in review]

**VILIUS (on camera):** "That RateLimiter hallucination — automated gates passed. Types were clean. Tests were consistent. But the class doesn't exist. Human review caught it because I recognised the import was wrong. AI agents hallucinate APIs. You catch it by reading the diffs."

---

## THE DASHBOARD (5:30 - 7:00)

[SCREEN: Verification dashboard — test pass rate trending, lint violations per session, review findings by category, protocol violations]

**VILIUS (voiceover):** "As your agent ecosystem grows, track the trends. Test pass rate dropping? Something changed. Lint violations increasing? Agent's getting sloppy. This isn't micromanagement — it's catching problems before they become crises."

---

## OUTRO (7:00 - 8:00)

**VILIUS (voiceover):** "Verification completes the safety net. Next: Compounding — all 9 patterns working together. Discoveries become skills. Skills accumulate. The agent gets better every session. This is where it becomes self-reinforcing."

**VILIUS (on camera):** "Today: review your agent's last PR. Read the diff. Check for invented APIs. You'll find something. They always do."
