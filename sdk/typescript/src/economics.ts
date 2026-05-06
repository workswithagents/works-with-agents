/**
 * Agent Economics Protocol client (TypeScript)
 * Compute credits, bounties, settlement.
 * Reference implementation. CC BY 4.0.
 */

const DEFAULT_API = "https://workswithagents.dev";

export class EconomicsClient {
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

  async balance(): Promise<Record<string, unknown>> {
    return this.request("GET", `/v1/economics/balance/${this.agent_id}`);
  }

  async postBounty(
    task: string, dod: string[], reward: number, deadline: string, tier: string = "trusted"
  ): Promise<Record<string, unknown>> {
    return this.request("POST", "/v1/economics/bounties", {
      poster: this.agent_id,
      task: { goal: task, definition_of_done: dod, deadline },
      reward_credits: reward,
      required_tier: tier,
    });
  }

  async claimBounty(bounty_id: string): Promise<Record<string, unknown>> {
    return this.request("POST", `/v1/economics/bounties/${bounty_id}/claim`, { agent_id: this.agent_id });
  }

  async listBounties(status: string = "open"): Promise<Record<string, unknown>[]> {
    return this.request("GET", `/v1/economics/bounties?status=${status}`);
  }

  async settle(
    bounty_id: string, outcome: string, metrics: Record<string, unknown> = {}
  ): Promise<Record<string, unknown>> {
    return this.request("POST", `/v1/economics/bounties/${bounty_id}/settle`, {
      worker: this.agent_id, outcome, metrics,
    });
  }
}
