#!/usr/bin/env python3
"""
Works With Agents — CLI
==================
Command-line interface for the NL→Process Engine.

Usage:
    python -m main parse "When a FOI request arrives, assign within 24h..."
    python -m main templates
    python -m main validate --spec spec.json
    python -m main end-to-end "DPIA approval process..." --domain nhs --output flow.json
"""

import argparse
import json
import sys
import os

# Add parent to path so we can run as `python main.py`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import WorksWithAgentsEngine


def cmd_templates(args):
    """List available templates."""
    engine = WorksWithAgentsEngine()
    print("📋 Available Process Templates:\n")
    for name in engine.available_templates:
        from engine.template_library import TEMPLATES
        spec = TEMPLATES[name]
        print(f"  {name}")
        print(f"    {spec.description[:100]}...")
        print(f"    Domain: {spec.domain} | Steps: {len(spec.steps)} | Regulation: {spec.regulation_ref or 'N/A'}")
        print()


def cmd_parse(args):
    """Parse English description to ProcessSpec."""
    engine = WorksWithAgentsEngine(
        gateway_url=args.gateway or "http://localhost:8443",
        license_key=args.license_key or "",
        model=args.model or "agentic-qwen-8b",
    )

    print(f"🔍 Parsing: {args.description[:100]}...")
    print(f"   Domain: {args.domain} | LLM: {not args.offline}\n")

    spec = engine.parse(args.description, args.domain, use_llm=not args.offline)

    print(engine.describe(spec))
    print(f"\n   Model: {spec.model_used}")

    # Validate
    if not args.skip_validation:
        result = engine.validate(spec)
        print(f"\n{result}")

    # Save if requested
    if args.output:
        with open(args.output, "w") as f:
            json.dump({
                "name": spec.name,
                "description": spec.description,
                "domain": spec.domain,
                "regulation_ref": spec.regulation_ref,
                "trigger": spec.trigger.value,
                "steps": [
                    {
                        "id": s.id,
                        "action": s.action.value,
                        "label": s.label,
                        "target": s.target,
                        "deadline_hours": s.deadline_hours,
                    }
                    for s in spec.steps
                ],
                "compliance_checklist": spec.compliance_checklist,
                "tags": spec.tags,
            }, f, indent=2)
        print(f"\n💾 Spec saved to: {args.output}")


def cmd_compile(args):
    """Compile a ProcessSpec JSON to Power Automate flow."""
    with open(args.spec) as f:
        spec_data = json.load(f)

    # Reconstruct ProcessSpec from JSON
    from engine.process_spec import ProcessSpec, ProcessStep, TriggerType, ActionType

    steps = []
    for s in spec_data.get("steps", []):
        steps.append(ProcessStep(
            id=s["id"],
            action=ActionType(s["action"]),
            label=s["label"],
            target=s.get("target"),
            deadline_hours=s.get("deadline_hours"),
        ))

    spec = ProcessSpec(
        name=spec_data["name"],
        description=spec_data["description"],
        domain=spec_data.get("domain", "general"),
        regulation_ref=spec_data.get("regulation_ref"),
        trigger=TriggerType(spec_data.get("trigger", "manual")),
        steps=steps,
        compliance_checklist=spec_data.get("compliance_checklist", []),
        tags=spec_data.get("tags", []),
    )

    engine = WorksWithAgentsEngine()
    flow_json = engine.to_json(
        spec,
        tenant=args.tenant or "{tenant}",
        site=args.site or "{site}",
    )

    if args.output:
        with open(args.output, "w") as f:
            f.write(flow_json)
        print(f"💾 Flow saved to: {args.output}")
    else:
        print(flow_json)


def cmd_end_to_end(args):
    """Full pipeline: English → ProcessSpec → Power Automate JSON."""
    engine = WorksWithAgentsEngine(
        gateway_url=args.gateway or "http://localhost:8443",
        license_key=args.license_key or "",
        model=args.model or "agentic-qwen-8b",
    )

    print(f"🚀 Works With Agents — Full Pipeline")
    print(f"   Input: {args.description[:100]}...")
    print(f"   Domain: {args.domain} | LLM: {not args.offline}\n")

    result = engine.end_to_end(
        args.description,
        domain=args.domain,
        tenant=args.tenant or "{tenant}",
        site=args.site or "{site}",
        use_llm=not args.offline,
        validate=True,
    )

    # Summary
    print("=" * 50)
    print("STEP 1: Process Spec (English → Structured)")
    print("=" * 50)
    print(result["summary"])

    # Validation
    if result["validation"]:
        print(f"\n{'=' * 50}")
        print("STEP 2: Validation")
        print("=" * 50)
        print(result["validation"])

    # Flow JSON (truncated)
    print(f"\n{'=' * 50}")
    print("STEP 3: Power Automate Flow JSON")
    print("=" * 50)
    flow_str = json.dumps(result["flow_json"], indent=2)
    if len(flow_str) > 2000:
        print(flow_str[:2000])
        print(f"\n... ({len(flow_str)} bytes total, truncated)")
    else:
        print(flow_str)

    # Save
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result["flow_json"], f, indent=2)
        print(f"\n💾 Full flow saved to: {args.output}")


