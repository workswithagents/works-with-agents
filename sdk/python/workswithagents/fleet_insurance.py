"""
Fleet Insurance — Strategic Concept
Risk scoring, actuarial data, and claims verification for agent fleet insurance.
Reference implementation. CC BY 4.0.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


@dataclass
class RiskProfile:
    """Risk assessment for an agent fleet — the actuarial data insurers need."""
    fleet_id: str = ""
    trust_score: float = 0.0          # 0-100, from Trust Score Protocol
    sla_compliance: float = 0.0       # % of SLAs met (0-100)
    audit_trail_depth_days: int = 0   # Days of continuous audit coverage
    model_safety_rate: float = 0.0    # Quality gate pass rate (0-100)
    incidents_last_90d: int = 0       # Number of reported incidents
    agent_count: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    domains: list[str] = field(default_factory=list)  # healthcare, finance, govt


@dataclass
class Policy:
    """Insurance policy for an agent fleet."""
    policy_id: str = field(default_factory=lambda: str(uuid4()))
    fleet_id: str = ""
    risk_score: float = 0.0
    premium_monthly: float = 0.0
    coverage_limit: float = 0.0
    deductible: float = 0.0
    exclusions: list[str] = field(default_factory=list)
    effective_from: str = ""
    expires: str = ""


@dataclass
class Claim:
    """An insurance claim for an agent incident."""
    claim_id: str = field(default_factory=lambda: str(uuid4()))
    policy_id: str = ""
    incident_id: str = ""
    filed_by: str = ""
    amount_claimed: float = 0.0
    status: str = "filed"  # filed, under_review, approved, denied, paid
    evidence: dict = field(default_factory=dict)
    filed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class FleetInsurance:
    """
    Risk scoring and claims engine for agent fleet insurance.
    Does NOT underwrite — provides actuarial data for insurer partners.

    Usage:
        fi = FleetInsurance()
        risk = fi.assess_risk(fleet_id="fleet-01", trust_score=85,
                              sla_compliance=97, incidents=2)
        policy = fi.generate_policy(risk, fleet_id="fleet-01",
                                     coverage=100000, deductible=5000)
        claim = fi.file_claim(policy.policy_id, "incident-42", amount=15000)
    """

    # Premium calculation weights
    BASE_PREMIUM = 500.0       # £/month base
    TRUST_WEIGHT = -10.0       # -£10 per trust score point (higher trust = cheaper)
    INCIDENT_WEIGHT = 100.0    # +£100 per incident in last 90d
    SLA_PENALTY = 5.0          # +£5 per % below 100% SLA compliance
    DOMAIN_SURCHARGE = {
        "healthcare": 0.3,     # 30% surcharge for clinical risk
        "finance": 0.2,        # 20% surcharge for financial risk
        "government": 0.1,     # 10% surcharge for govt
    }

    def __init__(self, underwriter_partner: str = ""):
        self.underwriter = underwriter_partner
        self._policies: dict[str, Policy] = {}
        self._claims: dict[str, Claim] = {}

    def assess_risk(self, fleet_id: str, *,
                    trust_score: float = 0.0,
                    sla_compliance: float = 0.0,
                    audit_trail_depth_days: int = 0,
                    model_safety_rate: float = 0.0,
                    incidents_last_90d: int = 0,
                    agent_count: int = 0,
                    tasks_completed: int = 0,
                    tasks_failed: int = 0,
                    domains: Optional[list[str]] = None) -> RiskProfile:
        """Produce a risk profile for underwriting."""
        domains = domains or []
        failure_rate = tasks_failed / max(tasks_completed, 1)

        return RiskProfile(
            fleet_id=fleet_id,
            trust_score=trust_score,
            sla_compliance=sla_compliance,
            audit_trail_depth_days=audit_trail_depth_days,
            model_safety_rate=model_safety_rate,
            incidents_last_90d=incidents_last_90d,
            agent_count=agent_count,
            tasks_completed=tasks_completed,
            tasks_failed=tasks_failed,
            domains=domains,
        )

    def calculate_premium(self, risk: RiskProfile, coverage_limit: float) -> float:
        """Calculate monthly premium from risk profile."""
        premium = self.BASE_PREMIUM

        # Trust score discount
        premium += self.TRUST_WEIGHT * risk.trust_score

        # Incident loading
        premium += self.INCIDENT_WEIGHT * risk.incidents_last_90d

        # SLA compliance penalty
        if risk.sla_compliance < 100:
            premium += self.SLA_PENALTY * (100 - risk.sla_compliance)

        # Domain risk surcharge
        domain_multiplier = 1.0
        for domain in risk.domains:
            domain_multiplier += self.DOMAIN_SURCHARGE.get(domain, 0)
        premium *= domain_multiplier

        # Minimum premium floor
        premium = max(premium, 100.0)

        return round(premium, 2)

    def calculate_risk_score(self, risk: RiskProfile) -> float:
        """0-100 risk score. Higher = riskier."""
        score = 100.0
        score -= risk.trust_score * 0.4          # Trust reduces risk
        score += risk.incidents_last_90d * 5.0   # Incidents increase risk
        score -= risk.sla_compliance * 0.2       # SLA compliance reduces risk
        score -= risk.model_safety_rate * 0.2    # Model safety reduces risk
        score -= min(risk.audit_trail_depth_days / 30, 20)  # Audit depth reduces risk

        score = max(0.0, min(100.0, score))
        return round(score, 1)

    def generate_policy(self, risk: RiskProfile, *,
                        coverage_limit: float = 100000.0,
                        deductible: float = 1000.0) -> Policy:
        """Generate an insurance policy from a risk assessment."""
        risk_score = self.calculate_risk_score(risk)
        premium = self.calculate_premium(risk, coverage_limit)

        policy = Policy(
            fleet_id=risk.fleet_id,
            risk_score=risk_score,
            premium_monthly=premium,
            coverage_limit=coverage_limit,
            deductible=deductible,
            exclusions=["intentional_misuse", "human_override", "force_majeure"],
            effective_from=datetime.now(timezone.utc).isoformat(),
            expires=datetime.fromisoformat(datetime.now(timezone.utc).isoformat()
                  ).replace(year=datetime.now().year + 1).isoformat(),
        )
        self._policies[policy.policy_id] = policy
        return policy

    def file_claim(self, policy_id: str, incident_id: str, *,
                   filed_by: str = "", amount: float = 0.0,
                   evidence: Optional[dict] = None) -> Claim:
        """File an insurance claim for an agent incident."""
        if policy_id not in self._policies:
            raise ValueError(f"Policy {policy_id} not found")

        policy = self._policies[policy_id]
        if amount > policy.coverage_limit:
            raise ValueError(f"Claim {amount} exceeds coverage {policy.coverage_limit}")

        claim = Claim(
            policy_id=policy_id,
            incident_id=incident_id,
            filed_by=filed_by,
            amount_claimed=amount,
            evidence=evidence or {},
        )
        self._claims[claim.claim_id] = claim
        return claim

    def resolve_claim(self, claim_id: str, status: str, *,
                      paid_amount: float = 0.0) -> Claim:
        """Approve or deny a claim."""
        if claim_id not in self._claims:
            raise ValueError(f"Claim {claim_id} not found")
        claim = self._claims[claim_id]
        claim.status = status
        return claim

    def fleet_summary(self, fleet_id: str) -> dict:
        """Summary for a fleet's insurance status."""
        policies = [p for p in self._policies.values() if p.fleet_id == fleet_id]
        claims = [c for c in self._claims.values()
                  if c.policy_id in {p.policy_id for p in policies}]
        return {
            "fleet_id": fleet_id,
            "active_policies": len(policies),
            "total_coverage": sum(p.coverage_limit for p in policies),
            "claims_filed": len(claims),
            "claims_pending": sum(1 for c in claims if c.status not in ("paid", "denied")),
            "underwriter": self.underwriter,
        }
