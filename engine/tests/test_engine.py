"""
Tests for engine/__init__.py — Works With Agents Engine class.
"""
import pytest
from engine import WorksWithAgentsEngine
from engine.process_spec import ProcessSpec, ProcessStep, TriggerType, ActionType


class TestWorksWithAgentsEngine:
    def test_engine_initialization(self):
        engine = WorksWithAgentsEngine()
        assert engine is not None
        assert engine._mode == "auto"

    def test_available_templates(self):
        engine = WorksWithAgentsEngine()
        templates = engine.available_templates
        assert isinstance(templates, list)
        assert len(templates) > 0
        assert "foi-request-processing" in templates

    def test_parse_offline_returns_spec(self):
        engine = WorksWithAgentsEngine()
        spec = engine.parse(
            "Handle a freedom of information request",
            domain="government",
            use_llm=False,
        )
        assert isinstance(spec, ProcessSpec)
        assert len(spec.steps) > 0

    def test_parse_general_no_match_fallback(self):
        """Parse a description that doesn't match any template — should use fallback."""
        engine = WorksWithAgentsEngine()
        spec = engine.parse(
            "Schedule a weekly team standup meeting",
            domain="general",
            use_llm=False,
        )
        assert isinstance(spec, ProcessSpec)
        # Fallback should produce at least one step
        assert len(spec.steps) > 0

    def test_compile_returns_dict(self):
        engine = WorksWithAgentsEngine()
        spec = engine.parse("FOI request handling process", domain="government", use_llm=False)
        flow = engine.compile(spec, tenant="test.sharepoint.com", sharepoint_site="sites/test")
        assert isinstance(flow, dict)
        assert "properties" in flow

    def test_validate_returns_validation_result(self):
        engine = WorksWithAgentsEngine()
        spec = engine.parse("FOI request handling", domain="government", use_llm=False)
        result = engine.validate(spec)
        assert result.is_valid

    def test_to_json_returns_string(self):
        engine = WorksWithAgentsEngine()
        spec = engine.parse("FOI request handling", domain="government", use_llm=False)
        json_str = engine.to_json(spec)
        assert isinstance(json_str, str)
        assert "properties" in json_str

    def test_describe_returns_string(self):
        engine = WorksWithAgentsEngine()
        spec = engine.parse("FOI request handling", domain="government", use_llm=False)
        desc = engine.describe(spec)
        assert isinstance(desc, str)
        assert spec.name in desc

    def test_end_to_end_returns_dict_with_all_keys(self):
        engine = WorksWithAgentsEngine()
        result = engine.end_to_end(
            "Process a FOI request with compliance checks",
            domain="government",
            use_llm=False,
        )
        assert isinstance(result, dict)
        assert "spec" in result
        assert "flow_json" in result
        assert "validation" in result
        assert "summary" in result
        assert result["validation"].is_valid

    def test_end_to_end_without_validation(self):
        engine = WorksWithAgentsEngine()
        result = engine.end_to_end(
            "Simple notification flow",
            domain="general",
            use_llm=False,
            validate=False,
        )
        assert result["validation"] is None


class TestEngineModeBehavior:
    def test_offline_mode_uses_templates(self):
        engine = WorksWithAgentsEngine()
        spec = engine.parse(
            "Subject access request under GDPR article 15",
            domain="nhs",
            use_llm=False,
        )
        # Should match SAR template
        assert "Subject Access" in spec.name or "SAR" in spec.name.upper()
