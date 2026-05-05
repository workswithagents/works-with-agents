# Pattern 1: Boot — The First Session That Makes Every Other Session Work

**Time to read:** 15 minutes  
**Time to apply:** 30 minutes  
**Prerequisites:** An AI coding agent installed (Claude Code, Codex, Hermes, or similar)

---

## What Most People Do Wrong

They open a terminal, type a prompt, and start coding. The agent has no idea what project it's in, what Python version to use, what the coding conventions are, or where anything lives. Every command needs qualification. Every tool call needs vetting.

The result: an hour of "use python3.11 not python3" corrections, "the tests are in the tests/ directory" reminders, and "no, don't deploy to production" interventions. By the time the agent is oriented, you've burned half the session.

I did this for months. Every session started from zero. I'd explain the project structure, the Python path, the testing conventions, the deployment rules — over and over. It was like onboarding a new developer every morning, except the developer had perfect memory of everything except what you told them yesterday.

## What You'll Learn

By the end of this module, you'll have a boot script that:

- Tells your agent exactly what project it's working on
- Provides environment details (language versions, paths, dependencies)
- Sets ground rules for autonomy (when to ask, when to proceed)
- Includes project-specific conventions (test commands, lint rules, build steps)
- Makes session two faster than session one by a factor of 10

The boot pattern is the foundation. Skip it, and every other pattern in this methodology is harder than it needs to be.

---

## The Pattern

### Option A: The 5-Field Template (No Code Required)

If you don't want to run a script, fill in these 5 fields and save as `AGENTS.md` in your project root:

```markdown
# AGENTS.md — [YOUR PROJECT NAME]

[ONE SENTENCE: what this project is]

## Stack

- [LANGUAGE + EXACT VERSION] at [EXACT PATH]
  Example: Python 3.11 at /opt/homebrew/bin/python3.11
- [ADD ANY OTHER CRITICAL TOOLS — Node, Docker, database]

## Conventions

- Run tests with: [EXACT COMMAND]
- Lint with: [EXACT COMMAND]
- [GIT WORKFLOW RULE]
- [DEPLOYMENT RULE — e.g. "Never deploy without passing tests"]
- [AUTONOMY RULE — e.g. "Proceed without asking on non-destructive changes"]

## Key files

- `[PATH TO MAIN ENTRY POINT]`
- `[PATH TO TESTS]`
- `[PATH TO CONFIG]`
- `[PATH TO DOCS]`
- `[ANY OTHER CRITICAL FILE]`
```

That's it. 5 fields, 10 minutes. This alone will save you hours of corrections.

### Option B: Environment Discovery Script (Automated)

For projects where the environment changes frequently — or for teams where multiple developers each have different setups — generate AGENTS.md from current environment state:

```python
#!/usr/bin/env python3.11
"""Generate AGENTS.md from current environment."""
import subprocess, sys, os
from pathlib import Path

def discover():
    """Discover the current environment."""
    env = {
        "python": sys.executable,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "node": None,
        "node_version": None,
        "docker": None,
        "git_branch": None,
    }

    # Discover Node
    try:
        node = subprocess.run(["which", "node"], capture_output=True, text=True)
        if node.returncode == 0:
            env["node"] = node.stdout.strip()
            v = subprocess.run(["node", "--version"], capture_output=True, text=True)
            env["node_version"] = v.stdout.strip()
    except Exception:
        pass

    # Discover git branch
    try:
        branch = subprocess.run(["git", "branch", "--show-current"],
                                capture_output=True, text=True)
        if branch.returncode == 0:
            env["git_branch"] = branch.stdout.strip()
    except Exception:
        pass

    return env

def generate_agents_md(project_name, description, env, key_files, conventions):
    """Generate AGENTS.md content."""
    lines = [
        f"# AGENTS.md — {project_name}",
        "",
        description,
        "",
        "## Stack",
        "",
        f"- Python {env['python_version']} at {env['python']}",
    ]
    if env["node"]:
        lines.append(f"- Node {env['node_version']} via {env['node']}")
    if env["git_branch"]:
        lines.append(f"- Current branch: {env['git_branch']}")

    lines.extend(["", "## Conventions", ""])
    for c in conventions:
        lines.append(f"- {c}")

    lines.extend(["", "## Key files", ""])
    for f in key_files:
        lines.append(f"- `{f}`")

    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    env = discover()
    content = generate_agents_md(
        project_name="My Project",
        description="Brief description of what this project is.",
        env=env,
        key_files=["src/main.py", "tests/test_main.py", "pyproject.toml"],
        conventions=[
            "Run tests with: python3.11 -m pytest -v",
            "Lint with: ruff check src/ tests/",
            "Never commit to main directly — use feature branches",
            "Proceed without asking on non-destructive changes",
        ]
    )
    Path("AGENTS.md").write_text(content)
    print("AGENTS.md generated successfully.")
    print(f"  Python: {env['python_version']} at {env['python']}")
    if env['node']:
        print(f"  Node:   {env['node_version']}")
    if env['git_branch']:
        print(f"  Branch: {env['git_branch']}")
```

Run `python3.11 generate_agents_md.py` after environment changes. The output confirms what was discovered.

### Step 3: First-Session Protocol

When you start a session with a booted agent, follow this protocol:

1. **Ensure the agent reads AGENTS.md.** Most tools (Claude Code, Hermes, Codex) auto-inject AGENTS.md into the system prompt when you're in a project directory. If your tool doesn't, start every session with: *"Read AGENTS.md in this directory first."*

2. **State the goal with precision.** Not "work on the project" — "Add rate limiting to the LLM proxy endpoint with configurable tokens-per-minute, and write tests for the new rate limiter."

