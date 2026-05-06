/**
 * Agent Onboarding Protocol — Layer 1/3 (TypeScript)
 * Productize the creation of new specialist AI agents.
 * Reference implementation. CC BY 4.0.
 */

const DEFAULT_API = "https://workswithagents.dev";

export interface OnboardingInterview {
  name: string;
  purpose: string;
  capabilities: string[];
  skills?: string[];
  tools?: string[];
  fleet?: string;
  constraints?: string[];
  benchmarks?: Record<string, unknown>[];
}

export class OnboardingClient {
  api: string;

  constructor(api_url: string = DEFAULT_API) {
    this.api = api_url.replace(/\/$/, "");
  }

  private async request(method: string, path: string, data?: Record<string, unknown>): Promise<any> {
    const url = `${this.api}${path}`;
    const opts: RequestInit = { method, headers: { "Content-Type": "application/json" } };
    if (data) opts.body = JSON.stringify(data);
    const resp = await fetch(url, opts);
    return resp.json();
  }

  async interview(
    name: string, purpose: string, capabilities: string[],
    opts?: { skills?: string[]; tools?: string[]; fleet?: string; constraints?: string[]; benchmarks?: Record<string, unknown>[] }
  ): Promise<Record<string, unknown>> {
    const payload: Record<string, unknown> = { agent_name: name, purpose, capabilities };
    if (opts?.skills) payload.skills = opts.skills;
    if (opts?.tools) payload.tools = opts.tools;
    if (opts?.fleet) payload.fleet = opts.fleet;
    if (opts?.constraints) payload.constraints = opts.constraints;
    if (opts?.benchmarks) payload.benchmarks = opts.benchmarks;
    return this.request("POST", "/v1/onboard/interview", payload);
  }

  async generate(interview_id: string): Promise<Record<string, unknown>> {
    return this.request("POST", `/v1/onboard/${interview_id}/generate`);
  }

  async calibrate(interview_id: string): Promise<Record<string, unknown>> {
    return this.request("POST", `/v1/onboard/${interview_id}/calibrate`);
  }

  async benchmark(interview_id: string): Promise<Record<string, unknown>> {
    return this.request("POST", `/v1/onboard/${interview_id}/benchmark`);
  }

  async register(interview_id: string): Promise<Record<string, unknown>> {
    return this.request("POST", `/v1/onboard/${interview_id}/register`);
  }

  async fullOnboard(
    name: string, purpose: string, capabilities: string[],
    opts?: Record<string, unknown>
  ): Promise<Record<string, unknown>> {
    const result = await this.interview(name, purpose, capabilities, opts as any);
    const iid = result.interview_id as string;
    if (!iid) return { error: "Interview failed", details: result };

    const gen = await this.generate(iid);
    if (gen.error) return { error: "Generation failed", details: gen };

    const cal = await this.calibrate(iid);
    if (!cal.passed) return { error: "Calibration failed", results: cal, next: "Review calibration failures and retry" };

    return this.register(iid);
  }
}
