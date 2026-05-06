/**
 * Works With Agents — TypeScript SDK
 * Reference implementations for all Agent OSI Model protocols.
 * Zero dependencies. Copy-pasteable. CC BY 4.0.
 */


// Re-export from modular protocol files
export { CoordinationClient, AgentRole } from "./coordination";
export { TransactionLedger, TransactionStatus } from "./transaction";
export { FleetInsurance } from "./fleet_insurance";
export type { CoordinationMessage } from "./coordination";
export type { Transaction, TransactionAction } from "./transaction";
export type { RiskProfile, Policy, Claim } from "./fleet_insurance";
const DEFAULT_API = "https://workswithagents.dev";

async function request(method: string, path: string, data?: object): Promise<any> {
  const res = await fetch(`${DEFAULT_API}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: data ? JSON.stringify(data) : undefined,
  });
  return res.json();
}

// ── Trust Score ──────────────────────────────────────────────────────

export class TrustScoreClient {
  constructor(private api: string = DEFAULT_API) {}

  async get(agentId: string) {
    const res = await fetch(`${this.api}/v1/trust/${agentId}`);
    return res.json();
  }

  async report(agentId: string, opts: { successRate: number; pitfalls?: number; skills?: number }) {
    return request("POST", "/v1/trust/report", {
      agent_id: agentId,
      success_rate: opts.successRate,
      pitfalls_contributed: opts.pitfalls ?? 0,
      skills_published: opts.skills ?? 0,
    });
  }

  async rate(fromAgent: string, toAgent: string, rating: number) {
    return request("POST", "/v1/trust/rate", { from_agent: fromAgent, to_agent: toAgent, rating });
  }

  async listTrusted() {
    return request("GET", "/v1/trust?tier=trusted");
  }

  async history(agentId: string) {
    return request("GET", `/v1/trust/${agentId}/history`);
  }
}

// ── Deployment Manifest ──────────────────────────────────────────────

export interface AgentCapability {
  action: string;
  target: string;
  success_rate?: number;
}

export interface AgentDef {
  id: string;
  type?: string;
  capabilities: AgentCapability[];
  count?: number;
  skills?: string[];
}

export interface FleetManifest {
  manifest_version: string;
  fleet: {
    name: string;
    agents: AgentDef[];
    registry?: string;
    coordination?: string;
    compliance?: Record<string, any>;
  };
}

export class DeploymentManifest {
  private fleetId: string | null = null;

  constructor(private manifest: FleetManifest, private api: string = DEFAULT_API) {}

  static fromObject(obj: FleetManifest, api?: string): DeploymentManifest {
    return new DeploymentManifest(obj, api);
  }

  static fromJson(json: string, api?: string): DeploymentManifest {
    return new DeploymentManifest(JSON.parse(json), api);
  }

  static minimal(name: string, agentId: string, capabilities: AgentCapability[], api?: string): DeploymentManifest {
    return new DeploymentManifest({
      manifest_version: "1.0.0-draft",
      fleet: { name, agents: [{ id: agentId, capabilities }] }
    }, api);
  }

  validate(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    const mf = this.manifest;
    if (!mf.manifest_version) errors.push("Missing manifest_version");
    if (!mf.fleet) errors.push("Missing fleet");
    else {
      if (!mf.fleet.name) errors.push("Missing fleet.name");
      if (!mf.fleet.agents?.length) errors.push("Missing fleet.agents");
      mf.fleet.agents?.forEach((a, i) => {
        if (!a.id) errors.push(`Agent[${i}]: missing id`);
        if (!a.capabilities?.length) errors.push(`Agent[${i}]: missing capabilities`);
      });
    }
    return { valid: errors.length === 0, errors };
  }

  async deploy() {
    const v = this.validate();
    if (!v.valid) return { status: "error", errors: v.errors };
    const res = await fetch(`${this.api}/v1/fleets/deploy`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(this.manifest),
    });
    const result = await res.json();
    if (result.fleet_id) this.fleetId = result.fleet_id;
    return result;
  }

  async status() {
    if (!this.fleetId) return { error: "Not deployed" };
    const res = await fetch(`${this.api}/v1/fleets/${this.fleetId}/status`);
    return res.json();
  }

  async scale(agentType: string, count: number) {
    if (!this.fleetId) return { error: "Not deployed" };
    return request("POST", `/v1/fleets/${this.fleetId}/scale`, { agent_type: agentType, count });
  }
}

// ── SLA Framework ────────────────────────────────────────────────────

export class SLAMetrics {
  static TIERS: Record<string, Record<string, number>> = {
    best_effort: { uptime: 0.95, accuracy: 0.80 },
    production: { uptime: 0.995, accuracy: 0.90, latency_p95: 300, recovery: 0.95 },
    regulated: { uptime: 0.999, accuracy: 0.95, latency_p99: 120, compliance: 1.0, recovery: 0.99 },
  };

  constructor(private fleetId: string, private tier: string = "production", private api: string = DEFAULT_API) {}

  get targets() { return SLAMetrics.TIERS[this.tier] ?? SLAMetrics.TIERS.production; }

  async report(agentId: string, actionId: string, opts: { durationSeconds: number; success: boolean; guaranteeLevel?: string }) {
    return request("POST", "/v1/sla/report", {
      fleet_id: this.fleetId, agent_id: agentId, action_id: actionId,
      duration_seconds: opts.durationSeconds, success: opts.success,
      timestamp: Math.floor(Date.now() / 1000),
      guarantee_level: opts.guaranteeLevel,
    });
  }

  async status() {
    const res = await fetch(`${this.api}/v1/sla/${this.fleetId}/status`);
    return res.json();
  }

  checkBreach(metric: string, actual: number): string | null {
    const target = this.targets[metric];
    if (target === undefined) return null;
    return actual < target ? `${metric}: ${actual} < target ${target}` : null;
  }
}

// ── Identity Protocol ────────────────────────────────────────────────

export class AgentIdentity {
  private privateKey: Uint8Array | null = null;
  private publicKey: Uint8Array | null = null;

  constructor(private agentId: string, private api: string = DEFAULT_API) {
    // Try loading from localStorage
    const saved = typeof localStorage !== "undefined" ? localStorage.getItem(`wwa_key_${agentId}`) : null;
    if (saved) {
      const keys = JSON.parse(saved);
      this.privateKey = new Uint8Array(Object.values(keys.private));
      this.publicKey = new Uint8Array(Object.values(keys.public));
    }
  }

  async generate(): Promise<{ agentId: string; publicKey: string }> {
    const keypair = await crypto.subtle.generateKey("Ed25519", true, ["sign", "verify"]);
    const pubRaw = await crypto.subtle.exportKey("raw", keypair.publicKey);
    const privRaw = await crypto.subtle.exportKey("pkcs8", keypair.privateKey);
    this.publicKey = new Uint8Array(pubRaw);
    this.privateKey = new Uint8Array(privRaw);
    this.save();
    return { agentId: this.agentId, publicKey: this.hex(this.publicKey) };
  }

  async register(ownerName?: string, ownerEmail?: string) {
    if (!this.publicKey) await this.generate();
    const payload: Record<string, string> = { agent_id: this.agentId, public_key: this.hex(this.publicKey!) };
    if (ownerName) payload.owner_name = ownerName;
    if (ownerEmail) payload.owner_email = ownerEmail;
    return request("POST", "/v1/identity/register", payload);
  }

  async sign(payload: object): Promise<string> {
    if (!this.privateKey) await this.generate();
    const msg = JSON.stringify({ agent_id: this.agentId, timestamp: Math.floor(Date.now() / 1000), payload });
    const key = await crypto.subtle.importKey("pkcs8", this.privateKey!, "Ed25519", true, ["sign"]);
    const sig = await crypto.subtle.sign("Ed25519", key, new TextEncoder().encode(msg));
    return this.hex(new Uint8Array(sig));
  }

  static async verify(agentId: string, message: object, signature: string, api: string = DEFAULT_API): Promise<boolean> {
    const res = await fetch(`${api}/v1/identity/verify`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ agent_id: agentId, message, signature }),
    });
    const data = await res.json();
    return data.valid === true;
  }

  async rotate() {
    if (!this.publicKey) return { error: "No keys" };
    const oldPub = this.hex(this.publicKey);
    await this.generate();
    return request("POST", `/v1/identity/${this.agentId}/rotate`, { new_public_key: this.hex(this.publicKey!), old_public_key: oldPub });
  }

  async revoke(reason = "manual") {
    return request("POST", `/v1/identity/${this.agentId}/revoke`, { reason });
  }

  private hex(buf: Uint8Array): string {
    return Array.from(buf).map(b => b.toString(16).padStart(2, "0")).join("");
  }

  private save() {
    if (typeof localStorage === "undefined") return;
    localStorage.setItem(`wwa_key_${this.agentId}`, JSON.stringify({
      private: Array.from(this.privateKey!),
      public: Array.from(this.publicKey!),
    }));
  }
}

// ── Compliance-as-Code ───────────────────────────────────────────────

export interface ValidationCheck {
  field: string;
  operator: "equals" | "exists" | "in" | "not_in" | "greater_than" | "less_than";
  value?: any;
  message: string;
}

export interface ComplianceRule {
  id: string;
  name: string;
  severity: string;
  validation: ValidationCheck[];
  evidence?: { type: string; description: string }[];
  trigger?: { events?: string[]; data_classification?: string[] };
}

export class ComplianceEngine {
  private cache: Map<string, RegulationPack> = new Map();

  constructor(private api: string = DEFAULT_API) {}

  async load(regulation: string): Promise<RegulationPack> {
    if (this.cache.has(regulation)) return this.cache.get(regulation)!;
    const res = await fetch(`${this.api}/v1/compliance/packs/${regulation}`);
    const rules = await res.json();
    const pack = new RegulationPack(regulation, rules);
    this.cache.set(regulation, pack);
    return pack;
  }

  async listPacks() {
    return request("GET", "/v1/compliance/packs");
  }

  async validate(regulation: string, action: object): Promise<ComplianceResult> {
    const pack = await this.load(regulation);
    return pack.validate(action);
  }
}

export class RegulationPack {
  constructor(public name: string, private rules: any) {}

  validate(action: any): ComplianceResult {
    const violations: string[] = [];
    for (const rule of this.rules.rules ?? []) {
      if (!this.triggered(rule, action)) continue;
      for (const check of rule.validation ?? []) {
        const val = this.getField(action, check.field);
        if (!this.evaluate(val, check.operator, check.value)) {
          violations.push(`${rule.id}: ${check.message}`);
        }
      }
    }
    return { passed: violations.length === 0, violations };
  }

  private triggered(rule: ComplianceRule, action: any): boolean {
    const t = (rule as any).trigger;
    if (!t) return true;
    const events: string[] = t.events ?? [];
    if (events.length && !events.includes(action.verb)) return false;
    const classes: string[] = t.data_classification ?? [];
    if (classes.length && !classes.includes(action.data_classification ?? "internal")) return false;
    return true;
  }

  private getField(obj: any, field: string): any {
    return field.split(".").reduce((o, k) => o?.[k], obj);
  }

  private evaluate(actual: any, op: string, expected: any): boolean {
    switch (op) {
      case "equals": return actual === expected;
      case "exists": return actual != null && actual !== "";
      case "in": return Array.isArray(expected) ? expected.includes(actual) : actual === expected;
      case "not_in": return Array.isArray(expected) ? !expected.includes(actual) : actual !== expected;
      case "greater_than": return actual > expected;
      case "less_than": return actual < expected;
      default: return false;
    }
  }
}

export interface ComplianceResult { passed: boolean; violations: string[]; }

// ── Onboarding Protocol ──────────────────────────────────────────────

export class OnboardingClient {
  constructor(private api: string = DEFAULT_API) {}

  async interview(name: string, purpose: string, opts: {
    capabilities: string[]; skills?: string[]; tools?: string[];
    fleet?: string; constraints?: string[];
  }) {
    return request("POST", "/v1/onboard/interview", { agent_name: name, purpose, ...opts });
  }

  async generate(interviewId: string) {
    return request("POST", `/v1/onboard/${interviewId}/generate`);
  }

  async calibrate(interviewId: string) {
    return request("POST", `/v1/onboard/${interviewId}/calibrate`);
  }

  async benchmark(interviewId: string) {
    return request("POST", `/v1/onboard/${interviewId}/benchmark`);
  }

  async register(interviewId: string) {
    return request("POST", `/v1/onboard/${interviewId}/register`);
  }

  async fullOnboard(name: string, purpose: string, opts: { capabilities: string[]; skills?: string[] }) {
    const r1 = await this.interview(name, purpose, opts);
    const iid = r1.interview_id;
    if (!iid) return { error: "Interview failed", details: r1 };
    const r2 = await this.generate(iid);
    if (r2.error) return { error: "Generation failed", details: r2 };
    const r3 = await this.calibrate(iid);
    if (!r3.passed) return { error: "Calibration failed", results: r3 };
    return this.register(iid);
  }
}

// Convenience: validate before execute
export async function safeExecute(action: object, regulations: string[], api?: string): Promise<boolean> {
  const engine = new ComplianceEngine(api);
  for (const reg of regulations) {
    const r = await engine.validate(reg, action);
    if (!r.passed) return false;
  }
  return true;
}
