/**
 * Agent Trust Score — Layer 3/5 (TypeScript)
 * Credit score for AI agents. Query, report, rate.
 * Reference implementation. CC BY 4.0.
 */

const DEFAULT_API = "https://workswithagents.dev";

export class TrustScoreClient {
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

  async get(agent_id: string): Promise<Record<string, unknown>> {
    return this.request("GET", `/v1/trust/${agent_id}`);
  }

  async report(
    agent_id: string, success_rate: number, pitfalls: number = 0, skills: number = 0
  ): Promise<Record<string, unknown>> {
    return this.request("POST", "/v1/trust/report", {
      agent_id, success_rate, pitfalls_contributed: pitfalls, skills_published: skills,
    });
  }

  async rate(from_agent: string, to_agent: string, rating: number): Promise<Record<string, unknown>> {
    return this.request("POST", "/v1/trust/rate", { from_agent, to_agent, rating });
  }

  async listTrusted(): Promise<Record<string, unknown>[]> {
    return this.request("GET", "/v1/trust?tier=trusted");
  }

  async history(agent_id: string): Promise<Record<string, unknown>[]> {
    return this.request("GET", `/v1/trust/${agent_id}/history`);
  }
}
