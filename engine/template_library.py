"""
Works With Agents — Template Library
===============================
Pre-built ProcessSpec templates for common regulated-industry workflows.
These serve as both training examples for the LLM parser and fallback
templates when the LLM Gateway is unavailable.
"""

from .process_spec import (
    ProcessSpec, ProcessStep, TriggerType, ActionType
)

# ── Template Registry ─────────────────────────────────────────────────

TEMPLATES: dict[str, ProcessSpec] = {}


def register(fn):
    """Decorator: call the function and register the resulting ProcessSpec."""
    spec = fn()
    TEMPLATES[spec.name.lower().replace(" ", "-")] = spec
    return spec  # Return the spec for direct access


# ── NHS / Healthcare ──────────────────────────────────────────────────

@register
def _foi_request():
    """Freedom of Information request handling — FOIA 2000 compliant"""
    return ProcessSpec(
        name="FOI Request Processing",
        description="Receive, log, assign, and respond to FOI requests within the statutory 20-working-day deadline. Includes escalation, redaction, and public interest test where applicable.",
        domain="government",
        regulation_ref="Freedom of Information Act 2000, s.10 (time for compliance), s.17 (refusal notice)",
        trigger=TriggerType.ITEM_CREATED,
        trigger_list="FOI Requests",
        steps=[
            ProcessStep(id="step_1", action=ActionType.LOG,
                       label="Log FOI request with date/time stamp and unique reference",
                       target="FOI Coordinator"),
            ProcessStep(id="step_2", action=ActionType.CONDITION,
                       label="Is the request valid? (name + address + clear description)",
                       condition="@equals(triggerOutputs()?['body/IsValid'], true)",
                       on_approve="step_4", on_reject="step_3"),
            ProcessStep(id="step_3", action=ActionType.NOTIFICATION,
                       label="Request clarification from applicant (pauses 20-day clock)",
                       target="Requestor",
                       notification_template="Dear {applicant}, we need clarification on your FOI request {ref}. Please specify: {missing_info}"),
            ProcessStep(id="step_4", action=ActionType.NOTIFICATION,
                       label="Assign to relevant department Information Asset Owner",
                       target="Department IAO",
                       deadline_hours=24),
            ProcessStep(id="step_5", action=ActionType.CONDITION,
                       label="Does the request exceed cost limit? (§12 — £450/£600)",
                       condition="@greater(length(variables('EstimatedHours')), 18)",
                       on_approve="step_6", on_reject="step_7"),
            ProcessStep(id="step_6", action=ActionType.NOTIFICATION,
                       label="Issue Section 12 refusal notice — cost exceeds appropriate limit",
                       target="Requestor",
                       notification_template="FOI Ref {ref}: Your request exceeds the appropriate limit under s.12 FOIA 2000. We estimate {hours} hours at £25/hr. Please narrow your request."),
            ProcessStep(id="step_7", action=ActionType.CONDITION,
                       label="Is any information exempt? (§21-44 exemptions)",
                       condition="@equals(variables('HasExemptions'), true)",
                       on_approve="step_8", on_reject="step_10"),
            ProcessStep(id="step_8", action=ActionType.APPROVAL,
                       label="Redaction review — mark exempt material, prepare refusal notice",
                       target="Information Governance Manager",
                       deadline_hours=72,
                       on_approve="step_9", on_reject="step_10"),
            ProcessStep(id="step_9", action=ActionType.CONDITION,
                       label="Does public interest override the exemption?",
                       condition="@equals(variables('PITOverride'), true)",
                       on_approve="step_10", on_reject="step_11"),
            ProcessStep(id="step_10", action=ActionType.UPDATE_ITEM,
                       label="Prepare response package — apply redactions",
                       target="FOI Coordinator"),
            ProcessStep(id="step_11", action=ActionType.SEND_EMAIL,
                       label="Issue Section 17 refusal with exemption justification",
                       target="Requestor",
                       notification_template="FOI Ref {ref}: Information withheld under s.{section} FOIA 2000. Reason: {justification}. Right to appeal to ICO within 6 months."),
            ProcessStep(id="step_12", action=ActionType.UPDATE_ITEM,
                       label="Send full or partial response to applicant",
                       target="Requestor",
                       notification_template="FOI Ref {ref}: Please find attached the information you requested. If you are dissatisfied, you may request an internal review within 40 working days."),
            ProcessStep(id="step_13", action=ActionType.LOG,
                       label="Record outcome, response date, exemptions used, and time taken",
                       target="FOI Coordinator"),
        ],
        compliance_checklist=[
            "20-working-day deadline tracked",
            "Section 12 cost limit check",
            "Exemption justification documented",
            "Public Interest Test recorded if applicable",
            "ICO appeal rights stated in response",
            "Publication scheme updated (if disclosing new information)",
        ],
        tags=["foi", "information-rights", "compliance", "public-sector"],
        estimated_complexity="complex",
    )


