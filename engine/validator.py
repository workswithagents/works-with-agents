"""
Works With Agents — Validator
========================
Validates generated Power Automate flow JSON and ProcessSpec objects.
Catches LLM hallucinations, missing required fields, and structural errors
before deployment to Microsoft Graph.
"""

import json
from typing import Optional

from .process_spec import ProcessSpec, ProcessStep, TriggerType, ActionType


class ValidationError:
    """A single validation issue found."""
    def __init__(self, code: str, message: str, path: str = ""):
        self.code = code
        self.message = message
        self.path = path

    def __str__(self):
        loc = f" ({self.path})" if self.path else ""
        return f"[{self.code}]{loc} {self.message}"


class ValidationResult:
    """Collection of validation issues."""
    def __init__(self):
        self.errors: list[ValidationError] = []
        self.warnings: list[ValidationError] = []

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    def error(self, code: str, message: str, path: str = ""):
        self.errors.append(ValidationError(code, message, path))

    def warning(self, code: str, message: str, path: str = ""):
        self.warnings.append(ValidationError(code, message, path))

    def __str__(self):
        parts = []
        if self.errors:
            parts.append(f"❌ {len(self.errors)} errors:")
            for e in self.errors:
                parts.append(f"  {e}")
        if self.warnings:
            parts.append(f"⚠️  {len(self.warnings)} warnings:")
            for w in self.warnings:
                parts.append(f"  {w}")
        if not parts:
            parts.append("✅ Valid — no issues found")
        return "\n".join(parts)


def validate_spec(spec: ProcessSpec) -> ValidationResult:
    """Validate a ProcessSpec for completeness and correctness."""
    result = ValidationResult()

    # ── Required top-level fields ─────────────────────────────────────
    if not spec.name or len(spec.name.strip()) < 3:
        result.error("SPEC-001", "Process name must be at least 3 characters", "name")

    if not spec.description or len(spec.description.strip()) < 10:
        result.error("SPEC-002", "Description must be at least 10 characters", "description")

    if spec.domain not in ("nhs", "finance", "government", "general"):
        result.error("SPEC-003", f"Unknown domain: {spec.domain}", "domain")

    # ── Steps validation ──────────────────────────────────────────────
    if not spec.steps:
        result.error("SPEC-004", "Process must have at least one step", "steps")

    step_ids = set()
    approval_count = 0
    has_log = False
    has_deadline = False

    for i, step in enumerate(spec.steps):
        path_prefix = f"steps[{i}]({step.id})"

        # Duplicate IDs
        if step.id in step_ids:
            result.error("SPEC-005", f"Duplicate step ID: {step.id}", path_prefix)
        step_ids.add(step.id)

        # Empty label
        if not step.label or len(step.label.strip()) < 3:
            result.warning("SPEC-006", f"Step label is too short", path_prefix)

        # Missing targets for human-required actions
        if step.action in (ActionType.APPROVAL, ActionType.NOTIFICATION,
                          ActionType.SEND_EMAIL, ActionType.TEAMS_MESSAGE,
                          ActionType.ESCALATION):
            if not step.target:
                result.warning("SPEC-007",
                    f"Step '{step.id}' ({step.action}) has no target — who performs this?",
                    path_prefix)

        # Approval must have routing
        if step.action == ActionType.APPROVAL:
            approval_count += 1
            if not step.on_approve and not step.on_reject:
                result.warning("SPEC-008",
                    f"Approval step '{step.id}' has no on_approve/on_reject routing",
                    path_prefix)

        # Escalation should have deadline
        if step.action == ActionType.ESCALATION:
            has_deadline = has_deadline or (step.deadline_hours is not None)

            if not step.deadline_hours:
                result.warning("SPEC-009",
                    f"Escalation step '{step.id}' has no deadline — when does it escalate?",
                    path_prefix)

        # Deadlines
        if step.deadline_hours:
            has_deadline = True
            if step.deadline_hours <= 0:
                result.error("SPEC-010",
                    f"Deadline must be positive: {step.deadline_hours}h", path_prefix)

        # Log tracking
        if step.action == ActionType.LOG:
            has_log = True

    # ── Process-level checks ──────────────────────────────────────────
    if spec.regulation_ref:
        # Check regulation references look plausible
        valid_refs = ["GDPR", "FOIA", "FOI", "DPA", "NHS", "DSP", "FCA", "PRA",
                      "PIDA", "Equality Act", "SMCR", "GDS", "LFPSE"]
        if not any(ref in spec.regulation_ref for ref in valid_refs):
            result.warning("SPEC-011",
                f"Unrecognised regulation reference: '{spec.regulation_ref}'",
                "regulation_ref")

    # Every regulated process should have an audit log
    if spec.domain != "general" and not has_log:
        result.warning("SPEC-012",
            f"Regulated process ({spec.domain}) has no audit log step — required for compliance",
            "steps")

    # Compliance checklist populated
    if spec.domain != "general" and not spec.compliance_checklist:
        result.warning("SPEC-013",
            "Compliance checklist is empty for regulated process",
            "compliance_checklist")

    # ── Domain-specific checks ────────────────────────────────────────
    if spec.domain == "nhs":
        # NHS processes should reference DSP or specific regulations
        nhs_refs = ["DSP", "NHS", "Caldicott", "IG Toolkit", "patient", "clinical"]
        if not any(ref.lower() in (spec.regulation_ref or "").lower() for ref in nhs_refs):
            result.warning("SPEC-NHS-001",
                "NHS process should reference DSP Toolkit, Caldicott, or specific NHS regulations",
                "regulation_ref")

    if spec.domain == "finance":
        finance_refs = ["FCA", "PRA", "SMCR", "GDPR", "MiFID", "AML"]
        if not any(ref in (spec.regulation_ref or "") for ref in finance_refs):
            result.warning("SPEC-FIN-001",
                "Finance process should reference FCA, PRA, SMCR, or specific regulations",
                "regulation_ref")

    # ── Quality heuristics ────────────────────────────────────────────
    if len(spec.steps) < 3 and spec.estimated_complexity != "simple":
        result.warning("SPEC-Q01",
            f"Process has {len(spec.steps)} steps but complexity is {spec.estimated_complexity}",
            "estimated_complexity")

    if approval_count == 0 and spec.domain != "general":
        result.warning("SPEC-Q02",
            "Regulated process has no approval step — is this intentional?",
            "steps")

    return result


