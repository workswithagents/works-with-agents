/**
 * Fleet Insurance — Strategic Concept (TypeScript)
 * Risk scoring, actuarial data, and claims verification for agent fleet insurance.
 * Reference implementation. CC BY 4.0.
 */

export interface RiskProfile {
  fleet_id: string;
  trust_score: number;
  sla_compliance: number;
  audit_trail_depth_days: number;
  model_safety_rate: number;
  incidents_last_90d: number;
  agent_count: number;
  tasks_completed: number;
  tasks_failed: number;
  domains: string[];
}

export interface Policy {
  policy_id: string;
  fleet_id: string;
  risk_score: number;
  premium_monthly: number;
  coverage_limit: number;
  deductible: number;
  exclusions: string[];
  effective_from: string;
  expires: string;
}

export interface Claim {
  claim_id: string;
  policy_id: string;
  incident_id: string;
  filed_by: string;
  amount_claimed: number;
  status: string;
  evidence: Record<string, unknown>;
  filed_at: string;
}

const DOMAIN_SURCHARGE: Record<string, number> = {
  healthcare: 0.3,
  finance: 0.2,
  government: 0.1,
};

const BASE_PREMIUM = 500.0;
const TRUST_WEIGHT = -10.0;
const INCIDENT_WEIGHT = 100.0;
const SLA_PENALTY = 5.0;

export class FleetInsurance {
  underwriter: string;
  private policies: Map<string, Policy> = new Map();
  private claims: Map<string, Claim> = new Map();

  constructor(underwriter = "") {
    this.underwriter = underwriter;
  }

  assessRisk(fleet_id: string, opts: {
    trust_score?: number;
    sla_compliance?: number;
    audit_trail_depth_days?: number;
    model_safety_rate?: number;
    incidents_last_90d?: number;
    agent_count?: number;
    tasks_completed?: number;
    tasks_failed?: number;
    domains?: string[];
  }): RiskProfile {
    const domains = opts.domains || [];
    return {
      fleet_id,
      trust_score: opts.trust_score || 0,
      sla_compliance: opts.sla_compliance || 0,
      audit_trail_depth_days: opts.audit_trail_depth_days || 0,
      model_safety_rate: opts.model_safety_rate || 0,
      incidents_last_90d: opts.incidents_last_90d || 0,
      agent_count: opts.agent_count || 0,
      tasks_completed: opts.tasks_completed || 0,
      tasks_failed: opts.tasks_failed || 0,
      domains,
    };
  }

  calculateRiskScore(risk: RiskProfile): number {
    let score = 100.0;
    score -= risk.trust_score * 0.4;
    score += risk.incidents_last_90d * 5.0;
    score -= risk.sla_compliance * 0.2;
    score -= risk.model_safety_rate * 0.2;
    score -= Math.min(risk.audit_trail_depth_days / 30, 20);
    return Math.round(Math.max(0, Math.min(100, score)) * 10) / 10;
  }

  calculatePremium(risk: RiskProfile, coverageLimit: number): number {
    let premium = BASE_PREMIUM;
    premium += TRUST_WEIGHT * risk.trust_score;
    premium += INCIDENT_WEIGHT * risk.incidents_last_90d;
    if (risk.sla_compliance < 100) {
      premium += SLA_PENALTY * (100 - risk.sla_compliance);
    }
    let multiplier = 1.0;
    for (const domain of risk.domains) {
      multiplier += DOMAIN_SURCHARGE[domain] || 0;
    }
    premium *= multiplier;
    return Math.round(Math.max(premium, 100) * 100) / 100;
  }

  generatePolicy(risk: RiskProfile, opts: {
    coverage_limit?: number;
    deductible?: number;
  }): Policy {
    const riskScore = this.calculateRiskScore(risk);
    const premium = this.calculatePremium(risk, opts.coverage_limit || 100000);
    const policy: Policy = {
      policy_id: crypto.randomUUID(),
      fleet_id: risk.fleet_id,
      risk_score: riskScore,
      premium_monthly: premium,
      coverage_limit: opts.coverage_limit || 100000,
      deductible: opts.deductible || 1000,
      exclusions: ["intentional_misuse", "human_override", "force_majeure"],
      effective_from: new Date().toISOString(),
      expires: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString(),
    };
    this.policies.set(policy.policy_id, policy);
    return policy;
  }

  fileClaim(policy_id: string, incident_id: string, opts: {
    filed_by?: string;
    amount?: number;
    evidence?: Record<string, unknown>;
  }): Claim {
    const policy = this.policies.get(policy_id);
    if (!policy) throw new Error(`Policy ${policy_id} not found`);
    if ((opts.amount || 0) > policy.coverage_limit) {
      throw new Error(`Claim amount exceeds coverage`);
    }
    const claim: Claim = {
      claim_id: crypto.randomUUID(),
      policy_id,
      incident_id,
      filed_by: opts.filed_by || "",
      amount_claimed: opts.amount || 0,
      status: "filed",
      evidence: opts.evidence || {},
      filed_at: new Date().toISOString(),
    };
    this.claims.set(claim.claim_id, claim);
    return claim;
  }

  fleetSummary(fleet_id: string): Record<string, unknown> {
    const policies = Array.from(this.policies.values())
      .filter(p => p.fleet_id === fleet_id);
    const policyIds = new Set(policies.map(p => p.policy_id));
    const claims = Array.from(this.claims.values())
      .filter(c => policyIds.has(c.policy_id));
    return {
      fleet_id,
      active_policies: policies.length,
      total_coverage: policies.reduce((s, p) => s + p.coverage_limit, 0),
      claims_filed: claims.length,
      claims_pending: claims.filter(c => !["paid", "denied"].includes(c.status)).length,
      underwriter: this.underwriter,
    };
  }
}
