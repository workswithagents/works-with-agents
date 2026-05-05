# YouTube Script: Pattern 8 — Resilience

**Title:** "Stop Restarting Failed Pipelines At 7 AM"  
**Duration:** ~7 minutes  
**Style:** Screen recording + talking head

---

## HOOK (0:00 - 0:35)

[SCREEN: Phone notification at 3:14 AM — "Pipeline failed." User wakes up, checks — service is fine, just a 2-second blip.]

**VILIUS (voiceover):** "3:14 AM. Pipeline failed. I check — the service is fine. Two-second network blip. My pipeline had one attempt and quit. I was the retry mechanism."

[SCREEN: Same scenario, agent retries 3 times, succeeds, no alert sent.]

**VILIUS (on camera):** "After resilience: the blip is absorbed. I never hear about it. Here's how to make your agent not quit on the first failure."

---

## ERROR CATEGORIES (0:35 - 2:30)

[SCREEN: Three error categories — Transient (retry), Permanent (escalate), Unknown (retry once)]

**VILIUS (voiceover):** "Step one: categorise errors. Transient — network timeouts, rate limits, 503s. These will probably work on the second attempt. Retry with backoff. Permanent — auth failures, missing dependencies, config errors. Don't retry. Escalate immediately. Unknown — everything else. Retry once. If it fails again, escalate."

[SCREEN: Code — retry_with_backoff function with exponential delays]

**VILIUS (on camera):** "Exponential backoff: two seconds, four seconds, eight seconds. Three attempts max. This handles 90% of transient failures without waking you up."

---

## SELF-HEALING (2:30 - 4:30)

[SCREEN: Pipeline detects missing dependency → pip install → verifies → continues → logs action]

**VILIUS (voiceover):** "Beyond retry: self-healing. The agent doesn't just report the error — it fixes it. Missing Python package? pip install. Cache corruption? Clear and retry. Service needs restart? Restart it."

[SCREEN: Self-healing rules — Green/Amber zone only, always log, escalate if fix fails]

**VILIUS (on camera):** "Rules: the fix must be deterministic, in Green or Amber zone, and logged. I wake up, check the pipeline log: 'Self-healed: installed missing httpx. Tests passed. No action needed.' Thirty seconds instead of thirty minutes."

---

## OUTRO (4:30 - 7:00)

**VILIUS (voiceover):** "Resilience handles failures. Next: Verify — because sometimes the agent succeeds but gets it wrong. Automated gates that catch problems before they reach production."

**VILIUS (on camera):** "Today: add retry to your health check. Three attempts, exponential backoff. You'll stop getting woken up for transient blips by tomorrow morning."