def validate_flow_json(flow_json: dict) -> ValidationResult:
    """Validate a Power Automate flow JSON structure."""
    result = ValidationResult()

    # Check required top-level structure
    required_keys = ["properties"]
    for key in required_keys:
        if key not in flow_json:
            result.error("FLOW-001", f"Missing required key: '{key}'", key)

    props = flow_json.get("properties", {})

    # Display name
    if not props.get("displayName"):
        result.error("FLOW-002", "Flow has no displayName", "properties.displayName")

    # Definition
    definition = props.get("definition", {})
    if not definition:
        result.error("FLOW-003", "Flow has no definition", "properties.definition")
        return result

    # Triggers
    triggers = definition.get("triggers", {})
    if not triggers:
        result.error("FLOW-004", "Flow has no triggers", "properties.definition.triggers")

    # Actions
    actions = definition.get("actions", {})
    if not actions:
        result.warning("FLOW-005", "Flow has no actions", "properties.definition.actions")

    # Check each action references valid predecessors
    action_ids = set(actions.keys())
    for action_id, action in actions.items():
        run_after = action.get("runAfter", {})
        for dep_id in run_after:
            if dep_id not in action_ids and dep_id not in triggers:
                result.warning("FLOW-006",
                    f"Action '{action_id}' depends on unknown action '{dep_id}'",
                    f"properties.definition.actions.{action_id}.runAfter")

    # Schema
    schema = definition.get("$schema", "")
    if "schema.management.azure.com" not in schema:
        result.warning("FLOW-007",
            f"Unusual schema URL: {schema}",
            "properties.definition.$schema")

    return result
