/**
 * Agent SLA Framework — Layer 7 Governance (TypeScript)
 * Define and track Service Level Agreements for agent fleets.
 * Reference implementation. CC BY 4.0.
 */

const DEFAULT_API = "https://workswithagents.dev";

export type SLATier = "best_effort" | "production" | "regulated";

export interface SLATargets {
  uptime?: number;
  accuracy?: number;
  latency_p95?: number;
  latency_p99?: number;
  recovery?: number;
  compliance?: number;
  audit_retention_days?: number;
}

const TIERS: Record<SLATier, SLATargets> = {
  best_effort: { uptime: 0.95, accuracy: 0.80 },
  production: { uptime: 0.995, accuracy: 0.90, latency_p95: 300, recovery: 0.95 },
  regulated: { uptime: 0.999, accuracy: 0.95, latency_p99: 120, compliance: 1.0, recovery: 0.99, audit_retention_days: 2555 },
};

export class SLAMetrics {
  fleet_id: string;
  tier: SLATier;
  api: string;
  targets: SLATargets;

  constructor(fleet_id: string, tier: SLATier = "production", api_url: string = DEFAULT_API) {
    this.fleet_id = fleet_id;
    this.tier = tier;
    this.api = api_url.replace(/\/$/, "");
    this.targets = TIERS[tier] || TIERS.production;
  }

  async report(
    agent_id: string,
    action_id: string,
    duration_seconds: number,
    success: boolean,
    guarantee_level?: string
  ): Promise<Record<string, unknown>> {
    const payload: Record<string, unknown> = {
      fleet_id: this.fleet_id,
      agent_id,
      action_id,
      duration_seconds,
      success,
      timestamp: Math.floor(Date.now() / 1000),
    };
    if (guarantee_level) payload.guarantee_level = guarantee_level;
    return this.request("POST", "/v1/sla/report", payload);
  }

  async status(): Promise<Record<string, unknown>> {
    return this.request("GET", `/v1/sla/${this.fleet_id}/status`);
  }

  async reportMonthly(period: string): Promise<Record<string, unknown>> {
    return this.request("GET", `/v1/sla/${this.fleet_id}/report?period=${period}`);
  }

  checkBreach(metric: string, actual: number): string | null {
    const target = (this.targets as any)[metric];
    if (target == null) return null;
    if (actual < target) return `${metric}: ${actual.toFixed(3)} < target ${target.toFixed(3)}`;
    return null;
  }

  private async request(method: string, path: string, data?: Record<string, unknown>): Promise<any> {
    const url = `${this.api}${path}`;
    const opts: RequestInit = { method, headers: { "Content-Type": "application/json" } };
    if (data) opts.body = JSON.stringify(data);
    const resp = await fetch(url, opts);
    return resp.json();
  }
}
