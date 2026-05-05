"""
Works With Agents — Process Parser
=============================
Converts English business process descriptions into structured ProcessSpec
objects. Uses the Bastion LLM Gateway for inference (keeps data on-prem).
"""

import json
import re
from datetime import datetime, timezone
from .process_spec import (
    ProcessSpec, ProcessStep, TriggerType, ActionType
)

# ── Prompt template for the LLM ──────────────────────────────────────

SYSTEM_PROMPT = """You are a business process analyst specialising in {domain} sector automation.
Your job is to convert English descriptions of business processes into a precise,
machine-readable JSON specification for Power Automate workflow generation.

Output ONLY valid JSON with no markdown wrapping. The schema is:

{
  "name": "Short process name",
  "description": "One paragraph summary",
  "regulation_ref": "Specific law/regulation if applicable (e.g., GDPR Art.15, FOIA 2000, NHS DSP §4.2)",
  "trigger": {
    "type": "item_created|item_modified|manual|scheduled|form_submitted|email_received|webhook",
    "list": "SharePoint list name if applicable",
    "condition": "Optional trigger filter expression"
  },
  "steps": [
    {
      "id": "step_1",
      "action": "approval|notification|create_item|update_item|delete_item|condition|wait|escalation|log|transform|custom_http|send_email|teams_message",
      "label": "Human-readable description of this step",
      "target": "Who does this (job title or role)",
      "deadline_hours": 48,
      "condition": "Power Automate expression or null",
      "on_approve": "step_id or null",
      "on_reject": "step_id or null",
      "notification_template": "Template text with {placeholders} or null"
    }
  ],
  "compliance_checklist": ["Check 1", "Check 2"],
  "tags": ["tag1", "tag2"],
  "estimated_complexity": "simple|medium|complex"
}

Rules:
- Every step must have a unique id (step_1, step_2, etc.)
- approval actions MUST have on_approve and on_reject set
- escalation actions include a deadline_hours and target (the escalation recipient)
- Include an audit log step at the end of EVERY regulated process
- For {domain}: follow {domain_specific_guidance}
- Be precise. Missing a step is worse than adding an extra one."""

DOMAIN_GUIDANCE = {
    "nhs": """NHS DSP Toolkit alignment. IG-compliant. Steps must include:
- Data Protection Impact Assessment check where personal data is involved
- Caldicott Guardian approval for patient data
- Audit trail with date/time/user for every action
- Information Governance sign-off for data sharing""",
    "finance": """FCA and PRA compliance. Steps must include:
- Conflict of interest check before approvals
- Segregation of duties (requester ≠ approver)
- Record-keeping for FCA audit (5-year minimum)
- SMCR accountability assignment""",
    "government": """Central government digital standards. Steps must include:
- Equality Impact Assessment trigger where applicable
- FOI awareness flag (assume content may be FOI-able)
- Data handling classification (Official, Official-Sensitive, Secret)
- GDS Service Standard alignment for citizen-facing processes""",
    "general": """Standard business process best practices:
- Clear approval chains
- Deadline tracking
- Status updates at each stage
- Confirmation to requestor on completion"""
}


def _build_prompt(description: str, domain: str) -> str:
    """Build the full prompt for the LLM."""
    guidance = DOMAIN_GUIDANCE.get(domain, DOMAIN_GUIDANCE["general"])
    return SYSTEM_PROMPT.format(
        domain=domain, domain_specific_guidance=guidance
    ) + f"\n\nConvert this process to JSON:\n{description}"


def _parse_llm_response(raw_json: str) -> dict:
    """Extract valid JSON from LLM response (handles markdown wrapping)."""
    # Try direct parse first
    try:
        return json.loads(raw_json)
    except json.JSONDecodeError:
        pass

    # Try extracting from ```json blocks
    match = re.search(r'```(?:json)?\s*([\s\S]*?)```', raw_json)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try finding JSON object boundaries
    match = re.search(r'\{[\s\S]*\}', raw_json)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse LLM response as JSON: {raw_json[:200]}...")


