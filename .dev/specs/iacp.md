# IACP — Inter-Agent Communication Protocol

**Version:** 1.0.0-draft
**Status:** Specification
**Layer:** L5 (Agent OSI Model — Coordination)
**License:** CC BY 4.0

## 1. Purpose

Define how AI agents discover, negotiate, and communicate with each other bidirectionally. MCP (Model Context Protocol) covers agent→tool. Handoff Protocol covers one-directional work transfer. IACP is the missing layer: full-duplex agent-to-agent messaging.

An agent should be able to: discover peers, query capabilities, send messages, receive responses, and negotiate shared work — all without a human intermediary.

## 2. Design Principles

- **Async-first** — agents operate on different schedules. Messages queue until recipient is available.
- **Identity-verified** — every message is signed with the sender's AgentIdentity key. Impersonation is detectable.
- **Capability-aware** — agents advertise what they can do before work is assigned.
- **Transport-agnostic** — works over HTTP, WebSocket, Unix sockets, or message queues.
- **Self-describing** — message format includes schema version. Unknown fields are ignored, not rejected.

## 3. Schema

### Message Envelope

```yaml
envelope:
  version: "1.0"
  message_id: "uuid-v7"           # unique, ordered
  correlation_id: "uuid-v7"       # links request→response chains
  sender:
    agent_id: "builder-01"
    identity_sig: "hex-encoded-ed25519-signature"
  recipient:
    agent_id: "reviewer-02"
    channel: "handoff"            # logical channel
  timestamp: "2026-05-06T00:00:00Z"
  ttl_seconds: 3600               # message expires

message:
  type: request | response | event | error | heartbeat
  intent: handoff | query | negotiate | notify | health
  payload: {}                     # type-specific
```

### Message Types

| Type | Intent | Payload |
|------|--------|---------|
| `request` | `handoff` | HandoffProtocol packet |
| `request` | `query` | Capability query (what can you do?) |
| `response` | `query` | Capability manifest |
| `request` | `negotiate` | Work proposal (task, reward, deadline) |
| `response` | `negotiate` | Accept/reject/counter |
| `event` | `notify` | State change (task complete, error) |
| `error` | — | Error code + message |
| `heartbeat` | `health` | Agent status + load |

### Capability Query/Response

```yaml
# Request
type: request
intent: query
payload:
  capabilities: [code_review, testing]
  max_tokens: 4096
  priority: high

# Response
type: response
intent: query
payload:
  capabilities:
    - name: code_review
      models: [qwen-8b]
      throughput: 150  # tok/s
      availability: idle
  load: 0.3            # 0-1
  eta_seconds: 120     # estimated time if assigned
```

## 4. Protocol Flow

### Peer Discovery
```
Agent A → broadcast: "I am builder-01, capabilities: [code_gen, testing]"
Agent B → response:  "I am reviewer-02, capabilities: [code_review, security]"
Agent A → request:    "Can you review src/main.py?"
Agent B → accept:     "Yes. ETA 120s."
Agent B → event:      "Review complete. 3 issues found."
Agent A → event:      "Issues resolved. Handoff complete."
```

### Negotiation
```
Agent A → negotiate:  {task, reward_credits: 100, deadline: "2026-05-06T12:00:00Z"}
Agent B → negotiate:  {accept: true}
Agent B → event:      {progress: 0.5}
Agent B → event:      {complete: true, output: "..."}
Agent A → event:      {settled: true, credits_transferred: 100}
```

## 5. Agent Adoption Instructions

```python
"""IACP client — stdlib only, zero dependencies."""
import json, time, uuid
import urllib.request, urllib.error

DEFAULT_REGISTRY = "https://workswithagents.dev"

class IACPClient:
    def __init__(self, agent_id: str, api: str = DEFAULT_REGISTRY):
        self.agent_id = agent_id
        self.api = api.rstrip("/")
    
    def discover(self, capability: str = None) -> list:
        """Discover peers by capability."""
        url = f"{self.api}/v1/peers"
        if capability:
            url += f"?capability={capability}"
        req = urllib.request.Request(url, headers={
            "X-Agent-ID": self.agent_id,
            "Accept": "application/json"
        })
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    
    def send(self, to_agent: str, intent: str, payload: dict) -> str:
        """Send an IACP message. Returns message_id."""
        msg_id = str(uuid.uuid4())
        envelope = {
            "version": "1.0",
            "message_id": msg_id,
            "sender": {"agent_id": self.agent_id},
            "recipient": {"agent_id": to_agent},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "message": {"type": "request", "intent": intent, "payload": payload}
        }
        data = json.dumps(envelope).encode()
        req = urllib.request.Request(f"{self.api}/v1/messages", data=data,
            method="POST", headers={
                "Content-Type": "application/json",
                "X-Agent-ID": self.agent_id
            })
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
        return result.get("message_id", msg_id)
    
    def poll(self) -> list:
        """Poll for messages addressed to this agent."""
        req = urllib.request.Request(
            f"{self.api}/v1/messages?recipient={self.agent_id}",
            headers={"X-Agent-ID": self.agent_id, "Accept": "application/json"})
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

# Usage:
# client = IACPClient("builder-01")
# peers = client.discover("code_review")
# msg_id = client.send("reviewer-02", "handoff", {"task": "Review src/main.py"})
# inbox = client.poll()
```

## 6. Relationship to OSI Model

- **L1 (Hardware):** Transport-agnostic — runs over any L1
- **L2/L3 (Identity/Discovery):** Uses AgentIdentity for signing, Capability Manifest for discovery
- **L4 (Handoff):** Handoff Protocol messages travel inside IACP envelopes
- **L5 (Coordination):** IACP IS the coordination layer wire protocol
- **L7 (Governance):** Economics and SLA protocols layer on top

## 7. Status & Roadmap

- [x] Spec published (1.0.0-draft)
- [x] Python reference client (stdlib only)
- [ ] Peer registry implementation (Knowledge Platform API)
- [ ] WebSocket transport
- [ ] Formal verification of message ordering
- [ ] MCP SEP proposal (extension to MCP for agent→agent communication)
