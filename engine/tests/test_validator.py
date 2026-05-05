"""
Tests for validator.py — ProcessSpec and Power Automate flow validation.
"""
import pytest
from engine.process_spec import (
    ProcessSpec, ProcessStep, TriggerType, ActionType
)
from engine.validator import (
    ValidationResult, ValidationError,
    validate_spec, validate_flow_json,
)


class TestValidationResult:
    def test_empty_is_valid(self):
        result = ValidationResult()
        assert result.is_valid
        assert not result.has_warnings

    def test_error_makes_invalid(self):
        result = ValidationResult()
        result.error("TEST-001", "Something went wrong")
        assert not result.is_valid

    def test_warnings_alone_still_valid(self):
        result = ValidationResult()
        result.warning("TEST-W01", "Just a heads up")
        assert result.is_valid
        assert result.has_warnings

    def test_str_formatting(self):
        result = ValidationResult()
        result.error("E1", "Error message", "field.x")
        result.warning("W1", "Warning message")
        output = str(result)
        assert "❌" in output
        assert "⚠️" in output
        assert "E1" in output
        assert "W1" in output

    def test_empty_str_shows_valid(self):
        result = ValidationResult()
        assert "✅" in str(result)


def _make_spec(name="Test", description="Test process description", domain="general",
               steps=None, regulation_ref=None, compliance_checklist=None, **kwargs):
    return ProcessSpec(
        name=name,
        description=description,
        domain=domain,
        regulation_ref=regulation_ref,
        steps=steps or [],
        compliance_checklist=compliance_checklist or [],
        **kwargs
    )


class TestValidateSpec:
    def test_empty_name(self):
        spec = _make_spec(name="Ab", description="Valid description here")
        result = validate_spec(spec)
        assert not result.is_valid
        assert any(e.code == "SPEC-001" for e in result.errors)

    def test_short_description(self):
        spec = _make_spec(name="Valid Name", description="Short")
        result = validate_spec(spec)
        assert not result.is_valid
        assert any(e.code == "SPEC-002" for e in result.errors)

    def test_unknown_domain(self):
        spec = _make_spec(name="Valid Name", description="Valid description text", domain="aerospace")
        result = validate_spec(spec)
        assert not result.is_valid
        assert any(e.code == "SPEC-003" for e in result.errors)

    def test_no_steps(self):
        spec = _make_spec(name="Valid Name", description="Valid description text")
        result = validate_spec(spec)
        assert not result.is_valid
        assert any(e.code == "SPEC-004" for e in result.errors)

    def test_duplicate_step_ids(self):
        steps = [
            ProcessStep(id="dup", action=ActionType.LOG, label="First"),
            ProcessStep(id="dup", action=ActionType.NOTIFICATION, label="Second"),
        ]
        spec = _make_spec(steps=steps)
        result = validate_spec(spec)
        assert not result.is_valid
        assert any(e.code == "SPEC-005" for e in result.errors)

    def test_approval_without_target(self):
        steps = [
            ProcessStep(id="s1", action=ActionType.APPROVAL, label="Approve something"),
        ]
        spec = _make_spec(steps=steps)
        result = validate_spec(spec)
        assert result.has_warnings
        assert any(w.code == "SPEC-007" for w in result.warnings)

    def test_approval_without_routing(self):
        steps = [
            ProcessStep(id="s1", action=ActionType.APPROVAL, label="Approve", target="Manager"),
        ]
        spec = _make_spec(steps=steps)
        result = validate_spec(spec)
        assert result.has_warnings
        assert any(w.code == "SPEC-008" for w in result.warnings)

    def test_escalation_without_deadline(self):
        steps = [
            ProcessStep(id="s1", action=ActionType.ESCALATION, label="Escalate", target="Director"),
        ]
        spec = _make_spec(steps=steps)
        result = validate_spec(spec)
        assert result.has_warnings
        assert any(w.code == "SPEC-009" for w in result.warnings)

    def test_negative_deadline(self):
        steps = [
            ProcessStep(id="s1", action=ActionType.WAIT, label="Wait", deadline_hours=-5),
        ]
        spec = _make_spec(steps=steps)
        result = validate_spec(spec)
        assert not result.is_valid
        assert any(e.code == "SPEC-010" for e in result.errors)

    def test_regulated_no_audit_log(self):
        steps = [
            ProcessStep(id="s1", action=ActionType.NOTIFICATION, label="Notify", target="User"),
            ProcessStep(id="s2", action=ActionType.APPROVAL, label="Approve", target="Manager",
                       on_approve="s3", on_reject="s3"),
        ]
        spec = _make_spec(domain="nhs", steps=steps, regulation_ref="GDPR Art.35",
                         compliance_checklist=["Check 1"])
        result = validate_spec(spec)
        # Should warn about no audit log for regulated process
        assert result.has_warnings
        assert any(w.code == "SPEC-012" for w in result.warnings)

    def test_regulated_no_compliance_checklist(self):
        steps = [
            ProcessStep(id="s1", action=ActionType.LOG, label="Log entry"),
            ProcessStep(id="s2", action=ActionType.APPROVAL, label="Approve", target="Mgr",
                       on_approve="s3", on_reject="s3"),
        ]
        spec = _make_spec(domain="finance", steps=steps, regulation_ref="FCA")
        result = validate_spec(spec)
        assert result.has_warnings
        assert any(w.code == "SPEC-013" for w in result.warnings)

    def test_valid_simple_process(self):
        steps = [
            ProcessStep(id="s1", action=ActionType.LOG, label="Log start"),
            ProcessStep(id="s2", action=ActionType.NOTIFICATION, label="Notify", target="Admin"),
        ]
        spec = _make_spec(domain="general", steps=steps)
        result = validate_spec(spec)
        assert result.is_valid

    def test_valid_regulated_process(self):
        steps = [
            ProcessStep(id="s1", action=ActionType.LOG, label="Log request"),
            ProcessStep(id="s2", action=ActionType.APPROVAL, label="DPO review", target="DPO",
                       on_approve="s3", on_reject="s3"),
            ProcessStep(id="s3", action=ActionType.LOG, label="Record outcome"),
        ]
        spec = _make_spec(
            domain="nhs",
            steps=steps,
            regulation_ref="UK GDPR Art.35, NHS DSP Toolkit §4.1",
            compliance_checklist=["Identity verified", "DPO consulted"],
        )
        result = validate_spec(spec)
        assert result.is_valid

    def test_nhs_without_nhs_regulation_ref(self):
        steps = [
            ProcessStep(id="s1", action=ActionType.LOG, label="Log"),
        ]
        spec = _make_spec(domain="nhs", steps=steps, regulation_ref="GDPR Art.6")
        result = validate_spec(spec)
        assert result.has_warnings
        assert any(w.code == "SPEC-NHS-001" for w in result.warnings)

    def test_finance_without_finance_regulation_ref(self):
        steps = [
            ProcessStep(id="s1", action=ActionType.LOG, label="Log"),
        ]
        spec = _make_spec(domain="finance", steps=steps, regulation_ref="SomeOtherAct")
        result = validate_spec(spec)
        assert any(w.code == "SPEC-FIN-001" for w in result.warnings)

    def test_unrecognised_regulation(self):
        steps = [
            ProcessStep(id="s1", action=ActionType.LOG, label="Log"),
        ]
        spec = _make_spec(steps=steps, regulation_ref="MadeUpAct 2025")
        result = validate_spec(spec)
        assert any(w.code == "SPEC-011" for w in result.warnings)

    def test_complexity_mismatch(self):
        steps = [
            ProcessStep(id="s1", action=ActionType.LOG, label="Do something"),
        ]
        spec = _make_spec(steps=steps, estimated_complexity="complex")
        result = validate_spec(spec)
        assert any(w.code == "SPEC-Q01" for w in result.warnings)


