/**
 * Compliance-as-Code — Layer 7 Governance (TypeScript)
 * Turn regulation into executable validation rules for AI agents.
 * Reference implementation. CC BY 4.0.
 */

const DEFAULT_API = "https://workswithagents.dev";

export interface ComplianceRule {
  id: string;
  trigger?: { events?: string[]; data_classification?: string[] };
  validation: { field: string; operator: string; value?: unknown; message: string }[];
  evidence?: Record<string, unknown>[];
}

export interface ComplianceResult {
  passed: boolean;
  violations: string[];
  evidence_required: Record<string, unknown>[];
}

export class RegulationPack {
  name: string;
  rules: Record<string, unknown>;
  api: string;

  constructor(name: string, rules: Record<string, unknown>, api_url: string) {
    this.name = name;
    this.rules = rules;
    this.api = api_url;
  }

  validate(action: Record<string, unknown>): ComplianceResult {
    const violations: string[] = [];
    const evidence_required: Record<string, unknown>[] = [];
    const rules = (this.rules.rules || []) as ComplianceRule[];

    for (const rule of rules) {
      if (!this.triggered(rule, action)) continue;
      for (const check of rule.validation) {
        const fieldValue = this.getField(action, check.field);
        const passed = this.checkOp(fieldValue, check.operator, check.value);
        if (!passed) violations.push(`${rule.id}: ${check.message}`);
      }
      if (rule.evidence) evidence_required.push(...rule.evidence);
    }
    return { passed: violations.length === 0, violations, evidence_required };
  }

  private triggered(rule: ComplianceRule, action: Record<string, unknown>): boolean {
    const trigger = rule.trigger;
    if (!trigger) return true;
    if (trigger.events?.length && !trigger.events.includes(action.verb as string)) return false;
    if (trigger.data_classification?.length) {
      const cls = (action.data_classification as string) || "internal";
      if (!trigger.data_classification.includes(cls)) return false;
    }
    return true;
  }

  private getField(obj: Record<string, unknown>, field: string): unknown {
    return field.split(".").reduce((o: any, k) => (o != null ? o[k] : undefined), obj);
  }

  private checkOp(actual: unknown, operator: string, expected: unknown): boolean {
    switch (operator) {
      case "equals": return actual === expected;
      case "exists": return actual != null && actual !== "";
      case "in": return Array.isArray(expected) ? expected.includes(actual) : actual === expected;
      case "not_in": return Array.isArray(expected) ? !expected.includes(actual) : actual !== expected;
      case "greater_than": return (actual as number) > (expected as number);
      case "less_than": return (actual as number) < (expected as number);
      default: return false;
    }
  }
}

export class ComplianceEngine {
  api: string;
  private cache: Map<string, RegulationPack> = new Map();

  constructor(api_url: string = DEFAULT_API) {
    this.api = api_url.replace(/\/$/, "");
  }

  async load(regulation: string): Promise<RegulationPack> {
    if (this.cache.has(regulation)) return this.cache.get(regulation)!;
    const rules = await this.request("GET", `/v1/compliance/packs/${regulation}`);
    const pack = new RegulationPack(regulation, rules, this.api);
    this.cache.set(regulation, pack);
    return pack;
  }

  async listPacks(): Promise<Record<string, unknown>[]> {
    return this.request("GET", "/v1/compliance/packs");
  }

  async validate(regulation: string, action: Record<string, unknown>): Promise<ComplianceResult> {
    const pack = await this.load(regulation);
    return pack.validate(action);
  }

  async applicable(fleet_id: string): Promise<Record<string, unknown>[]> {
    return this.request("GET", `/v1/compliance/applicable?fleet_id=${fleet_id}`);
  }

  async evidence(regulation: string, fleet_id: string, period: string): Promise<Record<string, unknown>> {
    return this.request("POST", "/v1/compliance/evidence", { regulation, fleet_id, period });
  }

  private async request(method: string, path: string, data?: Record<string, unknown>): Promise<any> {
    const url = `${this.api}${path}`;
    const opts: RequestInit = { method, headers: { "Content-Type": "application/json" } };
    if (data) opts.body = JSON.stringify(data);
    const resp = await fetch(url, opts);
    return resp.json();
  }
}

export async function safeExecute(
  action: Record<string, unknown>,
  regulations: string[],
  api_url: string = DEFAULT_API
): Promise<boolean> {
  const engine = new ComplianceEngine(api_url);
  for (const reg of regulations) {
    const result = await engine.validate(reg, action);
    if (!result.passed) return false;
  }
  return true;
}
