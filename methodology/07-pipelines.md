# Pattern 7: Pipelines — Agents That Run While You Sleep

**Time to read:** 15 minutes  
**Time to apply:** 45 minutes for first pipeline  
**Prerequisites:** Patterns 1-6

---

## What Most People Do Wrong

They're the trigger. Every agent action starts with them typing a prompt. When they're not at the keyboard, nothing happens.

This works for interactive work. It fails for everything else — scheduled builds, nightly health checks, automated monitoring, data collection, content generation. Anything that should happen on a timer requires you to be there. And you can't be there at 3 AM.

Pipelines flip this. The agent becomes the trigger. Time, events, or conditions fire the agent — not you.

---

## The Pattern

### Pipeline Types

**Cron pipelines** — Time-based. "Run this every hour." "Build every night at 2 AM." "Check health every 10 minutes."

**Event pipelines** — Triggered by external events. "When a PR is opened, review it." "When a deploy completes, run integration tests." "When a new file appears in the upload directory, process it."

**Chain pipelines** — Output of one agent feeds input of the next. "Collect data → analyse → generate report → email summary."

### Your First Cron Pipeline

The simplest pipeline: a scheduled health check that monitors your services and only alerts you when something's wrong.

```
Schedule: Every 30 minutes
What: Check all API endpoints are responding, verify database connectivity, confirm disk space above threshold
Output: Silent if healthy. Alert message if something's broken.
```

Implementation:
```python
# health_check.py — runs every 30 minutes via cron
import requests, json, sys

ENDPOINTS = [
    "https://workswithagents.dev/v1/health",
    "https://workswithagents.io/v1/health",
    "https://bastiongateway.com/v1/health",
]

failures = []
for url in ENDPOINTS:
    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200 or r.json().get("status") != "ok":
            failures.append(f"{url}: status={r.status_code}")
    except Exception as e:
        failures.append(f"{url}: {e}")

if failures:
    # Alert — something's wrong
    print("HEALTH CHECK FAILED:")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
else:
    # Silent — everything's fine
    print("All healthy")
```

Key design: the script only outputs when something's wrong. Silent success. This is how pipelines avoid notification fatigue — you only hear about them when you need to act.

### Multi-Step Build Pipeline

A more complex pipeline: every night at 2 AM, run tests, build docs, generate changelog, deploy to staging.

```
Step 1: Pull latest changes (git pull)
Step 2: Run full test suite (pytest -n 4)
Step 3: Build documentation (sphinx-build)
Step 4: Generate changelog from commits since last tag
Step 5: Deploy to staging
Step 6: Run smoke tests against staging
Step 7: Report results — success summary or failure alert
```

Each step depends on the previous step succeeding. If tests fail at step 2, the pipeline stops — no deploying broken code to staging. This is pipeline composition: chaining agents together with success/failure gates.

### The "Silent Unless Broken" Principle

The most important pipeline design rule: **send output only when something needs attention.**

A pipeline that reports "all tests passed" 24 times a day trains you to ignore it. A pipeline that only reports "build failed — check logs" gets your attention immediately.

Implementation: the pipeline's exit code determines delivery. Exit 0 (success) = no message sent. Exit non-zero (failure) = alert delivered. Most agent cron systems support this natively.

### Pipeline vs. Interactive Work

| Aspect | Interactive (you trigger) | Pipeline (time/event triggers) |
|--------|--------------------------|-------------------------------|
| Trigger | You type a prompt | Schedule or event |
| Speed | Blocked on your response time | Autonomous, no waiting |
| Scale | One task at a time | Can run multiple pipelines simultaneously |
| Attention | You watch it happen | You get notified only on failure |
| Best for | Exploratory work, decisions, complex single tasks | Repeated work, monitoring, scheduled operations |

---

## Real Examples

### Nightly Build Pipeline (5 months, 0 missed builds)

A cron job runs every night at 2 AM. It pulls the latest code, runs the full test suite, generates docs, and deploys to staging. Output: silent when successful, alert when tests fail.

Over 5 months: 0 builds missed, 3 alerts (all genuine test failures from dependency updates), 0 false alarms. I sleep through it every night.

### Health Monitor (catches problems before users notice)

A 10-minute health check monitors 5 services across 4 domains. When an endpoint goes down, I get an alert within 10 minutes — usually before any user notices. The script has caught 4 outages in 2 months, all resolved within minutes of the alert.

### Content Pipeline (research → draft → review)

A weekly pipeline: research agent collects interesting developments in AI agent tooling → draft agent writes a newsletter post → review agent checks facts, voice, and length → final draft arrives in my inbox for approval. What used to take 3 hours of manual work now takes 5 minutes of review.

---

## Common Pitfalls

| Pitfall | What happens | Fix |
|---------|--------------|-----|
| **Noisy pipelines** | "All tests passed" message every 30 minutes — you start ignoring all pipeline output | Silent unless broken. Only notify on failures. |
| **No failure handling** | Pipeline step 3 fails, step 4 runs anyway with broken data | Each step gates the next. Failure stops the chain. |
| **Over-pipelining** | Every small task becomes a cron job — 47 pipelines, impossible to maintain | Pipeline for repeated, scheduled work only. Interactive work stays interactive. |
| **Wrong schedule** | Health check every 5 minutes — burns API tokens for no benefit | Match the schedule to the urgency. Health: 10-30 min. Builds: nightly. Research: weekly. |
| **No alerting** | Pipeline fails silently — you find out 3 days later | Every pipeline needs a failure notification path. |
| **Ignoring pipeline output** | Alert fires, you don't see it for hours | Route alerts to where you actually look. Not email — Telegram, Slack, push notification. |

---

## Try It Now

1. **Create a health check pipeline.** Pick 2-3 of your services. Write a script that checks their health endpoints. Set it to run every 30 minutes. Make it silent on success.

2. **Set up a nightly build.** If you have tests, run them every night. Report only failures. You'll catch dependency breakage before it becomes a debugging session.

3. **Add alert routing.** Don't send pipeline output to email. Send it to where you actually look — messaging platform, push notification, or a dashboard.

**Time investment: 45 minutes for first pipeline. Return: problems caught before users notice them.**

---

## What's Next

Pattern 8: **Resilience** — Pipelines run autonomously. But when they fail — and they will — what happens? Never-stop loops, retry with backoff, self-healing. The agent finds another way instead of giving up.

---

*Pattern 7 of 10. From the Works With Agents methodology.*
