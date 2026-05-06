/**
 * Agent Identity Protocol — Layer 2/3 (TypeScript)
 * Cryptographic agent identity with Ed25519 keypairs.
 * Reference implementation. CC BY 4.0.
 */

const DEFAULT_API = "https://workswithagents.dev";

export class AgentIdentity {
  agent_id: string;
  api: string;
  private _privateKey: Uint8Array | null = null;
  private _publicKey: Uint8Array | null = null;

  constructor(agent_id: string, api_url: string = DEFAULT_API) {
    this.agent_id = agent_id;
    this.api = api_url.replace(/\/$/, "");
  }

  async generate(): Promise<{ agent_id: string; public_key: string }> {
    const subtle = crypto.subtle;
    const keypair = await subtle.generateKey(
      { name: "Ed25519" } as any,
      true,
      ["sign", "verify"]
    ) as CryptoKeyPair;
    const pubRaw = await subtle.exportKey("raw", keypair.publicKey);
    const privRaw = await subtle.exportKey("pkcs8", keypair.privateKey);
    this._publicKey = new Uint8Array(pubRaw);
    this._privateKey = new Uint8Array(privRaw);
    return { agent_id: this.agent_id, public_key: this.hex(this._publicKey) };
  }

  async register(owner_name?: string, owner_email?: string): Promise<Record<string, unknown>> {
    if (!this._publicKey) await this.generate();
    const payload: Record<string, unknown> = {
      agent_id: this.agent_id,
      public_key: this.hex(this._publicKey!),
    };
    if (owner_name) payload.owner_name = owner_name;
    if (owner_email) payload.owner_email = owner_email;
    return this.request("POST", "/v1/identity/register", payload);
  }

  async sign(payload: Record<string, unknown>): Promise<string> {
    if (!this._privateKey) await this.generate();
    const message = JSON.stringify({
      agent_id: this.agent_id,
      timestamp: Math.floor(Date.now() / 1000),
      payload,
    });
    const enc = new TextEncoder().encode(message);
    const key = await crypto.subtle.importKey(
      "pkcs8", this._privateKey!,
      { name: "Ed25519" } as any, false, ["sign"]
    );
    const sig = await crypto.subtle.sign("Ed25519" as any, key, enc);
    return this.hex(new Uint8Array(sig));
  }

  static async verify(
    agent_id: string, message: Record<string, unknown>,
    signature: string, api_url: string = DEFAULT_API
  ): Promise<boolean> {
    const resp = await fetch(`${api_url}/v1/identity/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ agent_id, message, signature }),
    });
    const data = await resp.json();
    return data.valid === true;
  }

  async rotate(): Promise<Record<string, unknown>> {
    const oldPub = this.hex(this._publicKey!);
    await this.generate();
    return this.request("POST", `/v1/identity/${this.agent_id}/rotate`, {
      new_public_key: this.hex(this._publicKey!),
      old_public_key: oldPub,
    });
  }

  async revoke(reason: string = "manual"): Promise<Record<string, unknown>> {
    return this.request("POST", `/v1/identity/${this.agent_id}/revoke`, { reason });
  }

  private hex(buf: Uint8Array): string {
    return Array.from(buf).map(b => b.toString(16).padStart(2, "0")).join("");
  }

  private async request(method: string, path: string, data?: Record<string, unknown>): Promise<any> {
    const url = `${this.api}${path}`;
    const opts: RequestInit = { method, headers: { "Content-Type": "application/json" } };
    if (data) opts.body = JSON.stringify(data);
    const resp = await fetch(url, opts);
    return resp.json();
  }
}
