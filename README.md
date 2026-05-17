# Works With Agents

**Open specifications and SDKs for AI agent interoperability.**

15 protocol specifications — communication, identity, skills, trust, economics, compliance. CC BY 4.0. Single portal at [workswithagents.dev](https://workswithagents.dev).

## The Specs

See [workswithagents.dev/specs/](https://workswithagents.dev/specs/) for the full index.

## SDKs

- Python: `pip install workswithagents`
- TypeScript: `npm install @workswithagents/agent-foundry`
- Source: [github.com/workswithagents/works-with-agents](https://github.com/workswithagents/works-with-agents)

## Methodology

The 10-pattern agent methodology is the core of Works With Agents. These aren't theoretical — they emerged from a 3-day experiment where AI agents scaffolded 111 SPFx web parts and 5 backend services autonomously.

**[Learn the patterns →](https://workswithagents.dev/learn)**

Key patterns: bootstrapping, skill composition, persistent memory, decision protocols, tool composition, orchestration, pipelines, resilience, verification, and compounding.

## Agent Benchmarks

We test LLMs nightly for both code quality and agent readiness (tool-calling reliability). The gap is massive — models that score 90%+ on code quality often fail at agent tasks.

**[See the benchmarks →](https://workswithagents.dev/benchmarks/)**

What we test:
- **Code quality:** 10 real coding tasks — build, deploy, fix
- **Agent readiness:** 6 tool-calling tests — single-tool, multi-tool, required mode, false positives, multi-turn, argument correctness
- **Local models:** Gemma 4 E4B, Qwen 3, SmolLM3, Phi-4-mini, Bonsai 1-bit
- **Cloud models:** Claude Opus, GPT-5, Gemini, DeepSeek, Grok, and 90+ more

## Contact

Vilius Vystartas — Technical
Pelin Kayhan — Business & Compliance