class TestValidateFlowJson:
    def test_valid_flow(self):
        flow = {
            "properties": {
                "displayName": "Test Flow",
                "definition": {
                    "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
                    "contentVersion": "1.0.0.0",
                    "parameters": {},
                    "triggers": {
                        "manual": {"type": "Request", "kind": "Button", "inputs": {}}
                    },
                    "actions": {
                        "step_1": {"type": "Compose", "inputs": "Hello", "runAfter": {}}
                    },
                    "outputs": {},
                },
                "state": "Started",
            }
        }
        result = validate_flow_json(flow)
        assert result.is_valid

    def test_missing_properties(self):
        result = validate_flow_json({})
        assert not result.is_valid
        assert any(e.code == "FLOW-001" for e in result.errors)

    def test_no_display_name(self):
        flow = {
            "properties": {
                "definition": {"triggers": {}, "actions": {}}
            }
        }
        result = validate_flow_json(flow)
        assert not result.is_valid
        assert any(e.code == "FLOW-002" for e in result.errors)

    def test_no_triggers(self):
        flow = {
            "properties": {
                "displayName": "Test",
                "definition": {"actions": {}}
            }
        }
        result = validate_flow_json(flow)
        assert not result.is_valid
        assert any(e.code == "FLOW-004" for e in result.errors)

    def test_no_actions_warns(self):
        flow = {
            "properties": {
                "displayName": "Test",
                "definition": {"triggers": {"manual": {"type": "Request"}}}
            }
        }
        result = validate_flow_json(flow)
        # No actions is a warning, not an error
        assert result.has_warnings
        assert any(w.code == "FLOW-005" for w in result.warnings)

    def test_broken_dependency(self):
        flow = {
            "properties": {
                "displayName": "Test",
                "definition": {
                    "$schema": "https://schema.management.azure.com/...",
                    "triggers": {"manual": {"type": "Request"}},
                    "actions": {
                        "step_2": {
                            "type": "Compose",
                            "inputs": "test",
                            "runAfter": {"step_1": ["Succeeded"]}
                        }
                    }
                }
            }
        }
        result = validate_flow_json(flow)
        assert result.has_warnings
        assert any(w.code == "FLOW-006" for w in result.warnings)

    def test_weird_schema_url(self):
        flow = {
            "properties": {
                "displayName": "Test",
                "definition": {
                    "$schema": "https://example.com/weird-schema",
                    "triggers": {"manual": {"type": "Request"}},
                    "actions": {"s1": {"type": "Compose", "inputs": "ok", "runAfter": {}}}
                }
            }
        }
        result = validate_flow_json(flow)
        assert result.has_warnings
        assert any(w.code == "FLOW-007" for w in result.warnings)
