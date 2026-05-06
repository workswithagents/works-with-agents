/**
 * IACP — Inter-Agent Communication Protocol client (TypeScript)
 * Zero dependencies. Copy-pasteable.
 * Reference implementation. CC BY 4.0.
 */

const DEFAULT_API = "https://workswithagents.dev";

export interface IACPMessage {
  version: string;
  message_id: string;
  sender: { agent_id: string };
  recipient: { agent_id: string };
  timestamp: string;
  message: { type: string; intent: string; payload: Record<string, unknown> };
}

export class IACPClient {
  agent_id: string;
  api: string;

  constructor(agent_id: string, api: string = DEFAULT_API) {
    this.agent_id = agent_id;
    this.api = api.replace(/\/$/, "");
  }

  async discover(capability?: string): Promise<Record<string, unknown>[]> {
    let url = `${this.api}/v1/peers`;
    if (capability) url += `?capability=${encodeURIComponent(capability)}`;
    const resp = await fetch(url, {
      headers: { "X-Agent-ID": this.agent_id, "Accept": "application/json" },
    });
    return resp.json();
  }

  async send(to_agent: string, intent: string, payload: Record<string, unknown>): Promise<string> {
    const msg_id = crypto.randomUUID();
    const envelope: IACPMessage = {
      version: "1.0",
      message_id: msg_id,
      sender: { agent_id: this.agent_id },
      recipient: { agent_id: to_agent },
      timestamp: new Date().toISOString(),
      message: { type: "request", intent, payload },
    };
    const resp = await fetch(`${this.api}/v1/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Agent-ID": this.agent_id },
      body: JSON.stringify(envelope),
    });
    const result = await resp.json();
    return result.message_id || msg_id;
  }

  async poll(): Promise<Record<string, unknown>[]> {
    const resp = await fetch(`${this.api}/v1/messages?recipient=${encodeURIComponent(this.agent_id)}`, {
      headers: { "X-Agent-ID": this.agent_id, "Accept": "application/json" },
    });
    return resp.json();
  }

  async heartbeat(status: string = "idle", load: number = 0.0): Promise<Record<string, unknown>> {
    return JSON.parse(await this.send("registry", "health", { status, load }));
  }
}