@register
def sar_request() -> ProcessSpec:
    """Subject Access Request — GDPR Art.15, UK DPA 2018"""
    return ProcessSpec(
        name="Subject Access Request Processing",
        description="Handle SARs within the statutory 1-month deadline. Verify identity, locate personal data, redact third-party data, and produce a complete response package.",
        domain="nhs",
        regulation_ref="UK GDPR Art.15 (Right of Access), DPA 2018 s.45",
        trigger=TriggerType.ITEM_CREATED,
        trigger_list="SAR Requests",
        steps=[
            ProcessStep(id="step_1", action=ActionType.LOG,
                       label="Log SAR with date/time — 1 calendar month clock starts",
                       target="Data Protection Officer"),
            ProcessStep(id="step_2", action=ActionType.CONDITION,
                       label="Is the requester's identity verified?",
                       condition="@equals(variables('IdentityVerified'), true)",
                       on_approve="step_4", on_reject="step_3"),
            ProcessStep(id="step_3", action=ActionType.NOTIFICATION,
                       label="Request ID verification — clock paused until received",
                       target="Requestor",
                       notification_template="To process your Subject Access Request (Ref: {ref}), we require proof of identity. Please provide: passport, driving license, or utility bill + photo ID. The 1-month clock is paused until we receive this.",
                       deadline_hours=0),
            ProcessStep(id="step_4", action=ActionType.CONDITION,
                       label="Is the request manifestly unfounded or excessive?",
                       condition="@equals(variables('IsExcessive'), true)",
                       on_approve="step_5", on_reject="step_6"),
            ProcessStep(id="step_5", action=ActionType.NOTIFICATION,
                       label="Notify requester — request deemed excessive, may charge fee or refuse",
                       target="Requestor"),
            ProcessStep(id="step_6", action=ActionType.WAIT,
                       label="Data search in progress — allow 14 days for departments to respond",
                       deadline_hours=336),
            ProcessStep(id="step_7", action=ActionType.APPROVAL,
                       label="Review collected data — redact third-party personal data",
                       target="Data Protection Officer",
                       deadline_hours=72,
                       on_approve="step_8", on_reject="step_11"),
            ProcessStep(id="step_8", action=ActionType.CONDITION,
                       label="Any third-party data that can't be redacted?",
                       condition="@equals(variables('HasThirdPartyData'), true)",
                       on_approve="step_9", on_reject="step_10"),
            ProcessStep(id="step_9", action=ActionType.APPROVAL,
                       label="Seek third-party consent or apply exemption (Schedule 2, Part 3 DPA 2018)",
                       target="Caldicott Guardian (if health data)",
                       deadline_hours=72,
                       on_approve="step_10", on_reject="step_10"),
            ProcessStep(id="step_10", action=ActionType.SEND_EMAIL,
                       label="Issue final response — data package + processing explanation + rights notice",
                       target="Requestor",
                       notification_template="SAR Ref {ref}: Please find your personal data attached. This includes: {data_categories}. Your data was processed for: {purposes}. You have the right to: rectification, erasure, restriction, objection, and to complain to the ICO."),
            ProcessStep(id="step_11", action=ActionType.LOG,
                       label="Close SAR — record: date completed, categories of data provided, exemptions used, any extensions",
                       target="Data Protection Officer"),
        ],
        compliance_checklist=[
            "Identity verified before processing",
            "1-month deadline tracked (extension possible for complex requests)",
            "Third-party data redacted or consent obtained",
            "Caldicott Guardian consulted for health data",
            "ICO complaint rights stated",
            "Record of processing documented",
        ],
        tags=["sar", "gdpr", "data-protection", "patient-data"],
        estimated_complexity="complex",
    )


