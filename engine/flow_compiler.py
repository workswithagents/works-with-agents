"""
Works With Agents — Flow Compiler
============================
Converts ProcessSpec objects into valid Power Automate flow JSON
ready for deployment via Microsoft Graph API.

Power Automate flow JSON structure:
{
  "properties": {
    "displayName": "...",
    "definition": {
      "$schema": "https://schema.management.azure.com/...",
      "contentVersion": "1.0.0.0",
      "parameters": {},
      "triggers": { ... },
      "actions": { ... },
      "outputs": {}
    },
    "state": "Started"
  }
}
"""

import json
import uuid
from .process_spec import ProcessSpec, ProcessStep, TriggerType, ActionType

# ── Power Automate API types ──────────────────────────────────────────

# Standard connectors used across regulated processes
STANDARD_CONNECTORS = {
    "sharepointonline": "/subscriptions/{subscription}/providers/Microsoft.Web/locations/{location}/managedApis/sharepointonline",
    "office365": "/subscriptions/{subscription}/providers/Microsoft.Web/locations/{location}/managedApis/office365",
    "teams": "/subscriptions/{subscription}/providers/Microsoft.Web/locations/{location}/managedApis/teams",
    "notifications": "/subscriptions/{subscription}/providers/Microsoft.Web/locations/{location}/managedApis/notifications",
}

TRIGGER_TEMPLATES = {
    TriggerType.ITEM_CREATED: {
        "type": "OpenApiConnection",
        "inputs": {
            "host": {
                "connectionName": "shared_sharepointonline",
                "operationId": "WhenAnItemIsCreated",
            },
            "parameters": {
                "dataset": "https://{tenant}.sharepoint.com/sites/{site}",
                "table": "{list_id}",  # GUID of SharePoint list
            },
        },
    },
    TriggerType.ITEM_MODIFIED: {
        "type": "OpenApiConnection",
        "inputs": {
            "host": {
                "connectionName": "shared_sharepointonline",
                "operationId": "WhenAnItemIsModified",
            },
            "parameters": {
                "dataset": "https://{tenant}.sharepoint.com/sites/{site}",
                "table": "{list_id}",
            },
        },
    },
    TriggerType.MANUAL: {
        "type": "Request",
        "kind": "Button",
        "inputs": {},
    },
    TriggerType.SCHEDULED: {
        "type": "Recurrence",
        "recurrence": {
            "frequency": "Day",
            "interval": 1,
        },
    },
    TriggerType.FORM_SUBMITTED: {
        "type": "OpenApiConnection",
        "inputs": {
            "host": {
                "connectionName": "shared_microsoftforms",
                "operationId": "WhenANewResponseIsSubmitted",
            },
            "parameters": {
                "formId": "{form_id}",
            },
        },
    },
}

