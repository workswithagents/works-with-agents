# Pattern 2: Skills — Build Once, Use Forever

**Time to read:** 18 minutes  
**Time to apply:** 45 minutes for your first skill, 15 minutes per subsequent skill  
**Prerequisites:** Pattern 1 (Boot — your agent has an AGENTS.md)

---

## What Most People Do Wrong

They tell their agent how to do something. The agent does it. Next session, they tell it again. Every single time.

The result: you become the skill library. Your brain holds all the procedural knowledge. The agent forgets everything between sessions. You're not collaborating with an agent — you're operating a very fancy command line.

Here's what that looks like in practice:

```
Session 1: "Set up a new Python package with pytest, ruff, and CI config." Agent does it. 45 minutes of guidance.
Session 2: "Set up a new Python package." Agent invents its own structure. Wrong test runner. Wrong lint config. Re-explain everything. 30 minutes.
Session 3: "Create a project skeleton like before." Agent asks: "What structure did you use?" Re-explain. 20 minutes.
Session 8: Gave up and did it myself. Faster than re-explaining for the eighth time.
```

The agent wasn't the problem. I was. I never saved the procedure.

By the end of this module, you'll have a skill system where:

- Every non-trivial procedure is saved once, used forever
- Your agent loads the right skill for the task automatically
- Discoveries from one session become permanent capabilities
- Your skill library grows every week — and so does your agent's competence

---

## The Pattern

### Copy-Pasteable Template

Start here. Fill in the bracketed fields, save as `SKILL.md` in your skills directory (`~/.hermes/skills/[category]/[skill-name]/` — or wherever your agent tool stores skills):

```markdown
---
name: [skill-name-lowercase-hyphens]
description: [One sentence — what this skill does]
triggers:
  - "[keyword that signals this task]"
  - "[another keyword]"
---

# [Skill Name]

## Trigger

Use when [specific situation].

## Steps

1. **[Step name]**
   ```bash
   [exact command]
   ```
   [Expected output or what to check]

2. **[Step name]**
   ```bash
   [exact command]
   ```

## Pitfalls

- **[Pitfall description]:** [exact fix]
- **[Another pitfall]:** [exact fix]

## Verification

[How to confirm the procedure worked — a health check, a test, a confirmation message]
```

### The Anatomy of a Skill

Every skill has four parts:

**1. Frontmatter (YAML)** — The metadata block between `---` delimiters.

```yaml
---
name: python-pypi-release        # Unique, lowercase, hyphens
description: Python package release checklist — PyPI classifiers, version bump, changelog, publish
triggers:                        # Keywords that signal "load this skill"
  - "release"
  - "publish to PyPI"
  - "bump version"
---
```

The triggers are the most important field. When the user says "publish the package," the agent scans available skills, finds a trigger match, and loads the skill automatically.

**2. Steps (numbered, exact commands)** — Every step should be copy-pasteable. If the agent needs to think, you haven't written the step clearly enough. Include exact commands, expected output, and what to do if the output differs.

**3. Pitfalls** — Every skill has edge cases. Document them. "Python 3.9 crashes — use python3.11." "The API returns 403 if the token is expired." These are the things you learned the hard way. Save them so the agent never learns them the hard way again.

**4. Verification** — How does the agent know the procedure worked? A health check, a test run, a confirmation message. Always include a way to verify.

### A Real Example: Python Package Release

Here's the full skill that handles Python PyPI releases — used dozens of times, zero errors:

```markdown
---
name: python-pypi-release
description: Python package release checklist — PyPI classifiers, version bump, changelog, publish
triggers:
  - "release"
  - "publish to PyPI"
  - "bump version"
  - "deploy package"
---

# Python PyPI Release

## Steps

1. **Verify version bump**
   ```bash
   grep version pyproject.toml
   ```
   Confirm it's higher than the last published version on PyPI.

2. **Update CHANGELOG.md**
   Add entry under new version header with today's date.
   Categories: Added, Changed, Fixed, Removed.

3. **Run full test suite**
   ```bash
   python3.11 -m pytest -n 4 -v
   ```
   All tests must pass. Stop here if they don't.

4. **Check with twine**
   ```bash
   python3.11 -m twine check dist/*
   ```
   Fix any warnings before proceeding.

5. **Upload to PyPI**
   ```bash
   python3.11 -m twine upload dist/*
   ```
   Requires PyPI token.

6. **Create git tag and push**
   ```bash
   git tag v$(python3.11 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
   git push origin --tags
   ```

7. **Verify on PyPI**
   Confirm the new version appears at the project's PyPI URL.

## Pitfalls

- **License classifier breaks pip:** Don't include "License :: OSI Approved ::" unless you have a LICENSE file — `pip install -e .` will fail.
- **Token expiry:** PyPI tokens expire. Check before starting.
- **Tag mismatch:** Always verify the git tag matches pyproject.toml version before pushing.
```

This skill is 57 lines. 15 minutes to write. Used dozens of times. Every time, the agent follows the exact procedure.

### Where Skills Live

Most AI coding agents use a standard location:

```
~/.hermes/skills/       # Hermes Agent
~/.claude/skills/       # Claude Code
~/.codex/skills/        # Codex
```

Check your tool's documentation. The directory structure inside is the same across tools:

```
skills/
├── [category]/           # Group by domain
│   └── [skill-name]/
│       └── SKILL.md      # The skill file — always named SKILL.md
```

Categories help the agent prioritise. A build failure loads skills from `software-development/`; an API call loads from `mlops/`. If you're unsure about categories, start with `general/` and split later.

### When to Create a Skill

**Create a skill when a task meets any of these criteria:**

- You've done it 3+ times (you'll do it again)
- It required 5+ tool calls to complete (complex enough to forget)
- You hit an error and found a fix (save the pitfall)
- It involves external services with specific API patterns (easy to get wrong)
- You want another agent — or another developer — to be able to do it without you

**Don't create a skill for:**

- One-off tasks you'll never repeat
- Trivial things the agent already does well ("run the tests")
- Tasks shorter than 3 steps — not worth a separate file

### The Skill Lifecycle

Skills aren't static. They evolve:

1. **Create** — Write SKILL.md. Test it in a fresh session.
2. **Use** — The skill loads when triggers match. You don't reference it directly.
3. **Patch** — Hit a new pitfall? Update the skill. Found a faster way? Update the skill. **After every complex task, ask: does the skill need updating?**
4. **Delete** — If a skill's been absorbed into another or the procedure is obsolete, remove it. Stale skills are dangerous — the agent follows them exactly as written.

A skill with wrong instructions cost me 45 minutes of debugging because the agent followed the stale procedure without question. I now have a rule: after any task that uses a skill, spend 60 seconds checking whether the skill needs a patch.

---

## Real Examples

### 1. Python Package Release (8.4 hours saved)

**Before skill:** 45 minutes per release, 3 errors, 1 failed PyPI upload. **After skill:** 3 minutes per release, zero errors. **Across 12 releases: 8.4 hours reclaimed.**

### 2. Build Failure Diagnosis (project-specific example)

Every codebase has build failures with known fixes. For SPFx SharePoint Framework — a Microsoft development framework — there are 6 common failure modes: CSS resolution errors, TypeScript version mismatches, Node version incompatibility, framework version drift, memory exhaustion during bundling, and manifest schema errors.

**Before skill:** Each build failure = 20-minute debugging session re-diagnosing the same 6 problems. **After skill:** Agent loads the diagnosis skill, matches error signature to known fix. 3 minutes per failure.

Your codebase has similar patterns. Whatever framework you use — React, Django, Spring Boot, whatever — the build failures are predictable. Write the skill once. Fix them in 3 minutes instead of 20.

### 3. The 153-Skill Library

Over 5 months, my skill library grew from 0 to 153. Not because I sat down and wrote 153 skills. Because every time the agent solved something hard, it saved the solution as a skill. That's Pattern 10 (Compounding) — but it only works if you understand skills first.

The first 10 skills are manual. After that, the agent starts creating its own.

---

## Common Pitfalls

| Pitfall | What happens | Fix |
|---------|--------------|-----|
| **Creating too few skills** | You re-explain procedures constantly | Be aggressive. 3+ uses = skill. 5+ tool calls = skill. |
| **Creating too many skills** | Library becomes noise — 500 one-line "skills" | Under 10 lines isn't a skill, it's a note. Keep it substantial. |
| **Stale skills** | Agent follows outdated procedures exactly — gets everything wrong | Patch after every use. 60 seconds. Check if anything changed. |
| **Vague triggers** | `triggers: ["work"]` — matches everything, skill loads constantly, burns context | Be specific. "SPFx build failure" not "build." "Python package release" not "release." |
| **No pitfalls section** | Agent hits the same errors every session | Every time you discover a fix, add it to the skill. This is the most valuable section. |
| **Verification missing** | Agent claims success but the procedure silently failed | Always include a "how to know it worked" step. |
| **Wrong directory** | Skill exists but the agent can't find it | Verify the skills directory path in your agent tool's config. Test a fresh session. |

---

## Try It Now

1. **Identify your first skill.** What procedure have you explained to your agent more than 3 times? Package releases? Database migrations? Deployment? Pick one.

2. **Copy the template** from the top of this module. Fill in the name, triggers, steps, pitfalls, and verification.

3. **Save it** as `SKILL.md` in your skills directory under an appropriate category. If you don't have a skills directory, create `~/.hermes/skills/[category]/[skill-name]/`.

4. **Test it.** Start a fresh agent session. Trigger the skill with a matching keyword — don't explain the procedure. The agent should load the skill and follow it.

5. **Patch it.** After the first use, something will be missing. A step you forgot. A pitfall you didn't document. Update the skill immediately.

**Time investment: 45 minutes for your first skill. Return: that procedure never needs explaining again.**

---

## What's Next

Pattern 3: **Memory** — Skills give your agent procedural knowledge (how to do things). Memory gives it durable context (what it already knows). Preferences, corrections, environment facts — remembered across sessions. The agent stops asking "what Python version?" because it already knows. You stop re-explaining yourself.

---

*Pattern 2 of 10. From the Works With Agents methodology — 153 skills written across 5 months of agent-assisted development.*
