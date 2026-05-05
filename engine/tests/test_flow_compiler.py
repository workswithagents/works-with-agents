"""
Tests for flow_compiler.py — ProcessSpec → Power Automate flow JSON compilation.
"""
import pytest
import json
from engine.process_spec import (
    ProcessSpec, ProcessStep, TriggerType, ActionType
)
from engine.flow_compiler import compile, compile_to_json, summary


def _make_simple_spec(**kwargs):
    steps = kwargs.pop("steps", [
        ProcessStep(id="s1", action=ActionType.LOG, label="Log start"),
        ProcessStep(id="s2", action=ActionType.NOTIFICATION, label="Notify user", target="user@org.com"),
    ])
    return ProcessSpec(
        name="Simple Flow",
        description="A simple test flow",
        domain="general",
        steps=steps,
        **kwargs
    )


class TestCompile:
    def test_basic_structure(self):
        spec = _make_simple_spec()
        flow = compile(spec)

        assert "properties" in flow
        props = flow["properties"]
        assert "displayName" in props
        assert "[GENERAL] Simple Flow" in props["displayName"]

    def test_definition_structure(self):
        spec = _make_simple_spec()
        flow = compile(spec)

        definition = flow["properties"]["definition"]
        assert "$schema" in definition
        assert definition["contentVersion"] == "1.0.0.0"
        assert "triggers" in definition
        assert "actions" in definition

    def test_manual_trigger(self):
        spec = _make_simple_spec(trigger=TriggerType.MANUAL)
        flow = compile(spec)
        triggers = flow["properties"]["definition"]["triggers"]
        assert "manual" in triggers
        assert triggers["manual"]["type"] == "Request"
        assert triggers["manual"]["kind"] == "Button"

    def test_item_created_trigger(self):
        spec = _make_simple_spec(
            trigger=TriggerType.ITEM_CREATED,
            trigger_list="00000000-0000-0000-0000-000000000001",
        )
        flow = compile(spec, tenant="contoso.sharepoint.com", sharepoint_site="sites/test")
        triggers = flow["properties"]["definition"]["triggers"]
        assert "item_created" in triggers
        t = triggers["item_created"]
        assert "contoso" in str(t)
        assert "sites/test" in str(t)

    def test_scheduled_trigger(self):
        spec = _make_simple_spec(trigger=TriggerType.SCHEDULED)
        flow = compile(spec)
        triggers = flow["properties"]["definition"]["triggers"]
        assert "scheduled" in triggers
        assert triggers["scheduled"]["type"] == "Recurrence"

    def test_actions_exist(self):
        spec = _make_simple_spec()
        flow = compile(spec)
        actions = flow["properties"]["definition"]["actions"]
        assert "s1" in actions
        assert "s2" in actions

    def test_action_run_after_wiring(self):
        steps = [
            ProcessStep(id="step_a", action=ActionType.LOG, label="First"),
            ProcessStep(id="step_b", action=ActionType.NOTIFICATION, label="Second", target="user"),
        ]
        spec = _make_simple_spec(steps=steps)
        flow = compile(spec)
        actions = flow["properties"]["definition"]["actions"]
        # Second action should run after first
        assert "step_a" in actions["step_b"]["runAfter"]

    def test_compliance_metadata(self):
        spec = ProcessSpec(
            name="Compliant Flow",
            description="A flow with compliance requirements",
            domain="nhs",
            regulation_ref="GDPR Art.35",
            steps=[
                ProcessStep(id="s1", action=ActionType.LOG, label="Log"),
            ],
            compliance_checklist=["Check A", "Check B"],
            tags=["gdpr", "healthcare"],
        )
        flow = compile(spec)
        props = flow["properties"]
        assert "GDPR Art.35" in props["description"]
        assert "compliance_checklist" in props
        assert len(props["compliance_checklist"]) == 2

    def test_connection_references(self):
        spec = _make_simple_spec()
        flow = compile(spec)
        refs = flow["properties"]["connectionReferences"]
        assert "sharepointonline" in refs
        assert "office365" in refs


class TestCompileToJson:
    def test_returns_valid_json_string(self):
        spec = _make_simple_spec()
        json_str = compile_to_json(spec)
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert "properties" in parsed

    def test_custom_indent(self):
        spec = _make_simple_spec()
        json_str = compile_to_json(spec, indent=4)
        # Should have 4-space indentation
        lines = json_str.split("\n")
        assert any(line.startswith("    ") for line in lines if line.strip())


class TestSummary:
    def test_returns_multiline_string(self):
        spec = _make_simple_spec()
        result = summary(spec)
        assert spec.name in result
        assert spec.domain in result

    def test_includes_steps(self):
        steps = [
            ProcessStep(id="s1", action=ActionType.APPROVAL, label="Manager approves", target="Manager"),
            ProcessStep(id="s2", action=ActionType.SEND_EMAIL, label="Notify applicant", target="applicant"),
        ]
        spec = _make_simple_spec(steps=steps)
        result = summary(spec)
        assert "Manager approves" in result
        assert "Notify applicant" in result
        assert "✅" in result  # approval emoji
        assert "📨" in result  # send_email emoji

    def test_includes_regulation(self):
        spec = _make_simple_spec(regulation_ref="GDPR Art.15")
        result = summary(spec)
        assert "GDPR Art.15" in result

    def test_includes_compliance_count(self):
        spec = _make_simple_spec(
            compliance_checklist=["Item 1", "Item 2", "Item 3"]
        )
        result = summary(spec)
        assert "3" in result  # compliance check count