@register
def dpia_process() -> ProcessSpec:
    """Data Protection Impact Assessment — GDPR Art.35"""
    return ProcessSpec(
        name="Data Protection Impact Assessment (DPIA)",
        description="Complete and approve DPIAs for high-risk processing activities. Includes screening, assessment, consultation, and sign-off stages.",
        domain="nhs",
        regulation_ref="UK GDPR Art.35, NHS DSP Toolkit §4.1",
        trigger=TriggerType.ITEM_CREATED,
        trigger_list="DPIAs",
        steps=[
            ProcessStep(id="step_1", action=ActionType.CONDITION,
                       label="Screening: Is a DPIA legally required? (new tech, large-scale, special categories, systematic monitoring)",
                       condition="@or(equals(variables('NewTech'), true), greater(variables('DataSubjects'), 5000))",
                       on_approve="step_3", on_reject="step_2"),
            ProcessStep(id="step_2", action=ActionType.LOG,
                       label="Record screening decision — DPIA not required, rationale documented",
                       target="DPO"),
            ProcessStep(id="step_3", action=ActionType.NOTIFICATION,
                       label="Assign DPIA owner (Project Lead + DPO consultation required)",
                       target="Project Lead",
                       deadline_hours=24),
            ProcessStep(id="step_4", action=ActionType.UPDATE_ITEM,
                       label="Describe the processing: nature, scope, context, purposes",
                       target="Project Lead"),
            ProcessStep(id="step_5", action=ActionType.UPDATE_ITEM,
                       label="Assess necessity and proportionality — why is this processing needed?",
                       target="Project Lead"),
            ProcessStep(id="step_6", action=ActionType.UPDATE_ITEM,
                       label="Identify and assess risks to individuals — likelihood × severity matrix",
                       target="Data Protection Officer"),
            ProcessStep(id="step_7", action=ActionType.UPDATE_ITEM,
                       label="Identify mitigating measures — pseudonymisation, encryption, access controls, retention limits",
                       target="Project Lead"),
            ProcessStep(id="step_8", action=ActionType.APPROVAL,
                       label="DPO review — is residual risk acceptable?",
                       target="Data Protection Officer",
                       deadline_hours=120,
                       on_approve="step_10", on_reject="step_9"),
            ProcessStep(id="step_9", action=ActionType.ESCALATION,
                       label="High residual risk — must consult ICO before proceeding (Art.36)",
                       target="Information Commissioner's Office",
                       deadline_hours=168),
            ProcessStep(id="step_10", action=ActionType.APPROVAL,
                       label="SIRO / Senior Management sign-off",
                       target="Senior Information Risk Owner",
                       deadline_hours=72,
                       on_approve="step_11", on_reject="step_9"),
            ProcessStep(id="step_11", action=ActionType.LOG,
                       label="DPIA approved — record in DPIA register, set review date (annual or on change)",
                       target="Data Protection Officer"),
        ],
        compliance_checklist=[
            "Screening decision documented even if DPIA not required",
            "DPO consulted throughout",
            "Risk assessment includes likelihood × severity",
            "Mitigating measures documented",
            "ICO consultation triggered for high residual risk",
            "SIRO approval obtained",
            "Review date set (max 12 months)",
        ],
        tags=["dpia", "gdpr", "risk-assessment", "data-protection", "dsp"],
        estimated_complexity="complex",
    )


