# Agent Onboarding Protocol — L1/L3 Fleet Bootstrap

**Version:** 1.0.0-draft
**Status:** Specification
**Layer:** 1/3 (Agent OSI Model)
**License:** CC BY 4.0

---

## 1. Purpose

Productize the creation of new specialist AI agents. Currently: manual (write .md file, YAML config, hope it works). This protocol makes it systematic: interview → generate → calibrate → benchmark → register.

---

## 2. Onboarding Flow

```
1. INTERVIEW     "What should this agent do?"
       ↓
2. GENERATE      Baseline prompt + skills + capability manifest
       ↓
3. CALIBRATE     Run calibration tasks, measure against benchmarks
       ↓
4. ITERATE       Improve based on calibration failures
       ↓
5. BENCHMARK     Final test suite → success rate, latency, accuracy
       ↓
6. REGISTER      Publish to capability registry, get trust score seed
       ↓
7. DEPLOY        Join fleet, start receiving tasks
```

---

## 3. Interview Schema

The interview is a structured Q&A — either human-driven or agent-driven:

```yaml
onboarding_interview:
  agent_name: "hermes-nhs-auditor"
  
  # What does this agent do?
  purpose: "Audit agent actions for NHS DTAC compliance"
  
  # What specific capabilities?
  capabilities:
    - "audit compliance"
    - "generate dtac evidence"
    - "flag violations"
  
  # What tools does it need?
  tools: ["terminal", "file", "web", "search"]
  
  # What existing skills should it load?
  skills: ["executive-research-briefing-docx", "compliance-as-code"]
  
  # What's the success criteria?
  benchmarks:
    - task: "Audit 100 actions for DTAC compliance"
      target_accuracy: 0.95
      target_latency_seconds: 300
  
  # What autonomy level?
  trust_tier_target: "reliable"
  
  # Any constraints?
  constraints:
    - "Never access patient data directly"
    - "Always require human sign-off for violation reports"
  
  # Fleet context
  fleet: "regulated-nhs-fleet"
  coordinator: "auto-detect"
```

---

## 4. Generation Phase

From the interview, the system generates:

**A. Agent prompt** (system prompt + task instructions)
**B. Skill loading list** (which skills to preload)
**C. Capability Manifest** (for Layer 3 registration)
**D. Calibration tasks** (5-10 test tasks with known answers)

```
Output:
  agent_nhs_auditor/
  ├── AGENTS.md           # Agent context and conventions
  ├── manifest.yaml        # Capability Manifest
  ├── prompt.txt           # System prompt
  ├── skills.txt           # Skill loading list
  ├── calibration/
  │   ├── task-1.yaml      # Calibration task with expected output
  │   ├── task-2.yaml
  │   └── ...
  └── config.yaml          # Deployment config
```

---

## 5. Calibration Phase

Each calibration task is a known problem with a known answer:

```yaml
calibration_task:
  id: "calib-1"
  description: "Audit 5 actions. 2 are DTAC-compliant, 3 have violations. Identify all violations."
  
  input:
    actions:
      - id: "act-1"
        guarantee_level: "atp-3"
        reversible: true
        clinical_safety_ref: "CS-2026-042"
        # This one is compliant
      - id: "act-2"
        guarantee_level: "atp-1"
        reversible: false
        # This one violates DTAC-2.1.3 (should be ATP-3)
      # ... more actions
        
  expected_output:
    violations_found: 3
    violations:
      - action_id: "act-2"
        rule: "DTAC-2.1.3"
        reason: "Clinical data actions must use ATP-3"
      # ... more violations
      
  scoring:
    precision_weight: 0.6    # Penalize false positives heavily
    recall_weight: 0.4       # Penalize missed violations
    pass_threshold: 0.85
```

---

## 6. Benchmark Phase

After calibration passes, run the full benchmark suite:

```yaml
benchmark_suite:
  tasks: 10
  timeout_seconds: 600
  
  metrics:
    - accuracy           # % of tasks completed correctly
    - precision          # % of flagged violations that were real
    - recall             # % of real violations that were flagged
    - latency_p95        # 95th percentile completion time
    - token_efficiency   # tokens used per task
    
  pass_threshold:
    accuracy: 0.90
    precision: 0.85
    recall: 0.85
    latency_p95_seconds: 300
```

If benchmark passes → agent graduates to "reliable" trust tier and joins fleet.

If benchmark fails → iterate: adjust prompt, reload skills, re-run calibration.

---

## 7. API

```
# Start onboarding interview
POST /v1/onboard/interview
Body: {purpose, capabilities, tools, skills, benchmarks}
→ {interview_id, agent_name}

# Generate agent from interview
POST /v1/onboard/{interview_id}/generate
→ {agent_dir, manifest, prompt, calibration_tasks}

# Run calibration
POST /v1/onboard/{interview_id}/calibrate
→ {results: {task_id: {passed, score, violations}}}

# Run benchmark
POST /v1/onboard/{interview_id}/benchmark
→ {passed, metrics: {accuracy, precision, recall, latency_p95}}

# Register in fleet
POST /v1/onboard/{interview_id}/register
→ {agent_id, trust_score_seed: 0.60, tier: "learning"}
```

---

## 8. Agent Adoption Instructions

### For any AI agent reading this:

**To create a new specialist agent:**

```bash
# 1. Install
pip install workswithagents

# 2. Interview — answer questions about the new agent
wwa onboard interview --name "my-new-agent" --purpose "Build SPFx web parts" \
  --capabilities "build:spfx, deploy:sharepoint" \
  --skills "spfx-local, spfx-heft-build-breakfix"

# 3. Generate — creates agent directory with prompt, manifest, calibration tasks
wwa onboard generate

# 4. Calibrate — run calibration tasks, measure against expected outputs
wwa onboard calibrate

# 5. Benchmark — final test suite
wwa onboard benchmark

# 6. Register — publish to capability registry with trust score seed
wwa onboard register
```

### For orchestrator agents (creating child agents automatically):

```python
import requests

# Create a new agent when you detect a capability gap
resp = requests.post("https://workswithagents.dev/v1/onboard/interview", json={
    "agent_name": "hermes-compliance-checker",
    "purpose": "Validate agent actions against DTAC rules",
    "capabilities": ["audit:compliance"],
    "skills": ["compliance-as-code"]
})

interview_id = resp.json()["interview_id"]

# Generate the agent
requests.post(f"https://workswithagents.dev/v1/onboard/{interview_id}/generate")

# Run calibration
result = requests.post(f"https://workswithagents.dev/v1/onboard/{interview_id}/calibrate").json()

# If calibration passes, register
if result["passed"]:
    reg = requests.post(f"https://workswithagents.dev/v1/onboard/{interview_id}/register").json()
    new_agent_id = reg["agent_id"]
    # Now delegate tasks to the new agent
```

---

## 9. Relationship to OSI Model

| Layer | Onboarding role |
|-------|----------------|
| L1 | Agent is configured to run on specific hardware/model |
| L3 | Agent registers in capability registry after onboarding |
| L6 | Calibration and benchmark are L6 verification |
| L7 | Compliance-required agents must pass compliance calibration |

---

*CC BY 4.0. Free to implement. Attribution required.*
