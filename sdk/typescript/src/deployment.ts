/**
 * Agent Deployment Manifest — Cross-Layer (TypeScript)
 * Deploy agent fleets from YAML/JSON manifests.
 * Reference implementation. CC BY 4.0.
 */

const DEFAULT_API = "https://workswithagents.dev";

export interface DeploymentAgent {
  id: string;
  type?: string;
  capabilities: string[];
  [key: string]: unknown;
}

export interface DeploymentFleet {
  name: string;
  agents: DeploymentAgent[];
  [key: string]: unknown;
}

export interface DeploymentManifestData {
  manifest_version: string;
  fleet: DeploymentFleet;
  [key: string]: unknown;
}

export class DeploymentManifest {
  manifest: DeploymentManifestData;
  api: string;
  fleet_id: string | null = null;

  constructor(manifest: DeploymentManifestData, api_url: string = DEFAULT_API) {
    this.manifest = manifest;
    this.api = api_url.replace(/\/$/, "");
  }

  static fromObject(obj: Record<string, unknown>, api_url: string = DEFAULT_API): DeploymentManifest {
    return new DeploymentManifest(obj as DeploymentManifestData, api_url);
  }

  static minimal(name: string, agent_id: string, capabilities: string[], api_url: string = DEFAULT_API): DeploymentManifest {
    return new DeploymentManifest({
      manifest_version: "1.0.0-draft",
      fleet: { name, agents: [{ id: agent_id, type: "hermes", capabilities }] }
    }, api_url);
  }

  validate(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    const mf = this.manifest;
    if (!mf.manifest_version) errors.push("Missing manifest_version");
    if (!mf.fleet) { errors.push("Missing fleet section"); return { valid: false, errors }; }
    if (!mf.fleet.name) errors.push("Missing fleet.name");
    if (!mf.fleet.agents?.length) errors.push("Missing fleet.agents (at least one required)");
    mf.fleet.agents?.forEach((agent, i) => {
      if (!agent.id) errors.push(`Agent[${i}]: missing id`);
      if (!agent.capabilities) errors.push(`Agent[${i}]: missing capabilities`);
    });
    return { valid: errors.length === 0, errors };
  }

  async deploy(): Promise<Record<string, unknown>> {
    const validation = this.validate();
    if (!validation.valid) return { status: "error", errors: validation.errors };
    const result = await this.request("POST", "/v1/fleets/deploy", this.manifest as unknown as Record<string, unknown>);
    if (result.fleet_id) this.fleet_id = result.fleet_id as string;
    return result;
  }

  async status(): Promise<Record<string, unknown>> {
    if (!this.fleet_id) return { error: "Fleet not deployed. Call deploy() first." };
    return this.request("GET", `/v1/fleets/${this.fleet_id}/status`);
  }

  async scale(agent_type: string, count: number): Promise<Record<string, unknown>> {
    if (!this.fleet_id) return { error: "Fleet not deployed." };
    return this.request("POST", `/v1/fleets/${this.fleet_id}/scale`, { agent_type, count });
  }

  private async request(method: string, path: string, data?: Record<string, unknown>): Promise<any> {
    const url = `${this.api}${path}`;
    const opts: RequestInit = { method, headers: { "Content-Type": "application/json" } };
    if (data) opts.body = JSON.stringify(data);
    const resp = await fetch(url, opts);
    return resp.json();
  }
}