@register
def whistleblowing() -> ProcessSpec:
    """Whistleblowing / Freedom to Speak Up — NHS"""
    return ProcessSpec(
        name="Whistleblowing / Freedom to Speak Up",
        description="Confidential reporting of concerns about risk, malpractice, or wrongdoing. NHS FTSU Guardian review with protected disclosure protection under PIDA 1998.",
        domain="nhs",
        regulation_ref="Public Interest Disclosure Act 1998, NHS FTSU Policy",
        trigger=TriggerType.FORM_SUBMITTED,
        trigger_list="Whistleblowing Reports",
        steps=[
            ProcessStep(id="step_1", action=ActionType.LOG,
                       label="Confidential log — case number assigned, timestamp, anonymised if requested",
                       target="Freedom to Speak Up Guardian"),
            ProcessStep(id="step_2", action=ActionType.CONDITION,
                       label="Is the concern patient-safety related?",
                       condition="@equals(variables('Category'), 'Patient Safety')",
                       on_approve="step_3", on_reject="step_4"),
            ProcessStep(id="step_3", action=ActionType.NOTIFICATION,
                       label="Escalate to Patient Safety Team + notify staff member of protection under PIDA",
                       target="Patient Safety Lead",
                       deadline_hours=4),
            ProcessStep(id="step_4", action=ActionType.NOTIFICATION,
                       label="Assign to appropriate investigating officer (HR, Clinical, or Management)",
                       target="Investigating Officer",
                       deadline_hours=24),
            ProcessStep(id="step_5", action=ActionType.UPDATE_ITEM,
                       label="Investigation commenced — gather evidence, interview witnesses",
                       target="Investigating Officer",
                       deadline_hours=336),  # 14 days
            ProcessStep(id="step_6", action=ActionType.APPROVAL,
                       label="Findings review — was there wrongdoing or risk?",
                       target="FTSU Guardian + Senior Manager",
                       deadline_hours=72,
                       on_approve="step_7", on_reject="step_8"),
            ProcessStep(id="step_7", action=ActionType.NOTIFICATION,
                       label="Recommendations issued — corrective actions, policy changes, disciplinary if needed",
                       target="Board / Executive Team",
                       notification_template="FTSU Case {ref}: Investigation complete. Finding: {finding}. Recommendations: {recommendations}. Staff member protected under PIDA 1998.",
                       deadline_hours=48),
            ProcessStep(id="step_8", action=ActionType.NOTIFICATION,
                       label="No wrongdoing found — inform reporter with explanation and support",
                       target="Reporter",
                       notification_template="FTSU Case {ref}: Investigation concluded. No evidence of wrongdoing found. If you have further concerns, please contact the FTSU Guardian. Your disclosure is protected under PIDA 1998."),
            ProcessStep(id="step_9", action=ActionType.LOG,
                       label="Close case — record: outcome, recommendations, reporter satisfaction, lessons learned",
                       target="FTSU Guardian"),
        ],
        compliance_checklist=[
            "Confidentiality maintained throughout",
            "PIDA protection confirmed to reporter",
            "Investigation completed within reasonable timeframe",
            "Patient safety escalation (if applicable)",
            "Board-level awareness of findings",
            "No retaliation against reporter — monitored",
        ],
        tags=["whistleblowing", "ftsu", "patient-safety", "pida", "confidential"],
        estimated_complexity="medium",
    )


@register
def incident_reporting() -> ProcessSpec:
    """Incident / Near-Miss Reporting — NHS patient safety"""
    return ProcessSpec(
        name="Incident & Near-Miss Reporting",
        description="Report, investigate, and learn from patient safety incidents and near-misses. Includes harm grading, investigation, and improvement actions per NHS Patient Safety Strategy.",
        domain="nhs",
        regulation_ref="NHS Patient Safety Strategy, LFPSE (Learn from Patient Safety Events)",
        trigger=TriggerType.ITEM_CREATED,
        trigger_list="Incidents",
        steps=[
            ProcessStep(id="step_1", action=ActionType.CONDITION,
                       label="Triage: What is the harm level?",
                       condition="@equals(variables('HarmLevel'), 'Severe')",
                       on_approve="step_2", on_reject="step_4"),
            ProcessStep(id="step_2", action=ActionType.ESCALATION,
                       label="Severe harm / death — immediate escalation to Medical Director + notify CQC within 24h",
                       target="Medical Director",
                       deadline_hours=1),
            ProcessStep(id="step_3", action=ActionType.NOTIFICATION,
                       label="Duty of Candour — inform patient/family within 24h (statutory requirement)",
                       target="Patient / Family",
                       deadline_hours=24,
                       notification_template="We are sorry that {incident_description}. We are investigating and will share the findings with you within {timeframe}. You are entitled to support and representation throughout this process."),
            ProcessStep(id="step_4", action=ActionType.NOTIFICATION,
                       label="Assign investigating team (Clinical Lead + Governance)",
                       target="Clinical Governance Lead",
                       deadline_hours=24),
            ProcessStep(id="step_5", action=ActionType.UPDATE_ITEM,
                       label="Investigation — root cause analysis, staff interviews, evidence review",
                       target="Investigating Team",
                       deadline_hours=168),  # 7 days
            ProcessStep(id="step_6", action=ActionType.APPROVAL,
                       label="Review findings and proposed improvement actions",
                       target="Clinical Governance Committee",
                       deadline_hours=72,
                       on_approve="step_7", on_reject="step_5"),
            ProcessStep(id="step_7", action=ActionType.UPDATE_ITEM,
                       label="Implement improvement actions + set review date (30/60/90 days)",
                       target="Department Lead"),
            ProcessStep(id="step_8", action=ActionType.LOG,
                       label="Close — record on LFPSE, share learning, update risk register",
                       target="Clinical Governance Lead"),
        ],
        compliance_checklist=[
            "Harm level assessed and graded",
            "CQC notification if severe harm/death",
            "Duty of Candour fulfilled (statutory)",
            "Root cause analysis completed",
            "Improvement actions tracked to completion",
            "LFPSE submission",
        ],
        tags=["incident", "patient-safety", "duty-of-candour", "lfpse", "governance"],
        estimated_complexity="complex",
    )


