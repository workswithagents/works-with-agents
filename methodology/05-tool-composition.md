# Pattern 5: Tool Composition — Right Tool, Right Job

**Time to read:** 15 minutes  
**Time to apply:** Immediate — these are decisions you make every session  
**Prerequisites:** Patterns 1-4

---

## What Most People Do Wrong

They delegate everything to sub-agents. Every code change becomes a `delegate_task` call. Every file read spawns a new agent. The result: 600-second timeouts, garbage output, and a context window full of sub-agent summaries instead of actual work.

Or they do the opposite: run everything through the terminal. `cat` to read files. `sed` to edit them. `echo` to create them. Ten shell commands where a single `write_file` would do. The equivalent of building a house with a Swiss Army knife when there's a workshop next door.

Tool composition is knowing which tool for which job. Get it right, and your agent is surgical. Get it wrong, and you're burning tokens on sub-agents or fighting the terminal for 15 minutes.

---

## The Pattern

### The Tool Decision Matrix

| Task | Right tool | Wrong tool | Cost of wrong |
|------|-----------|------------|---------------|
| Read a file | `read_file` | `cat` in terminal | Missed line numbers, no pagination, can't handle binary |
| Search code | `search_files` | `grep -r` in terminal | Slower, no regex optimisation, no fuzzy matching |
| Edit a file | `patch` (targeted) | `sed` or full rewrite | Sed regex failures, overwriting unrelated code |
| Create a new file | `write_file` | `echo >>` in terminal | Escaping bugs, no syntax auto-check |
| Run a command | `terminal` | N/A — this IS the right tool for commands | — |
| Long computation | `execute_code` | Multiple terminal calls with intermediate files | Context pollution from intermediate outputs |
| Research task | `web_search` or `delegate_task` | Reading web pages in terminal | 15-minute manual browsing vs. 30-second research |
| Complex reasoning | Direct analysis | `delegate_task` | Sub-agent can't access your conversation context |
| Parallel work | `delegate_task` (batch) | Sequential direct work | 3x slower for independent streams |
| Code generation | Direct `write_file` | `delegate_task` | 600s timeouts, invented files, lost context |

### The Golden Rule

**Never delegate coding to a sub-agent.**

This was the most expensive lesson I learned. Sub-agents have no memory of your conversation. They don't know your project structure. They don't know your conventions. They can't use `patch` efficiently. They generate entire files instead of targeted edits.

The result: 600-second timeouts, invented directories, overwritten working code, and output that needs complete rewrites anyway. For coding tasks, use `write_file`, `patch`, `terminal` directly. Sub-agents are for research, parallel analysis, and reasoning-heavy tasks — not code generation.

### When to Use Each Tool

**`write_file`** — Creating new files. Also: overwriting a file completely when you know the full content. Syntax check runs automatically after write.

**`patch`** — Targeted edits to existing files. One change, one location. Don't rewrite a 500-line file for a 3-line change — `patch` is surgical.

**`terminal`** — Running commands: builds, installs, tests, git operations, server startups. Not for reading/editing files. Not for searching. Reserve for what only a shell can do.

**`search_files`** — Finding patterns in code, or finding files by name. Ripgrep-backed, faster than terminal grep, handles regex better.

**`read_file`** — Reading text files with line numbers and pagination. Handles large files with offset/limit. Can't read images — use vision tools for that.

**`delegate_task`** — Parallel independent workstreams. Research topic A + research topic B simultaneously. Code review as a separate agent. NOT for code generation. Sub-agents are isolated — they can't see your conversation, your files, or your corrections. Only the final summary reaches you.

**`execute_code`** — Python scripts that call multiple tools with processing logic between them. Use when you need 3+ tool calls with conditional logic, filtering, or loops. The 5-minute timeout means long-running tasks should use `terminal(background=true)` instead.

### The 30-Second vs. 15-Minute Trap

Here's the same task done wrong and right:

**Wrong (delegate_task for coding):**
```
User: "Add a health check endpoint to the API."
Agent: delegate_task(goal="Add health check endpoint")
Sub-agent: *invents new file structure, doesn't know the API framework, writes in wrong language, 600s timeout*
Result: 15 minutes wasted, complete rewrite needed.
```

**Right (direct tools):**
```
Agent: read_file("api/main.py", offset=1, limit=30) — sees FastAPI, sees existing endpoints
Agent: patch("api/main.py", old="existing endpoint block", new="existing + health check") — surgical edit
Agent: terminal("pytest tests/test_api.py::test_health -v") — verify
Result: 30 seconds, working code, tests pass.
```

Same task. One used the wrong tool — 15 minutes, garbage output. One used the right tools — 30 seconds, correct result.

---

## Real Examples

### The SPFx Catastrophe

Early on, I delegated an SPFx web part build to a sub-agent. The sub-agent:
- Didn't know SPFx requires specific Node versions
- Invented a `src/components/` directory that doesn't exist in SPFx projects
- Generated TypeScript that didn't match the SPFx API
- Timed out after 600 seconds with a 200-line "summary" that was 80% hallucinated

I spent 90 minutes undoing the damage. Then I wrote the `spfx-local` skill and stopped delegating framework-specific coding entirely. Direct tools + skills = 3-minute web part builds. Delegation = disaster.

### The Research Win

But delegation isn't bad — it's bad for code. For research, it's excellent:

```
delegate_task(goal="Research WebSocket rate limiting strategies for FastAPI")
→ Sub-agent searches 12 sources, produces a structured comparison
→ 3 minutes, high quality
```

The difference: research is information gathering. Coding is creation that needs project context. Sub-agents can gather information. They can't create in a context they don't have.

---

## Common Pitfalls

| Pitfall | What happens | Fix |
|---------|--------------|-----|
| **Delegating code generation** | Timeouts, hallucinations, invented structures | Use `write_file` + `patch` directly. Sub-agents are for research, not code. |
| **Using terminal for file ops** | `cat 5000-line-file` floods context, `sed` breaks on edge cases | `read_file` for reading, `patch` for editing, `write_file` for creating. |
| **Using write_file for 1-line edits** | Context window fills with entire file content unnecessarily | `patch` — surgical, efficient, one change at a time |
| **Sequential when parallel is possible** | Research A waits for research B — doubles time | `delegate_task` batch mode: 3 research tasks in parallel |
| **Direct analysis for parallel work** | Your context window fills with intermediate data from 3 streams | Delegate analysis-heavy subtasks, keep your context clean |
| **Never using execute_code** | 8 sequential tool calls with manual processing between each | `execute_code` for 3+ tool calls with filtering/looping |

---

## Try It Now

1. **Audit your last session.** Did you delegate code generation? Stop. Rewrite those tasks using direct tools.
2. **Learn the decision matrix.** Bookmark the table above. When your agent reaches for a tool, check: is this the right one?
3. **Use `patch` for your next edit.** Not `write_file` for the whole file. Not `sed` in terminal. `patch` — surgical, efficient.

**Time investment: zero — these are decisions you make in every session. Return: 15-minute coding tasks become 30 seconds when the right tool is used.**

---

## What's Next

Pattern 6: **Orchestration** — Now you know which tools to use. But what about when the work is too big for one agent? Multi-agent orchestration: splitting complex work across specialist agents working in parallel.

---

*Pattern 5 of 10. From the Works With Agents methodology.*
