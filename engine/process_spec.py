"""
Works With Agents — Process Spec Model
==================================
The intermediate representation between English descriptions and
Power Automate flow JSON. All components operate on this schema.
"""

from dataclasses import dataclass, field
from typing import Optional, Literal
from enum import Enum


class TriggerType(str, Enum):
    """How the process starts"""
    ITEM_CREATED = "item_created"        # New SP list item
    ITEM_MODIFIED = "item_modified"      # SP list item changed
    MANUAL = "manual"                     # Button press
    SCHEDULED = "scheduled"              # Time-based (cron)
    FORM_SUBMITTED = "form_submitted"    # MS Forms / custom form
    EMAIL_RECEIVED = "email_received"    # Incoming email
    WEBHOOK = "webhook"                   # HTTP endpoint


class ActionType(str, Enum):
    """What the step does"""
    APPROVAL = "approval"       # Human approves/rejects
    NOTIFICATION = "notification"  # Email, Teams, etc.
    CREATE_ITEM = "create_item"    # New SP list item
    UPDATE_ITEM = "update_item"    # Modify existing item
    DELETE_ITEM = "delete_item"    # Remove item
    CONDITION = "condition"        # If/else branch
    WAIT = "wait"                  # Delay / deadline
    ESCALATION = "escalation"      # Forward to higher authority
    LOG = "log"                    # Audit trail entry
    TRANSFORM = "transform"        # Data mapping / field changes
    CUSTOM_HTTP = "custom_http"    # External API call
    SEND_EMAIL = "send_email"      # Email with template
    TEAMS_MESSAGE = "teams_message"  # Teams notification


@dataclass
class ProcessStep:
    """One step in a business process"""
    id: str
    action: ActionType
    label: str  # Human description of this step
    target: Optional[str] = None  # Who does it (role, person, group)
    deadline_hours: Optional[int] = None  # SLA in hours
    condition: Optional[str] = None  # Power Automate expression
    on_approve: Optional[str] = None  # Step ID to go to on approve
    on_reject: Optional[str] = None   # Step ID to go to on reject
    notification_template: Optional[str] = None  # Email/Teams template
    sp_list: Optional[str] = None     # Target SharePoint list
    sp_fields: Optional[dict] = None  # Fields to set/update
    metadata: dict = field(default_factory=dict)


@dataclass
class ProcessSpec:
    """Complete specification for a business process"""
    # Identity
    name: str
    description: str
    domain: Literal["nhs", "finance", "government", "general"]
    regulation_ref: Optional[str] = None  # e.g., "GDPR Art.15", "FOIA 2000"

    # Trigger
    trigger: TriggerType = TriggerType.MANUAL
    trigger_list: Optional[str] = None    # SP list name for item triggers
    trigger_conditions: Optional[str] = None  # Optional filter

    # Steps
    steps: list[ProcessStep] = field(default_factory=list)

    # Meta
    compliance_checklist: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    estimated_complexity: Literal["simple", "medium", "complex"] = "medium"

    # Generated
    raw_input: Optional[str] = None  # The original English description
    generated_at: Optional[str] = None  # ISO timestamp
    model_used: Optional[str] = None    # Which LLM generated this
