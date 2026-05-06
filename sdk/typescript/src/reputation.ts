/**
 * Agent Reputation Ledger client (TypeScript)
 * Verifiable cross-org reputation claims.
 * Reference implementation. CC BY 4.0.
 */

const DEFAULT_API = "https://workswithagents.dev";

export class ReputationClient {
  agent_id: string;
  api: string;

  constructor(agent_id: string, api: string = DEFAULT_API) {
    this.agent_id = agent_id;
    this.api = api.replace(/\/$/, "");
  }

  private async request(method: string, path: string, data?: Record<string, unknown>): Promise<any> {
    const url = `${this.api}${path}`;
    const opts: RequestInit = {
      method,
      headers: { "Content-Type": "application/json", "X-Agent-ID": this.agent_id },
    };
    if (data) opts.body = JSON.stringify(data);
    const resp = await fetch(url, opts);
    return resp.json();
  }

  async query(target_agent: string, scope: string = "public"): Promise<Record<string, unknown>> {
    let url = `/v1/reputation/agents/${target_agent}`;
    if (scope) url += `?scope=${encodeURIComponent(scope)}`;
    return this.request("GET", url);
  }

  async submitClaim(
    target: string, event_type: string, outcome: string, metrics: Record<string, unknown>,
    signature: string = "", pubkey: string = ""
  ): Promise<Record<string, unknown>> {
    const claim: Record<string, unknown> = {
      claim: {
        subject: target,
        verifier: this.agent_id,
        event: { type: event_type, outcome, metrics },
        scope: "public",
      },
    };
    if (signature) claim.signature = signature;
    if (pubkey) claim.public_key = pubkey;
    return this.request("POST", "/v1/reputation/claims", claim);
  }

  async history(agent_id?: string, limit: number = 20): Promise<Record<string, unknown>[]> {
    const target = agent_id || this.agent_id;
    return this.request("GET", `/v1/reputation/agents/${target}/claims?limit=${limit}`);
  }

  async endorse(target: string, statement: string): Promise<Record<string, unknown>> {
    return this.request("POST", `/v1/reputation/agents/${target}/endorse`, {
      verifier: this.agent_id, statement,
    });
  }

  async summary(agent_id?: string): Promise<Record<string, unknown>> {
    const target = agent_id || this.agent_id;
    const profile = await this.query(target);
    return (profile as any).profile?.summary || {};
  }
}