ACTION_TEMPLATES = {
    ActionType.APPROVAL: {
        "type": "OpenApiConnection",
        "inputs": {
            "host": {
                "connectionName": "shared_approvals",
                "operationId": "CreateAnApproval",
            },
            "parameters": {
                "approvalType": "Custom",
                "title": "{label}",
                "assignedTo": "{target}",
                "details": "{notification_template}",
            },
        },
        "runAfter": {},
    },
    ActionType.NOTIFICATION: {
        "type": "OpenApiConnection",
        "inputs": {
            "host": {
                "connectionName": "shared_office365",
                "operationId": "SendEmailV2",
            },
            "parameters": {
                "To": "{target}",
                "Subject": "{label}",
                "Body": "{notification_template}",
                "Importance": "Normal",
            },
        },
        "runAfter": {},
    },
    ActionType.SEND_EMAIL: {
        "type": "OpenApiConnection",
        "inputs": {
            "host": {
                "connectionName": "shared_office365",
                "operationId": "SendEmailV2",
            },
            "parameters": {
                "To": "{target}",
                "Subject": "{label}",
                "Body": "{notification_template}",
                "Importance": "High",
            },
        },
        "runAfter": {},
    },
    ActionType.TEAMS_MESSAGE: {
        "type": "OpenApiConnection",
        "inputs": {
            "host": {
                "connectionName": "shared_teams",
                "operationId": "PostMessageInChatOrChannel",
            },
            "parameters": {
                "message": {
                    "body": {
                        "content": "{notification_template}",
                    }
                }
            },
        },
        "runAfter": {},
    },
    ActionType.UPDATE_ITEM: {
        "type": "OpenApiConnection",
        "inputs": {
            "host": {
                "connectionName": "shared_sharepointonline",
                "operationId": "UpdateItem",
            },
            "parameters": {
                "dataset": "https://{tenant}.sharepoint.com/sites/{site}",
                "table": "{trigger_list}",
                "id": "@triggerBody()?['ID']",
                "item/Status": "{label}",
            },
        },
        "runAfter": {},
    },
    ActionType.WAIT: {
        "type": "Wait",
        "inputs": {
            "unit": "Hour",
            "count": "{deadline_hours}",
        },
        "runAfter": {},
    },
    ActionType.ESCALATION: {
        "type": "OpenApiConnection",
        "inputs": {
            "host": {
                "connectionName": "shared_office365",
                "operationId": "SendEmailV2",
            },
            "parameters": {
                "To": "{target}",
                "Subject": "ESCALATION: {label}",
                "Body": "This item has been escalated: {notification_template}. Deadline: {deadline_hours}h.",
                "Importance": "High",
            },
        },
        "runAfter": {},
    },
    ActionType.LOG: {
        "type": "OpenApiConnection",
        "inputs": {
            "host": {
                "connectionName": "shared_sharepointonline",
                "operationId": "CreateItem",
            },
            "parameters": {
                "dataset": "https://{tenant}.sharepoint.com/sites/{site}",
                "table": "Audit Log",
                "item/Title": "{label}",
                "item/Description": "{notification_template}",
                "item/Timestamp": "@utcNow()",
            },
        },
        "runAfter": {},
    },
    ActionType.CONDITION: {
        "type": "If",
        "expression": {
            "and": [
                {
                    "equals": [
                        "@equals(1, 1)",
                        True
                    ]
                }
            ]
        },
        "actions": {},   # True branch
        "else": {
            "actions": {}  # False branch
        },
        "runAfter": {},
    },
}


def _format_string(template: str, step: ProcessStep, spec: ProcessSpec) -> str:
    """Replace placeholders in action templates with step/spec values."""
    replacements = {
        "{label}": step.label,
        "{target}": step.target or "Administrator",
        "{deadline_hours}": str(step.deadline_hours or 48),
        "{notification_template}": step.notification_template or step.label,
        "{trigger_list}": spec.trigger_list or "Shared Documents",
    }
    result = template
    for key, val in replacements.items():
        result = result.replace(key, val)
    return result


