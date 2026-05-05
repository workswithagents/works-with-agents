"""
Works With Agents — NL→Process Engine
=================================
Core engine for converting English business process descriptions into
deployable workflow configurations (e.g. Power Automate). Built for regulated industries.

Usage:
    from engine import WorksWithAgentsEngine

    engine = WorksWithAgentsEngine(gateway_url="http://localhost:8443", license_key="...")

    # Parse English → structured spec
    spec = engine.parse(
        "When a DPIA is submitted, route to DPO for approval within 14 days",
        domain="nhs"
    )

    # Compile to workflow deployment JSON
    flow_json = engine.compile(spec, tenant="contoso.sharepoint.com")

    # Validate
    result = engine.validate(spec)
    print(f"Valid: {result.is_valid}")

    # Deploy-ready JSON
    print(engine.to_json(spec))
"""

from .process_spec import ProcessSpec, ProcessStep, TriggerType, ActionType
from .process_parser import ProcessParser
from .flow_compiler import compile, compile_to_json, summary
from .template_library import TEMPLATES, match_template
from .validator import validate_spec, ValidationResult


class WorksWithAgentsEngine:
    """
    Main entry point for the Works With Agents NL→Process pipeline.

    Three modes:
    1. Gateway mode (requires running LLM Gateway) — best quality
    2. Template mode (offline, keyword matching) — fast, no LLM needed
    3. Fallback mode (minimal generic workflow) — always works
    """

    def __init__(self, gateway_url: str = "http://localhost:8443",
                 license_key: str = "", model: str = "agentic-qwen-8b"):
        self.parser = ProcessParser(gateway_url, license_key, model)
        self._mode = "auto"  # auto, gateway, template, fallback

    @property
    def available_templates(self) -> list[str]:
        """List available template names."""
        return sorted(TEMPLATES.keys())

    def parse(self, description: str, domain: str = "general",
              use_llm: bool = True) -> ProcessSpec:
        """
        Convert English description to ProcessSpec.

        Tries in order:
        1. LLM Gateway inference (if use_llm=True)
        2. Template matching (keyword-based)
        3. Fallback generic workflow

        Args:
            description: English description of the business process
            domain: 'nhs', 'finance', 'government', or 'general'
            use_llm: Whether to use the LLM Gateway (requires running gateway)

        Returns:
            ProcessSpec with structured steps
        """
        # If LLM is enabled, try it first
        if use_llm and self.parser.gateway_url:
            try:
                return self.parser.parse_sync(description, domain)
            except Exception as e:
                # Log and fall through to template matching
                print(f"⚠️  LLM Gateway unavailable: {e}")
                print(f"   Falling back to template matching...")

        # Try template matching
        spec = match_template(description, domain)
        if spec:
            return spec

        # Final fallback
        return self.parser.parse_local(description, domain)

    def compile(self, spec: ProcessSpec, tenant: str = "{tenant}",
                sharepoint_site: str = "{site}",
                connections: dict | None = None) -> dict:
        """
        Compile a ProcessSpec to deployable workflow definition.

        Args:
            spec: The process specification
            tenant: SharePoint tenant URL
            sharepoint_site: SharePoint site path
            connections: Custom connector references

        Returns:
            Power Automate flow definition dict
        """
        return compile(spec, tenant, sharepoint_site, connections)

    def validate(self, spec: ProcessSpec) -> ValidationResult:
        """Validate a ProcessSpec for completeness and correctness."""
        return validate_spec(spec)

    def to_json(self, spec: ProcessSpec, tenant: str = "{tenant}",
                site: str = "{site}", indent: int = 2) -> str:
        """Compile and return JSON string ready for deployment."""
        return compile_to_json(spec, tenant, site, indent)

    def describe(self, spec: ProcessSpec) -> str:
        """Human-readable summary of what the flow does."""
        return summary(spec)

    def end_to_end(self, description: str, domain: str = "nhs",
                   tenant: str = "{tenant}", site: str = "{site}",
                   use_llm: bool = True, validate: bool = True) -> dict:
        """
        Full pipeline: English → ProcessSpec → deployable workflow → validated.

        Returns dict with:
          - spec: ProcessSpec
          - flow_json: Power Automate flow dict
          - validation: ValidationResult
          - summary: Human-readable text
        """
        # Parse
        spec = self.parse(description, domain, use_llm)

        # Compile
        flow_json = self.compile(spec, tenant, site)

        # Validate
        validation_result = self.validate(spec) if validate else None

        return {
            "spec": spec,
            "flow_json": flow_json,
            "validation": validation_result,
            "summary": self.describe(spec),
        }
