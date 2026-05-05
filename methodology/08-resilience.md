# Pattern 8: Resilience — Never-Stop Loops

**Time to read:** 13 minutes  
**Time to apply:** 20 minutes to add to existing pipelines  
**Prerequisites:** Patterns 1-7, especially Pipelines

---

## What Most People Do Wrong

Their agent hits an error and stops. Build fails once — agent gives up. API returns 503 — agent reports failure and waits for instructions. A transient network blip kills a pipeline that would have succeeded on the second attempt.

Result: you spend your mornings restarting pipelines that failed at 3 AM because of a 2-second network hiccup. You become the retry mechanism. The agent has one attempt and quits.

Resilience means the agent doesn't quit on the first failure. It retries. It categorises errors. It finds another way. It only escalates to you when it's genuinely stuck.

---

## The Pattern

### Error Categorisation

Not all errors are equal. The agent needs to distinguish:

**Transient errors** — Retry. The thing will probably work on the second attempt.
- Network timeouts
- API rate limits (429)
- Service temporarily unavailable (503)
- Database connection pool exhausted
- File locked by another process

**Permanent errors** — Don't retry. It'll fail the same way every time.
- Authentication failure (401/403)
- Resource not found (404)
- Invalid input / schema validation failure
- Missing dependencies
- Configuration errors

**Unknown errors** — Retry once. If it fails again, escalate.
- Anything not in the above categories

### The Retry Pattern

```python
import time

def retry_with_backoff(fn, max_attempts=3, base_delay=2):
    """Retry a function with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return fn()
        except TransientError:
            if attempt == max_attempts - 1:
                raise  # All retries exhausted
            delay = base_delay * (2 ** attempt)  # 2s, 4s, 8s
            time.sleep(delay)
        except PermanentError:
            raise  # Don't retry — it'll fail the same way
        except Exception:
            if attempt == 0:
                time.sleep(base_delay)  # One retry for unknowns
            else:
                raise
```

This pattern means:
- Network timeout → wait 2 seconds, try again → succeeds → pipeline continues
- API 429 rate limit → wait 4 seconds, try again → succeeds
- Auth 401 → don't retry → report immediately → you fix the credentials
- Unknown error → retry once → if it fails again, escalate to you

### The Escalation Protocol

When all retries are exhausted, the agent escalates. Not a vague "something failed" — a structured report:

```
PIPELINE FAILURE: Nightly Build — Step 3 (Build documentation)

Error: sphinx-build exited with code 2
Last successful: 2026-05-03 (2 days ago)
Retries attempted: 3
Error category: Permanent (config issue)
Likely cause: Missing conf.py or broken Sphinx config
Suggested action: Check docs/conf.py was not modified in recent commits
```

This is what you want to wake up to. Not "build failed" — you have to diagnose. A structured escalation that's halfway to diagnosis already. You spend 2 minutes fixing instead of 20 minutes investigating.

### Self-Healing (Advanced)

Beyond retry: the agent fixes the problem itself. This requires skills and decision protocols working together.

Example: a pipeline detects that a Python package is missing. The agent doesn't just report "import error" — it runs `pip install`, verifies the import works, and continues the pipeline.

Self-healing rules:
1. The fix must be deterministic (pip install, cache clear, restart service)
2. The fix must be in the Green or Amber zone (see Pattern 4)
3. After self-healing, log what happened — even if it worked
4. If the fix fails, escalate normally

Self-healing transforms "pipeline failed at 3 AM, I fixed it at 9 AM" into "pipeline detected a problem at 3 AM, fixed itself, and I read about it in the morning log."

---

## Real Examples

### The Nightly Build That Saved Itself

Pipeline: nightly test suite. Error: `ModuleNotFoundError: No module named 'httpx'`. Agent categorises: permanent (missing dependency), but fixable (deterministic pip install). Agent runs `pip install httpx`, verifies import, re-runs tests — all pass. Pipeline completes.

Morning log: "Pipeline self-healed: installed missing httpx dependency. Tests passed normally. No action needed."

Without resilience: pipeline fails at 3 AM. I wake up at 7 AM. See failure notification. Diagnose. Pip install. Re-run. 30 minutes. With resilience: I wake up, check the log, see it self-healed, move on. 30 seconds.

### The API Blip

Health check pipeline hits a 503 from an endpoint. Transient error → retry after 2 seconds → still 503 → retry after 4 seconds → 200 OK. Pipeline continues. No alert. No escalation. Just handled.

Without retry: alert fires at 3:14 AM. I wake up, check — service is fine, it was a 2-second blip. I'm annoyed. With retry: the blip is absorbed. I never hear about it.

---

## Common Pitfalls

| Pitfall | What happens | Fix |
|---------|--------------|-----|
| **Retrying permanent errors** | Auth 401 retried 3 times — same result, wasted time | Categorise errors. Permanent = no retry, escalate immediately. |
| **No backoff** | Retries fire instantly — 3 attempts in 200ms, all fail | Exponential backoff: 2s, 4s, 8s. Give the problem time to resolve. |
| **Too many retries** | 10 retries over 5 minutes on a permanently broken service | Max 3 retries for transient, 1 for unknown. After that, escalate. |
| **Self-healing without logging** | Agent fixed something silently — you never know it happened | Log all self-healing actions. Even successful ones. |
| **Self-healing in Red zone** | Agent "fixed" a production database by running a migration without approval | Self-healing only for Green/Amber zone actions. Never Red. |
| **Escalating too early** | Single 503 triggers alert — you're woken up for nothing | At least 1 retry before escalation. Transient errors are common. |

---

## Try It Now

1. **Add retry to your next pipeline.** 3 attempts, exponential backoff (2s, 4s, 8s). Transient errors only.
2. **Categorise your common errors.** Go through the last 5 pipeline failures. Which were transient (retry would have fixed them)? Which were permanent (retry would have been wasted)?
3. **Write one escalation template.** Structured: what failed, when it last worked, retries attempted, likely cause, suggested action.

**Time investment: 20 minutes. Return: pipelines that don't wake you up for transient blips.**

---

## What's Next

Pattern 9: **Verify** — Resilience handles failures automatically. But what about successes that are actually failures? Trust but verify: automated gates that catch problems before they reach production, and a human review cadence for everything the agent does.

---

*Pattern 8 of 10. From the Works With Agents methodology.*