def cmd_validate(args):
    """Validate a ProcessSpec JSON file."""
    with open(args.spec) as f:
        spec_data = json.load(f)

    from engine.process_spec import ProcessSpec, ProcessStep, TriggerType, ActionType

    steps = []
    for s in spec_data.get("steps", []):
        steps.append(ProcessStep(
            id=s["id"],
            action=ActionType(s["action"]),
            label=s["label"],
            target=s.get("target"),
            deadline_hours=s.get("deadline_hours"),
            condition=s.get("condition"),
            on_approve=s.get("on_approve"),
            on_reject=s.get("on_reject"),
        ))

    spec = ProcessSpec(
        name=spec_data["name"],
        description=spec_data["description"],
        domain=spec_data.get("domain", "general"),
        regulation_ref=spec_data.get("regulation_ref"),
        trigger=TriggerType(spec_data.get("trigger", "manual")),
        steps=steps,
        compliance_checklist=spec_data.get("compliance_checklist", []),
        tags=spec_data.get("tags", []),
    )

    engine = WorksWithAgentsEngine()
    result = engine.validate(spec)
    print(f"🔍 Validating: {spec.name}")
    print(f"   Steps: {len(spec.steps)} | Domain: {spec.domain}")
    print(f"\n{result}")

    if result.is_valid:
        sys.exit(0)
    else:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Works With Agents — English → process workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py templates
  python main.py parse "When a FOI request arrives, assign to coordinator"
  python main.py parse --offline "Approval process for expense claims" --domain finance
  python main.py end-to-end "DPIA with DPO approval and SIRO sign-off" --domain nhs --output dpia-flow.json
  python main.py compile --spec my-spec.json --output flow.json
  python main.py validate --spec my-spec.json
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # templates
    subparsers.add_parser("templates", help="List available process templates")

    # parse
    parse_parser = subparsers.add_parser("parse", help="Parse English description to ProcessSpec")
    parse_parser.add_argument("description", help="English description of the process")
    parse_parser.add_argument("--domain", default="general",
                             choices=["nhs", "finance", "government", "general"])
    parse_parser.add_argument("--gateway", help="LLM Gateway URL")
    parse_parser.add_argument("--license-key", help="Bastion license key")
    parse_parser.add_argument("--model", default="agentic-qwen-8b")
    parse_parser.add_argument("--offline", action="store_true",
                             help="Skip LLM, use template matching")
    parse_parser.add_argument("--skip-validation", action="store_true")
    parse_parser.add_argument("--output", "-o", help="Save spec as JSON")

    # compile
    compile_parser = subparsers.add_parser("compile", help="Compile ProcessSpec JSON to PA flow")
    compile_parser.add_argument("--spec", required=True, help="ProcessSpec JSON file")
    compile_parser.add_argument("--tenant", help="SharePoint tenant")
    compile_parser.add_argument("--site", help="SharePoint site")
    compile_parser.add_argument("--output", "-o", help="Save flow JSON")

    # end-to-end
    e2e_parser = subparsers.add_parser("end-to-end", help="Full pipeline: English → PA flow")
    e2e_parser.add_argument("description", help="English process description")
    e2e_parser.add_argument("--domain", default="nhs",
                           choices=["nhs", "finance", "government", "general"])
    e2e_parser.add_argument("--gateway", help="LLM Gateway URL")
    e2e_parser.add_argument("--license-key", help="Bastion license key")
    e2e_parser.add_argument("--model", default="agentic-qwen-8b")
    e2e_parser.add_argument("--offline", action="store_true")
    e2e_parser.add_argument("--tenant", help="SharePoint tenant")
    e2e_parser.add_argument("--site", help="SharePoint site")
    e2e_parser.add_argument("--output", "-o", help="Save flow JSON")

    # validate
    validate_parser = subparsers.add_parser("validate", help="Validate ProcessSpec JSON")
    validate_parser.add_argument("--spec", required=True, help="ProcessSpec JSON file")

    args = parser.parse_args()

    if args.command == "templates":
        cmd_templates(args)
    elif args.command == "parse":
        cmd_parse(args)
    elif args.command == "compile":
        cmd_compile(args)
    elif args.command == "end-to-end":
        cmd_end_to_end(args)
    elif args.command == "validate":
        cmd_validate(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
