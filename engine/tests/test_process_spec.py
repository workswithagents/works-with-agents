"""
Tests for process_spec.py — ProcessSpec and ProcessStep data models.
"""
import pytest
from engine.process_spec import (
    ProcessSpec, ProcessStep, TriggerType, ActionType
)


class TestProcessStep:
    def test_minimal_step(self):
        step = ProcessStep(id="step_1", action=ActionType.NOTIFICATION, label="Notify user")
        assert step.id == "step_1"
        assert step.action == ActionType.NOTIFICATION
        assert step.label == "Notify user"
        assert step.target is None
        assert step.deadline_hours is None
        assert step.condition is None
        assert step.on_approve is None
        assert step.on_reject is None

    def test_full_step(self):
        step = ProcessStep(
            id="approval_1",
            action=ActionType.APPROVAL,
            label="Manager sign-off",
            target="Line Manager",
            deadline_hours=72,
            on_approve="step_next",
            on_reject="step_reject",
            notification_template="Please review {item}",
        )
        assert step.target == "Line Manager"
        assert step.deadline_hours == 72
        assert step.on_approve == "step_next"
        assert step.on_reject == "step_reject"
        assert step.notification_template == "Please review {item}"

    def test_sp_fields(self):
        step = ProcessStep(
            id="update_1",
            action=ActionType.UPDATE_ITEM,
            label="Update status",
            sp_list="Requests",
            sp_fields={"Status": "Approved"},
        )
        assert step.sp_list == "Requests"
        assert step.sp_fields == {"Status": "Approved"}

    def test_metadata(self):
        step = ProcessStep(id="s1", action=ActionType.LOG, label="Audit", metadata={"source": "agent"})
        assert step.metadata == {"source": "agent"}


class TestProcessSpec:
    def test_minimal_spec(self):
        spec = ProcessSpec(
            name="Test Process",
            description="A test process for unit testing",
            domain="general",
        )
        assert spec.name == "Test Process"
        assert spec.domain == "general"
        assert spec.trigger == TriggerType.MANUAL
        assert spec.steps == []
        assert spec.compliance_checklist == []
        assert spec.tags == []
        assert spec.estimated_complexity == "medium"

    def test_spec_with_steps(self):
        steps = [
            ProcessStep(id="s1", action=ActionType.LOG, label="Log request"),
            ProcessStep(id="s2", action=ActionType.APPROVAL, label="Approve", target="Manager"),
        ]
        spec = ProcessSpec(
            name="Approval Flow",
            description="Simple approval process",
            domain="finance",
            regulation_ref="GDPR Art.35",
            trigger=TriggerType.ITEM_CREATED,
            trigger_list="Requests",
            steps=steps,
            compliance_checklist=["Check A", "Check B"],
            tags=["approval", "finance"],
            estimated_complexity="simple",
        )
        assert len(spec.steps) == 2
        assert spec.regulation_ref == "GDPR Art.35"
        assert spec.trigger == TriggerType.ITEM_CREATED
        assert spec.trigger_list == "Requests"
        assert len(spec.compliance_checklist) == 2
        assert "Check A" in spec.compliance_checklist
        assert spec.estimated_complexity == "simple"

    def test_generated_fields_default_none(self):
        spec = ProcessSpec(name="T", description="Test desc", domain="general")
        assert spec.raw_input is None
        assert spec.generated_at is None
        assert spec.model_used is None

    def test_domain_literal(self):
        spec = ProcessSpec(name="N", description="NHS process", domain="nhs")
        assert spec.domain == "nhs"

        spec = ProcessSpec(name="F", description="Finance process", domain="finance")
        assert spec.domain == "finance"

        spec = ProcessSpec(name="G", description="Gov process", domain="government")
        assert spec.domain == "government"


class TestActionType:
    def test_all_actions_have_string_values(self):
        for action in ActionType:
            assert isinstance(action.value, str)

    def test_approval_exists(self):
        assert ActionType.APPROVAL.value == "approval"

    def test_no_assignment_type(self):
        """Guard against reintroducing the phantom ASSIGNMENT type."""
        values = [a.value for a in ActionType]
        assert "assignment" not in values
        with pytest.raises(AttributeError):
            _ = ActionType.ASSIGNMENT


class TestTriggerType:
    def test_all_triggers_have_string_values(self):
        for trigger in TriggerType:
            assert isinstance(trigger.value, str)

    def test_scheduled_trigger(self):
        assert TriggerType.SCHEDULED.value == "scheduled"

    def test_webhook_trigger(self):
        assert TriggerType.WEBHOOK.value == "webhook"