@register
def equality_impact_assessment() -> ProcessSpec:
    """Equality Impact Assessment — Public Sector Equality Duty"""
    return ProcessSpec(
        name="Equality Impact Assessment (EqIA)",
        description="Assess the impact of a policy, service change, or project on people with protected characteristics. Required under the Equality Act 2010 Public Sector Equality Duty.",
        domain="government",
        regulation_ref="Equality Act 2010 s.149 (Public Sector Equality Duty)",
        trigger=TriggerType.MANUAL,
        steps=[
            ProcessStep(id="step_1", action=ActionType.CONDITION,
                       label="Screening: Does the proposal affect people? If no people impact, EqIA not required.",
                       condition="@equals(variables('HasPeopleImpact'), true)",
                       on_approve="step_2", on_reject="step_7"),
            ProcessStep(id="step_2", action=ActionType.UPDATE_ITEM,
                       label="Describe the proposal and gather data on affected groups (age, disability, sex, race, religion, sexual orientation, gender reassignment, pregnancy, marriage)",
                       target="Policy Lead",
                       deadline_hours=120),
            ProcessStep(id="step_3", action=ActionType.UPDATE_ITEM,
                       label="Assess impact on each protected characteristic — positive, negative, or neutral",
                       target="Equality Lead",
                       deadline_hours=72),
            ProcessStep(id="step_4", action=ActionType.APPROVAL,
                       label="Review — is there disproportionate negative impact on any group?",
                       target="Equality & Diversity Committee",
                       deadline_hours=240,
                       on_approve="step_5", on_reject="step_6"),
            ProcessStep(id="step_5", action=ActionType.UPDATE_ITEM,
                       label="Propose mitigation measures — reasonable adjustments, alternative approaches",
                       target="Policy Lead"),
            ProcessStep(id="step_6", action=ActionType.APPROVAL,
                       label="Final sign-off by Senior Responsible Officer",
                       target="SRO / Director",
                       deadline_hours=72,
                       on_approve="step_7", on_reject="step_5"),
            ProcessStep(id="step_7", action=ActionType.LOG,
                       label="Publish EqIA and record in register — set review date",
                       target="Equality Lead"),
        ],
        compliance_checklist=[
            "All 9 protected characteristics considered",
            "Data used to assess impact (not assumptions)",
            "Negative impacts identified and mitigated",
            "Consultation with affected groups where evidence gaps",
            "Published and accessible",
            "Review date set",
        ],
        tags=["equality", "eia", "psed", "public-sector", "inclusion"],
        estimated_complexity="medium",
    )


# ── Template Matcher ──────────────────────────────────────────────────


def match_template(description: str, domain: str = "general") -> ProcessSpec | None:
    """
    Match an English description to the closest template using keyword analysis.
    Returns None if no close match found (caller should use LLM fallback).
    """
    description_lower = description.lower()

    # Keyword scoring
    scores: dict[str, int] = {}
    keyword_map = {
        "foi": ["foi", "freedom of information", "foia", "ico", "public interest test"],
        "sar": ["sar", "subject access", "dsar", "right of access", "data subject", "personal data request"],
        "dpia": ["dpia", "data protection impact", "high risk processing", "article 35", "dsp"],
        "whistleblowing": ["whistleblow", "freedom to speak up", "ftsu", "speaking up", "pida", "protected disclosure"],
        "incident": ["incident", "near miss", "patient safety event", "harm", "duty of candour", "lfpse"],
        "equality": ["equality impact", "eqia", "psed", "protected characteristic", "equality act", "discrimination"],
    }

    for template_name, keywords in keyword_map.items():
        score = sum(2 if kw in description_lower else 0 for kw in keywords)
        if score > 0:
            scores[template_name] = score

    if not scores:
        return None

    # Return highest-scoring template, requiring at least 2 keyword matches
    best = max(scores, key=scores.get)
    if scores[best] < 2:
        return None

    # Map keyword names to TEMPLATES keys
    template_key_map = {
        "foi": "foi-request-processing",
        "sar": "subject-access-request-processing",
        "dpia": "data-protection-impact-assessment-(dpia)",
        "whistleblowing": "whistleblowing-/-freedom-to-speak-up",
        "incident": "incident-&-near-miss-reporting",
        "equality": "equality-impact-assessment-(eqia)",
    }

    template_key = template_key_map.get(best, best)
    return TEMPLATES.get(template_key)
