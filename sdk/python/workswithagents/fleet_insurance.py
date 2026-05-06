     1|"""
     2|Fleet Insurance — Reference Implementation
     3|Risk scoring, actuarial data, and claims verification for agent fleet insurance.
     4|Reference implementation. CC BY 4.0.
     5|"""
     6|
     7|from dataclasses import dataclass, field
     8|from datetime import datetime, timezone
     9|from typing import Optional
    10|from uuid import uuid4
    11|
    12|
    13|@dataclass
    14|class RiskProfile:
    15|    """Risk assessment for an agent fleet — the actuarial data insurers need."""
    16|    fleet_id: str = ""
    17|    trust_score: float = 0.0          # 0-100, from Trust Score Protocol
    18|    sla_compliance: float = 0.0       # % of SLAs met (0-100)
    19|    audit_trail_depth_days: int = 0   # Days of continuous audit coverage
    20|    model_safety_rate: float = 0.0    # Quality gate pass rate (0-100)
    21|    incidents_last_90d: int = 0       # Number of reported incidents
    22|    agent_count: int = 0
    23|    tasks_completed: int = 0
    24|    tasks_failed: int = 0
    25|    domains: list[str] = field(default_factory=list)  # healthcare, finance, govt
    26|
    27|
    28|@dataclass
    29|class Policy:
    30|    """Insurance policy for an agent fleet."""
    31|    policy_id: str = field(default_factory=lambda: str(uuid4()))
    32|    fleet_id: str = ""
    33|    risk_score: float = 0.0
    34|    premium_monthly: float = 0.0
    35|    coverage_limit: float = 0.0
    36|    deductible: float = 0.0
    37|    exclusions: list[str] = field(default_factory=list)
    38|    effective_from: str = ""
    39|    expires: str = ""
    40|
    41|
    42|@dataclass
    43|class Claim:
    44|    """An insurance claim for an agent incident."""
    45|    claim_id: str = field(default_factory=lambda: str(uuid4()))
    46|    policy_id: str = ""
    47|    incident_id: str = ""
    48|    filed_by: str = ""
    49|    amount_claimed: float = 0.0
    50|    status: str = "filed"  # filed, under_review, approved, denied, paid
    51|    evidence: dict = field(default_factory=dict)
    52|    filed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    53|
    54|
    55|class FleetInsurance:
    56|    """
    57|    Risk scoring and claims engine for agent fleet insurance.
    58|    Does NOT underwrite — provides actuarial data for insurer partners.
    59|
    60|    Usage:
    61|        fi = FleetInsurance()
    62|        risk = fi.assess_risk(fleet_id="fleet-01", trust_score=85,
    63|                              sla_compliance=97, incidents=2)
    64|        policy = fi.generate_policy(risk, fleet_id="fleet-01",
    65|                                     coverage=100000, deductible=5000)
    66|        claim = fi.file_claim(policy.policy_id, "incident-42", amount=15000)
    67|    """
    68|
    69|    # Premium calculation weights
    70|    BASE_PREMIUM = 500.0       # £/month base
    71|    TRUST_WEIGHT = -10.0       # -£10 per trust score point (higher trust = cheaper)
    72|    INCIDENT_WEIGHT = 100.0    # +£100 per incident in last 90d
    73|    SLA_PENALTY = 5.0          # +£5 per % below 100% SLA compliance
    74|    DOMAIN_SURCHARGE = {
    75|        "healthcare": 0.3,     # 30% surcharge for clinical risk
    76|        "finance": 0.2,        # 20% surcharge for financial risk
    77|        "government": 0.1,     # 10% surcharge for govt
    78|    }
    79|
    80|    def __init__(self, underwriter_partner: str = ""):
    81|        self.underwriter = underwriter_partner
    82|        self._policies: dict[str, Policy] = {}
    83|        self._claims: dict[str, Claim] = {}
    84|
    85|    def assess_risk(self, fleet_id: str, *,
    86|                    trust_score: float = 0.0,
    87|                    sla_compliance: float = 0.0,
    88|                    audit_trail_depth_days: int = 0,
    89|                    model_safety_rate: float = 0.0,
    90|                    incidents_last_90d: int = 0,
    91|                    agent_count: int = 0,
    92|                    tasks_completed: int = 0,
    93|                    tasks_failed: int = 0,
    94|                    domains: Optional[list[str]] = None) -> RiskProfile:
    95|        """Produce a risk profile for underwriting."""
    96|        domains = domains or []
    97|        failure_rate = tasks_failed / max(tasks_completed, 1)
    98|
    99|        return RiskProfile(
   100|            fleet_id=fleet_id,
   101|            trust_score=trust_score,
   102|            sla_compliance=sla_compliance,
   103|            audit_trail_depth_days=audit_trail_depth_days,
   104|            model_safety_rate=model_safety_rate,
   105|            incidents_last_90d=incidents_last_90d,
   106|            agent_count=agent_count,
   107|            tasks_completed=tasks_completed,
   108|            tasks_failed=tasks_failed,
   109|            domains=domains,
   110|        )
   111|
   112|    def calculate_premium(self, risk: RiskProfile, coverage_limit: float) -> float:
   113|        """Calculate monthly premium from risk profile."""
   114|        premium = self.BASE_PREMIUM
   115|
   116|        # Trust score discount
   117|        premium += self.TRUST_WEIGHT * risk.trust_score
   118|
   119|        # Incident loading
   120|        premium += self.INCIDENT_WEIGHT * risk.incidents_last_90d
   121|
   122|        # SLA compliance penalty
   123|        if risk.sla_compliance < 100:
   124|            premium += self.SLA_PENALTY * (100 - risk.sla_compliance)
   125|
   126|        # Domain risk surcharge
   127|        domain_multiplier = 1.0
   128|        for domain in risk.domains:
   129|            domain_multiplier += self.DOMAIN_SURCHARGE.get(domain, 0)
   130|        premium *= domain_multiplier
   131|
   132|        # Minimum premium floor
   133|        premium = max(premium, 100.0)
   134|
   135|        return round(premium, 2)
   136|
   137|    def calculate_risk_score(self, risk: RiskProfile) -> float:
   138|        """0-100 risk score. Higher = riskier."""
   139|        score = 100.0
   140|        score -= risk.trust_score * 0.4          # Trust reduces risk
   141|        score += risk.incidents_last_90d * 5.0   # Incidents increase risk
   142|        score -= risk.sla_compliance * 0.2       # SLA compliance reduces risk
   143|        score -= risk.model_safety_rate * 0.2    # Model safety reduces risk
   144|        score -= min(risk.audit_trail_depth_days / 30, 20)  # Audit depth reduces risk
   145|
   146|        score = max(0.0, min(100.0, score))
   147|        return round(score, 1)
   148|
   149|    def generate_policy(self, risk: RiskProfile, *,
   150|                        coverage_limit: float = 100000.0,
   151|                        deductible: float = 1000.0) -> Policy:
   152|        """Generate an insurance policy from a risk assessment."""
   153|        risk_score = self.calculate_risk_score(risk)
   154|        premium = self.calculate_premium(risk, coverage_limit)
   155|
   156|        policy = Policy(
   157|            fleet_id=risk.fleet_id,
   158|            risk_score=risk_score,
   159|            premium_monthly=premium,
   160|            coverage_limit=coverage_limit,
   161|            deductible=deductible,
   162|            exclusions=["intentional_misuse", "human_override", "force_majeure"],
   163|            effective_from=datetime.now(timezone.utc).isoformat(),
   164|            expires=datetime.fromisoformat(datetime.now(timezone.utc).isoformat()
   165|                  ).replace(year=datetime.now().year + 1).isoformat(),
   166|        )
   167|        self._policies[policy.policy_id] = policy
   168|        return policy
   169|
   170|    def file_claim(self, policy_id: str, incident_id: str, *,
   171|                   filed_by: str = "", amount: float = 0.0,
   172|                   evidence: Optional[dict] = None) -> Claim:
   173|        """File an insurance claim for an agent incident."""
   174|        if policy_id not in self._policies:
   175|            raise ValueError(f"Policy {policy_id} not found")
   176|
   177|        policy = self._policies[policy_id]
   178|        if amount > policy.coverage_limit:
   179|            raise ValueError(f"Claim {amount} exceeds coverage {policy.coverage_limit}")
   180|
   181|        claim = Claim(
   182|            policy_id=policy_id,
   183|            incident_id=incident_id,
   184|            filed_by=filed_by,
   185|            amount_claimed=amount,
   186|            evidence=evidence or {},
   187|        )
   188|        self._claims[claim.claim_id] = claim
   189|        return claim
   190|
   191|    def resolve_claim(self, claim_id: str, status: str, *,
   192|                      paid_amount: float = 0.0) -> Claim:
   193|        """Approve or deny a claim."""
   194|        if claim_id not in self._claims:
   195|            raise ValueError(f"Claim {claim_id} not found")
   196|        claim = self._claims[claim_id]
   197|        claim.status = status
   198|        return claim
   199|
   200|    def fleet_summary(self, fleet_id: str) -> dict:
   201|        """Summary for a fleet's insurance status."""
   202|        policies = [p for p in self._policies.values() if p.fleet_id == fleet_id]
   203|        claims = [c for c in self._claims.values()
   204|                  if c.policy_id in {p.policy_id for p in policies}]
   205|        return {
   206|            "fleet_id": fleet_id,
   207|            "active_policies": len(policies),
   208|            "total_coverage": sum(p.coverage_limit for p in policies),
   209|            "claims_filed": len(claims),
   210|            "claims_pending": sum(1 for c in claims if c.status not in ("paid", "denied")),
   211|            "underwriter": self.underwriter,
   212|        }
   213|