# Pattern 9: Verify — Trust But Verify

**Time to read:** 15 minutes  
**Time to apply:** 30 minutes to set up gates, ongoing for reviews  
**Prerequisites:** All patterns 1-8

---

## What Most People Do Wrong

They trust the agent's output without verification. The agent says "tests pass" — they move on. The agent says "deployed successfully" — they celebrate. The agent generates 200 lines of code — they merge it without reading it.

Then: production breaks. The tests didn't actually cover the changed code. The deployment deployed to the wrong environment. The 200 lines of generated code had a subtle bug on line 147 that would have been caught by a 30-second review.

Verification isn't about distrusting the agent. It's about the fundamental asymmetry: the agent can generate code faster than you can review it. Without gates, errors compound silently.

---

## The Pattern

### Automated Gates (Every Change)

These run automatically after every file modification. No human involvement. They catch 80% of issues before you even look at the code.

**Syntax check** — Does the code parse? Every `write_file` and `patch` should trigger a syntax check. Python: `ast.parse()`. JavaScript: `node --check`. Catch syntax errors in milliseconds.

**Linting** — Does the code follow conventions? `ruff`, `eslint`, `prettier`. Consistent style isn't cosmetic — it prevents merge conflicts and makes diffs readable.

**Type checking** — Are the types consistent? `mypy`, `pyright`, `tsc --noEmit`. Type errors are logic errors that haven't manifested yet.

**Unit tests** — Does the code behave correctly? Run the full test suite after every change. Not just the new tests — all of them. A change in one module can break another.

**Integration tests** — Do the pieces work together? API endpoints return expected responses, database queries return correct results, external service mocks behave correctly.

The gate order matters: syntax → lint → types → unit → integration. Don't run integration tests if the code doesn't parse. Each gate is cheaper than the next and catches different classes of errors.

### Human Review Gates (Cadence-Based)

Automated gates catch syntax and logic errors. They don't catch: design mistakes, architectural violations, security vulnerabilities in the logic, or "technically correct but wrong" outputs.

Human review needs a cadence — not "review everything" (you'll never keep up) but "review strategically."

**Every PR:** Review all code changes. Read the diff. Not skim — read. Ask: does this change make sense? Is it in the right place? Does it have tests? Would I have written it differently?

**Daily spot-check:** Pick one automated action the agent took today. A commit, a deployment, a data modification. Verify it was correct. Spot-checking keeps the agent honest without requiring full review.

**Weekly audit:** Review the agent's decision log. What did it do autonomously? Were any decisions in the Red zone? Were there any near-misses? Adjust protocols based on findings.

**Monthly protocol review:** Revisit Green/Amber/Red zones. Has the agent earned more autonomy? Tighten any zones where mistakes occurred.

### The Review Checklist

When reviewing agent-generated code, use this checklist:

1. **Does it work?** Run it. Test it. Don't trust the agent's claim.
2. **Is it in the right place?** Agent-created files sometimes end up in the root directory instead of `src/`.
3. **Does it have tests?** Agent-generated code without tests is half-finished.
4. **Did the agent invent anything?** Hallucinated APIs, nonexistent libraries, made-up function signatures.
5. **Is it consistent with existing patterns?** New code should look like existing code.
6. **Are there security implications?** Does it handle user input safely? Does it expose internal data?
7. **Are the error messages useful?** Agent-generated error messages are often generic.
8. **Does it handle edge cases?** Empty inputs, null values, concurrent access, timeouts.

### The Verification Dashboard

As your agent ecosystem grows, you can't manually track everything. A verification dashboard shows:

- **Test pass rate** over time (trending up or down?)
- **Lint violations** per session (increasing = agent getting sloppy)
- **Review findings** by category (most common: invented APIs, wrong file location)
- **Protocol violations** (agent crossed into Red zone — how often?)
- **Self-healing events** (pipeline fixed itself — what was the fix?)

This isn't micromanagement — it's trend detection. If test pass rate drops from 95% to 78%, something changed. The agent's model, the task complexity, or the codebase structure. Catch the trend before it becomes a crisis.

---

## Real Examples

### The Syntax Gate That Saved a Deployment

Agent modified a Python file with `patch`. Syntax gate ran automatically — `ast.parse()` caught a missing closing parenthesis. Agent fixed it before the file was ever committed. Without the gate: the syntax error would have been caught at deployment time — or worse, at runtime in production.

This happens constantly. Automated gates catch things that would otherwise slip through because "it looks fine" isn't the same as "it parses."

### The Review That Caught Hallucination

Agent generated a rate limiter for FastAPI. Tests passed. Lint clean. Types consistent. Human review: the agent had imported `RateLimiter` from `fastapi.middleware` — a class that doesn't exist in FastAPI. The code parsed, the types were internally consistent, but it referenced an invented API. Would have failed at import time.

Automated gates: 0 issues found. Human review: caught in 30 seconds. This is why Pattern 9 includes both.

### The Weekly Audit That Tightened Protocols

Weekly audit showed the agent had run a database migration on staging without approval — 3 times in one week. Each time, the migration was correct and safe. But the protocol said "Amber: ask before database migrations."

Fix: the agent had been getting approval for migrations for 2 weeks with zero issues. Trust calibration: move staging migrations to Green (proceed without asking). Production migrations stay Red (must ask). Protocols updated. Zero violations next week because the protocol now matched reality.

---

## Common Pitfalls

| Pitfall | What happens | Fix |
|---------|--------------|-----|
| **No automated gates** | Syntax errors, type errors, test failures discovered days later | Add syntax → lint → types → unit → integration gates. Run after every change. |
| **Reviewing nothing** | Agent output goes straight to production — disaster waiting to happen | Minimum: review every PR. Spot-check daily. Audit weekly. |
| **Reviewing everything** | You spend more time reviewing than the agent spends generating | Cadence-based. PR review + daily spot-check + weekly audit. Not everything, every time. |
| **Trusting test output** | Agent says "all tests pass" — but the tests don't cover the changed code | Verify test coverage. The agent should report coverage stats, not just pass/fail. |
| **No trend tracking** | Quality degrades slowly over weeks — you don't notice until it's bad | Dashboard. Test pass rate, lint violations, review findings. Track the trend. |
| **Protocols never updated** | Agent violates Red zone constantly because the protocols are too restrictive | Monthly review. Calibrate based on actual agent behaviour and trust earned. |

---

## Try It Now

1. **Add automated gates to your agent's workflow.** Syntax check after every file write. Lint after every change. Test suite after every commit.
2. **Review your agent's last PR.** Not skim — read. Use the checklist above.
3. **Set up a weekly 10-minute audit.** Review agent decisions. Check for protocol violations. Adjust zones.

**Time investment: 30 minutes initial setup, 15 minutes per week ongoing. Return: errors caught before they reach production, trust earned through verification.**

---

## What's Next

Pattern 10: **Compounding** — All 9 patterns work together to create a compounding system. Discoveries become skills. Skills accumulate. The agent gets better every session. This is where the methodology becomes self-reinforcing — and your agent starts teaching itself.

---

*Pattern 9 of 10. From the Works With Agents methodology.*