3. **Set the autonomy level.** This is the most important sentence you'll type in the session:
   - *"Proceed without asking for approval on non-destructive changes."* (confident)
   - *"Ask before any file modification."* (cautious — good for unfamiliar codebases)
   - *"Decide and execute — only pause if you hit something that could break production."* (for seasoned agent users)

4. **Confirm understanding.** Ask: *"Summarise what you know about this project from AGENTS.md."* If the agent gets anything wrong, fix it now — not after 30 minutes of work.

### Step 4: The Bootstrap Self-Test

After creating AGENTS.md, verify it works. Start a fresh agent session and ask:

*"What Python version should you use for this project, and what's the test command?"*

If the agent answers correctly from AGENTS.md — without accessing the file system — your boot is working. If it guesses or asks, your AGENTS.md isn't specific enough, or your tool doesn't auto-inject it. Fix either.

---

## Real Examples

### Before Boot (my first month)

```
Session 1: "Use python3.11" — 4 corrections about Python version
Session 2: "The tests are in tests/" — 3 corrections about paths
Session 3: "Don't commit to main" — 2 corrections about git workflow
Session 4: Agent used python3 instead of python3.11 — broken build
Session 5: Agent invented a test directory at src/tests/ — cleanup needed
```

Average session: 15 minutes of orientation before actual work. Over a month of daily sessions, that's ~7 hours spent just orienting the agent.

### After Boot

```
Session 1: Agent reads AGENTS.md, uses correct Python, runs correct tests, commits to feature branch. Zero corrections.
Session 2: Same. Zero corrections.
Session 3: Same. One minor path correction because I moved the tests directory and hadn't updated AGENTS.md.
```

Average session: 30 seconds of orientation. The other 14.5 minutes are actual work. Over a month: 7 hours reclaimed.

---

## Multiple Environments

If your project has dev, staging, and production environments, AGENTS.md can handle that. Add an environments section:

```markdown
## Environments

| Environment | Branch | Database | Deploy Command |
|-------------|--------|----------|----------------|
| dev | develop | localhost:5432/mydb_dev | `make deploy-dev` |
| staging | staging | staging-db.internal:5432/mydb | `make deploy-staging` |
| production | main | NEVER DIRECTLY ACCESS | `make deploy-prod` |

**⚠️ Never run destructive commands against production without explicit confirmation.**
```

This prevents the agent from running a migration against the wrong database or deploying a feature branch to production.

## Compliance Boundaries (Regulated Industries)

For teams in finance, healthcare, or government — where an agent's mistake could have regulatory consequences — add explicit boundaries to AGENTS.md:

```markdown
## Compliance Boundaries

- **Never** access, modify, or read files in `patient-data/` or `financial-records/`
- **Never** make external API calls to services not listed in the approved services list
- **Never** commit credentials, API keys, or personally identifiable information
- All data processing must occur within the approved environment — no uploading to external LLM providers
- Agent must log all file modifications for audit purposes
```

Your agent won't enforce these by itself — that comes in Pattern 9 (Verify). But stating the boundaries upfront makes violations harder and gives you a clear reference point when reviewing agent work.

---

## Common Pitfalls

| Pitfall | What happens | Fix |
|---------|--------------|-----|
| **Vague paths** | "Python" instead of "Python 3.11 at /opt/homebrew/bin/python3.11" | Be specific. Give the agent the exact path. The agent can't read your mind and won't guess correctly. |
| **Missing conventions** | Agent invents its own workflow — wrong test runner, wrong lint tool, wrong commit style | Document every command you've ever corrected the agent on |
| **Stale AGENTS.md** | Agent uses old paths after you reorganise directories | Re-run the generator or update manually after structural changes. Add it to your pre-commit hook. |
| **Over-documenting** | 50-page AGENTS.md that the agent skims without absorbing | Keep it to what the agent actually needs: stack, conventions, key files, boundaries. Move architecture docs to a separate file. |
| **No autonomy rules** | Agent asks permission for every file write, every test run, every commit | Add: "Proceed without approval on non-destructive changes" — this alone transforms agent speed |
| **Skipping the self-test** | You assume AGENTS.md works, but the agent can't actually read it or the path is wrong | Always start a fresh session and test after modifying AGENTS.md |
| **Tool doesn't auto-read AGENTS.md** | Agent has no project context at all | Start every session with "Read AGENTS.md first." Better: switch to a tool that supports it (most do now). |

---

## Try It Now

1. **If you have 10 minutes:** Use Option A (the 5-field template). Fill in project name, language path, 3 conventions, 3 key files. Save as `AGENTS.md` in your project root.

2. **If you have 25 minutes:** Use Option B (the Python script). Paste it, update the project name and key files, run it.

3. Start a fresh agent session in your project directory. Ask: *"What Python version should you use for this project?"*

4. If the agent answers correctly without probing the filesystem — you now have a booted agent. Every session from here is faster.

5. If it doesn't work: check that AGENTS.md is in the right directory, the path is exact, and your tool supports auto-injection. Fix and retest.

**Time investment: 10-25 minutes. Return: 15 minutes saved per session, forever.**

---

## What's Next

Pattern 2: **Skills** — AGENTS.md gives your agent static project knowledge. Skills give it dynamic, load-on-demand expertise. When your agent encounters a task it's done before — running SPFx builds, deploying to Cloudflare, setting up a Python package — it loads the skill instead of figuring it out from scratch. Skills are how your agent gets faster every session.

---

*Pattern 1 of 10. From the Works With Agents methodology — developed through hands-on agent-assisted development of 111 SPFx web parts and 5 backend services.*
