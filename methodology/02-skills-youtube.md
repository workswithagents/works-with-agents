# YouTube Script: Pattern 2 — Skills

**Title:** "Stop Explaining The Same Thing To Your AI Agent"  
**Duration:** ~9 minutes  
**Style:** Screen recording + talking head

---

## HOOK (0:00 - 0:40)

[SCREEN: Fast montage of terminal sessions — same corrections repeated across different dates]

**VILIUS (voiceover):** "Session one: I explain how to publish a Python package. Forty-five minutes of guidance. Session two: same task, same agent — it's forgotten everything. Thirty more minutes. Session three: twenty minutes. Session eight: I give up and do it myself."

[SCREEN: Cut to talking head]

**VILIUS (on camera):** "This is the most common waste pattern with AI agents. You teach them something, they do it, and then they forget. Next session, you teach them again. Here's the fix — it's one file format, and it takes 15 minutes to write."

---

## THE CONCEPT (0:40 - 2:00)

[SCREEN: Animation — brain icon labelled "You" fading, file icon labelled "SKILL.md" appearing]

**VILIUS (voiceover):** "Right now, you're the skill library. Your brain holds all the procedures. The agent forgets everything when the session ends. The solution is to externalise those procedures into a standard format that the agent can load on demand — automatically."

[SCREEN: SKILL.md template appearing, each section highlighted]

**VILIUS (voiceover):** "A skill is a markdown file with YAML frontmatter. Four parts. One: metadata — name, description, and triggers. Keywords that tell the agent when to load it. Two: numbered steps with exact commands. Three: pitfalls — the edge cases you learned the hard way. Four: verification — how to confirm it worked."

---

## LIVE DEMO: Writing a Skill (2:00 - 5:00)

[SCREEN: VS Code — creating ~/skills/devops/python-pypi-release/SKILL.md]

**VILIUS (on camera):** "Let me show you a real one. This is the skill for publishing Python packages to PyPI. I wrote it once. It's been used dozens of times."

[SCREEN: Walk through the frontmatter]

**VILIUS (voiceover):** "The triggers are the key. When I say 'release the package' or 'publish to PyPI,' the agent finds this skill and loads it. I never have to say 'load the PyPI release skill' — it's automatic."

[SCREEN: Walk through each step — version check, changelog, tests, build, upload, tag]

**VILIUS (voiceover):** "Every step has an exact command. No thinking required. The agent follows the checklist. This is the difference between a procedure that works every time and one that requires you to supervise."

[SCREEN: Highlight pitfalls section]

**VILIUS (voiceover):** "This section is the most valuable. License classifier breaks pip install. Token expiry during upload. Tag mismatch with version. I learned all of these the hard way — each one cost me 10-20 minutes the first time. Now the agent knows them before it makes the mistake."

---

## THE NUMBERS (5:00 - 6:00)

[SCREEN: Before/after comparison graphic]

**VILIUS (on camera):** "Let me give you the actual numbers on this one skill. Before: 45 minutes per package release. Three errors per release on average. One failed PyPI upload because of an expired token."

[SCREEN: After comparison]

**VILIUS (voiceover):** "After the skill: 3 minutes per release. Zero errors. The agent catches the token expiry at step 4 — twine check — before it even tries to upload. Twelve releases later: 8.4 hours saved. One skill. Fifteen minutes to write."

---

## WHEN TO CREATE A SKILL (6:00 - 7:00)

[SCREEN: Decision tree graphic]

**VILIUS (on camera):** "Not everything needs to be a skill. Here's the rule: create a skill when you've done something three times, or it took more than five tool calls, or you hit an error and found a fix. Don't create skills for one-offs or trivial tasks."

[SCREEN: Skill lifecycle diagram — Create → Use → Patch → Delete]

**VILIUS (voiceover):** "Skills aren't static. They evolve. After every use, patch the skill if you found a new pitfall or a faster way. A stale skill is worse than no skill — the agent follows it exactly and gets everything wrong."

---

## THE COMPOUNDING EFFECT (7:00 - 8:00)

[SCREEN: Counter animation — 0 → 153 skills over 5 months]

**VILIUS (voiceover):** "Here's the part that changed everything for me. Once you have 10 skills, the agent starts creating its own. It solves a hard problem, saves the solution as a new skill. That's Pattern 10 — but it only works if you understand skills first."

[SCREEN: Screenshot of skills directory — 153 files]

**VILIUS (on camera):** "This is my actual skill library. 153 skills. I didn't write all of them. The agent wrote most of them — by following the skill format I taught it to use."

---

## OUTRO (8:00 - 9:00)

[SCREEN: Works With Agents logo]

**VILIUS (voiceover):** "Skills give your agent procedural knowledge — how to do things. In the next module, we add Memory — durable context. Preferences, corrections, facts — remembered across sessions. The agent stops asking what Python version to use because it already knows."

[SCREEN: Call to action — "Skill template at workswithagents.com/learn"]

**VILIUS (on camera):** "Your homework: pick one procedure you've explained more than three times. Write it as a skill. Use the template from the course page. Test it in a fresh session. That one skill will save you hours within a month. Guaranteed."

---

## PRODUCTION NOTES

- **B-roll:** Terminal sessions showing the skill being loaded and executed, VS Code creating SKILL.md
- **Graphics:** Skill anatomy diagram, before/after comparison cards, 0→153 counter animation, decision tree for "when to create a skill"
- **Music:** Minimal, ambient
- **Captions:** Important for the terminal demonstration sections