def compile(spec: ProcessSpec, tenant: str = "{tenant}",
            sharepoint_site: str = "{site}",
            connections: dict | None = None) -> dict:
    """
    Compile a ProcessSpec into a deployable Power Automate flow definition.

    Args:
        spec: The process specification
        tenant: SharePoint tenant (e.g., 'contoso.sharepoint.com')
        sharepoint_site: SharePoint site path (e.g., 'sites/Compliance')
        connections: Custom connector references (optional)

    Returns:
        Power Automate flow definition dict ready for Graph API
    """
    if connections is None:
        connections = STANDARD_CONNECTORS

    # ── Build triggers ────────────────────────────────────────────────
    trigger_template = TRIGGER_TEMPLATES.get(spec.trigger, TRIGGER_TEMPLATES[TriggerType.MANUAL])
    triggers = {
        spec.trigger.value: json.loads(
            json.dumps(trigger_template)
            .replace("{tenant}", tenant)
            .replace("{site}", sharepoint_site)
            .replace("{list_id}", spec.trigger_list or "00000000-0000-0000-0000-000000000000")
        )
    }

    # ── Build actions ─────────────────────────────────────────────────
    actions = {}

    for step in spec.steps:
        action_template = ACTION_TEMPLATES.get(step.action)
        if not action_template:
            # Unsupported action — skip with a placeholder
            actions[step.id] = {
                "type": "Compose",
                "inputs": f"[Unsupported: {step.action}] {step.label}",
                "runAfter": {},
            }
            continue

        # Deep copy to avoid mutating the template
        action = json.loads(json.dumps(action_template))

        # Format strings
        for key, val in action.get("inputs", {}).get("parameters", {}).items():
            if isinstance(val, str):
                action["inputs"]["parameters"][key] = _format_string(val, step, spec)
        if "Subject" in action.get("inputs", {}).get("parameters", {}):
            subject = action["inputs"]["parameters"].get("Subject", "")
            if isinstance(subject, str):
                action["inputs"]["parameters"]["Subject"] = _format_string(
                    f"[{spec.regulation_ref or spec.name}] {subject}", step, spec
                )

        # Handle conditions (If/else)
        if step.action == ActionType.CONDITION and step.condition:
            action["expression"] = {"equals": [step.condition, True]}
            # The condition branches will be populated by the caller
            # using _build_condition_tree

        # Handle approval routing
        if step.action == ActionType.APPROVAL:
            if step.notification_template:
                action["inputs"]["parameters"]["details"] = step.notification_template
            # Add approval outcomes as parallel branches
            action["inputs"]["parameters"]["enableAutoRejection"] = bool(
                step.deadline_hours and step.deadline_hours > 0
            )

        actions[step.id] = action

    # ── Wire up runAfter ──────────────────────────────────────────────
    prev_id = None
    for step in spec.steps:
        if step.id not in actions:
            continue

        if prev_id is None:
            # First action runs after trigger
            actions[step.id]["runAfter"] = {}
        elif step.action == ActionType.CONDITION:
            # Conditions are special — they're wired in _build_condition_tree
            pass
        else:
            actions[step.id]["runAfter"] = {prev_id: ["Succeeded"]}

        prev_id = step.id

    # ── Build final flow definition ───────────────────────────────────
    definition = {
        "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
        "contentVersion": "1.0.0.0",
        "parameters": {},
        "triggers": triggers,
        "actions": actions,
        "outputs": {},
    }

    flow = {
        "properties": {
            "displayName": f"[{spec.domain.upper()}] {spec.name}",
            "definition": definition,
            "state": "Started",
            "connectionReferences": {
                name: {
                    "connectionName": conn,
                    "id": conn,
                    "api": {"name": name},
                }
                for name, conn in connections.items()
            },
        },
    }

    # Add compliance metadata
    flow["properties"]["description"] = (
        f"{spec.description}\n\n"
        f"Regulation: {spec.regulation_ref or 'N/A'}\n"
        f"Generated by Works With Agents Engine\n"
        f"Domain: {spec.domain} | Complexity: {spec.estimated_complexity}"
    )

    if spec.compliance_checklist:
        flow["properties"]["tags"] = spec.tags
        flow["properties"]["compliance_checklist"] = spec.compliance_checklist

    return flow


def compile_to_json(spec: ProcessSpec, tenant: str = "{tenant}",
                    sharepoint_site: str = "{site}",
                    indent: int = 2) -> str:
    """Compile ProcessSpec to JSON string ready for deployment."""
    flow = compile(spec, tenant, sharepoint_site)
    return json.dumps(flow, indent=indent)


def summary(spec: ProcessSpec) -> str:
    """Human-readable summary of what the compiled flow does."""
    lines = [
        f"📋 {spec.name}",
        f"   Domain: {spec.domain} | Complexity: {spec.estimated_complexity}",
        f"   Regulation: {spec.regulation_ref or 'N/A'}",
        f"   Trigger: {spec.trigger.value}",
        f"   Steps: {len(spec.steps)}",
        "",
    ]

    for step in spec.steps:
        emoji = {
            ActionType.APPROVAL: "✅",
            ActionType.NOTIFICATION: "📧",
            ActionType.SEND_EMAIL: "📨",
            ActionType.WAIT: "⏰",
            ActionType.ESCALATION: "🚨",
            ActionType.CONDITION: "🔀",
            ActionType.LOG: "📝",
            ActionType.UPDATE_ITEM: "✏️",
            ActionType.CREATE_ITEM: "➕",
            ActionType.DELETE_ITEM: "🗑️",
            ActionType.TRANSFORM: "🔄",
            ActionType.CUSTOM_HTTP: "🌐",
            ActionType.TEAMS_MESSAGE: "💬",
        }.get(step.action, "▶️")

        target_str = f" → {step.target}" if step.target else ""
        deadline_str = f" [{step.deadline_hours}h]" if step.deadline_hours else ""
        lines.append(f"   {emoji} {step.label}{target_str}{deadline_str}")

    lines.append("")
    lines.append(f"   ✅ Compliance checks: {len(spec.compliance_checklist)}")

    return "\n".join(lines)
