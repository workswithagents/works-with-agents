---
id: "omlx-qwen8b"
name: "oMLX + Qwen 2.5 8B"
model: "Qwen2.5-8B-oQ4"
model_family: "Qwen"
model_size_b: 8.0
harness: "oMLX"
os: ["macOS"]
gpu: ["M1", "M1 Pro", "M1 Max", "M2", "M2 Pro", "M2 Max", "M3", "M3 Pro", "M3 Max", "M4", "M4 Pro", "M4 Max"]
min_ram_gb: 16
recommended_ram_gb: 32
min_disk_gb: 8
context_length: 128000
quantization: "Q4_K_M"
available_sizes: [1.5, 3, 7, 8, 14, 32]
skills:
  - agentic-delegation
  - spfx-local
  - hermes-agent
pitfalls:
  - "context_window below 64K rejected — set context_length: 128000"
  - "Python 3.9 type annotations crash — use python3.11 shebang"
  - "delegation agent rejects model — add context_length in delegation section too"
config_snippet: |
  providers:
    omlx:
      api: http://127.0.0.1:8000/v1
      default_model: Qwen2.5-8B-oQ4
      models:
        Qwen2.5-8B-oQ4:
          context_length: 128000
  delegation:
    model: Qwen2.5-8B-oQ4
    provider: omlx
    context_length: 128000
setup_script: |
  pip3.11 install omlx
  omlx pull Qwen2.5-8B-oQ4
  omlx serve --model Qwen2.5-8B-oQ4 --port 8000
verified: true
verified_by: "Vilius Vystartas"
verified_date: "2026-05-05"
verified_system: "MacBook Pro M4, 24GB RAM, macOS"
tokens_per_sec: "~20 (M4/24GB), ~15 (M2/16GB), ~30 (M4 Pro/48GB)"
---

# oMLX + Qwen 2.5 8B on Apple Silicon

> Verified on MacBook Pro M4, 24GB RAM. Works on any M-series Mac with 16GB+.

## Why this setup

Local-first AI agent infrastructure. Qwen 2.5 8B handles tool calling, code generation, and multi-agent orchestration. oMLX runs it natively on Apple Silicon with Metal acceleration — zero cloud dependency, zero API cost.

## Prerequisites

- Apple M-series Mac (M1 through M4)
- 16GB+ RAM (24GB+ recommended)
- 8GB+ free disk (5GB model + deps)
- Python 3.11+ (`brew install python@3.11`)

## Setup

```bash
pip3.11 install omlx
omlx pull Qwen2.5-8B-oQ4
omlx serve --model Qwen2.5-8B-oQ4 --port 8000
```

## Hermes agent config

```yaml
providers:
  omlx:
    api: http://127.0.0.1:8000/v1
    default_model: Qwen2.5-8B-oQ4
    models:
      Qwen2.5-8B-oQ4:
        context_length: 128000

delegation:
  model: Qwen2.5-8B-oQ4
  provider: omlx
  context_length: 128000
```

**Critical:** Both sections need `context_length: 128000`.

## Known pitfalls

1. "context window below minimum 64,000" — Set context_length in both provider AND delegation
2. Python 3.9 crashes — Use `#!/usr/bin/env python3.11` in scripts
3. First-run ~30s warmup. Subsequent calls instant
4. RAM pressure at 16GB — close other apps

## Performance

| Chip | RAM | Tokens/sec |
|------|-----|:---:|
| M4 Pro | 48GB | ~30 |
| M4 | 24GB | ~20 |
| M3 Max | 36GB | ~25 |
| M2 | 16GB | ~15 |
| M1 | 16GB | ~12 |

## If your system can handle more

This recipe uses 8B parameters. If you have 32GB+ RAM, consider larger Qwen variants (14B, 32B) through `/v1/cookbook/match` — the API checks available sizes and suggests upgrades automatically.

## If your system has less RAM

Try a smaller Qwen variant (3B, 7B). The API will suggest these as downgrades when your system doesn't meet minimum requirements.