def _spec_from_dict(data: dict, raw_input: str = "", model: str = "") -> ProcessSpec:
    """Convert parsed JSON dict to ProcessSpec."""

    trigger_data = data.get("trigger", {})
    trigger_type = TriggerType(trigger_data.get("type", "manual"))

    steps = []
    for s in data.get("steps", []):
        step = ProcessStep(
            id=s["id"],
            action=ActionType(s.get("action", "notification")),
            label=s.get("label", s["id"]),
            target=s.get("target"),
            deadline_hours=s.get("deadline_hours"),
            condition=s.get("condition"),
            on_approve=s.get("on_approve"),
            on_reject=s.get("on_reject"),
            notification_template=s.get("notification_template"),
        )
        steps.append(step)

    return ProcessSpec(
        name=data.get("name", "Unnamed Process"),
        description=data.get("description", ""),
        domain=data.get("domain", "general"),
        regulation_ref=data.get("regulation_ref"),
        trigger=trigger_type,
        trigger_list=trigger_data.get("list"),
        trigger_conditions=trigger_data.get("condition"),
        steps=steps,
        compliance_checklist=data.get("compliance_checklist", []),
        tags=data.get("tags", []),
        estimated_complexity=data.get("estimated_complexity", "medium"),
        raw_input=raw_input,
        generated_at=datetime.now(timezone.utc).isoformat(),
        model_used=model,
    )


class ProcessParser:
    """Converts English descriptions to ProcessSpec using LLM inference."""

    def __init__(self, gateway_url: str = "http://localhost:8443",
                 license_key: str = "", model: str = "agentic-qwen-8b"):
        self.gateway_url = gateway_url
        self.license_key = license_key
        self.model = model

    async def parse(self, description: str, domain: str = "general") -> ProcessSpec:
        """
        Convert an English process description to a structured ProcessSpec.

        Args:
            description: English description of the business process
            domain: One of 'nhs', 'finance', 'government', 'general'

        Returns:
            ProcessSpec with structured steps, triggers, and compliance data
        """
        import httpx

        prompt = _build_prompt(description, domain)

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.gateway_url}/v1/chat",
                headers={
                    "Content-Type": "application/json",
                    "X-License-Key": self.license_key,
                },
                json={
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": description}
                    ],
                    "model": self.model,
                    "temperature": 0.2,  # Low temp for structured output
                    "max_tokens": 4096,
                }
            )
            resp.raise_for_status()
            data = resp.json()

        raw_output = data["choices"][0]["message"]["content"]
        parsed = _parse_llm_response(raw_output)

        # Enforce domain in spec
        parsed["domain"] = domain

        return _spec_from_dict(parsed, raw_input=description, model=self.model)

    def parse_sync(self, description: str, domain: str = "general") -> ProcessSpec:
        """Synchronous wrapper for environments without async support."""
        import asyncio
        return asyncio.run(self.parse(description, domain))

    def parse_local(self, description: str, domain: str = "general") -> ProcessSpec:
        """
        Offline fallback — uses template matching to approximate a ProcessSpec
        without requiring a running LLM Gateway. Matches keywords in the
        description against the template library.
        """
        from .template_library import match_template

        # Try template matching first
        spec = match_template(description, domain)
        if spec:
            spec.raw_input = description
            spec.generated_at = datetime.now(timezone.utc).isoformat()
            spec.model_used = "template_matcher"
            return spec

        # Fallback: generate a minimal generic approval workflow
        return ProcessSpec(
            name="Custom Workflow",
            description=description,
            domain=domain,
            trigger=TriggerType.MANUAL,
            steps=[
                ProcessStep(id="step_1", action=ActionType.NOTIFICATION,
                           label=f"Process started: {description[:80]}...",
                           target="Process Owner"),
                ProcessStep(id="step_2", action=ActionType.APPROVAL,
                           label="Manual approval required",
                           target="Manager",
                           deadline_hours=72,
                           on_approve="step_3", on_reject="step_4"),
                ProcessStep(id="step_3", action=ActionType.NOTIFICATION,
                           label="Approved — notify requestor",
                           target="Requestor"),
                ProcessStep(id="step_4", action=ActionType.NOTIFICATION,
                           label="Rejected — notify requestor with reason",
                           target="Requestor"),
            ],
            raw_input=description,
            generated_at=datetime.now(timezone.utc).isoformat(),
            model_used="fallback_rule_engine",
        )
