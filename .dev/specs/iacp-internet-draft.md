---
title: "Inter-Agent Communication Protocol (IACP)"
abbrev: "IACP"
category: info
docname: draft-vystartas-iacp-00
date: 2026-05-06
author:
  - name: Vilius Vystartas
    org: Works With Agents
    email: hello@workswithagents.com
  - name: Pelin Kayhan
    org: Works With Agents
    email: pelin@workswithagents.com
stand_alone: yes
pi: [toc, sortrefs, symrefs]
---

.# Abstract

This document defines the Inter-Agent Communication Protocol (IACP), a
transport-agnostic, identity-verified, async-first messaging protocol for
AI agents. IACP enables agents to discover peers, query capabilities, send
messages, receive responses, and negotiate shared work without human
intermediaries. The protocol is designed to operate as a companion to the
Message Context Protocol (MCP), filling the agent-to-agent communication
gap that MCP's agent-to-tool orientation leaves open.

.# Status of This Memo

This Internet-Draft is submitted in full conformance with the provisions of
BCP 78 and BCP 79.

Internet-Drafts are working documents of the Internet Engineering Task Force
(IETF). Note that other groups may also distribute working documents as
Internet-Drafts. The list of current Internet-Drafts is at
https://datatracker.ietf.org/drafts/current/.

Internet-Drafts are draft documents valid for a maximum of six months and
may be updated, replaced, or obsoleted by other documents at any time. It is
inappropriate to use Internet-Drafts as reference material or to cite them
other than as "work in progress."

This Internet-Draft will expire on November 6, 2026.

.# Copyright Notice

Copyright (c) 2026 IETF Trust and the persons identified as the document
authors. All rights reserved.

This document is subject to BCP 78 and the IETF Trust's Legal Provisions
Relating to IETF Documents (https://trustee.ietf.org/license-info) in effect
on the date of publication of this document. Please review these documents
carefully, as they describe your rights and restrictions with respect to
this document.

The reference implementation and specification maintained at
https://workswithagents.dev/specs/iacp.md is licensed under CC BY 4.0.

--- back

.# Introduction

AI agents are being deployed in production across enterprise, government,
and regulated industry environments. They operate autonomously: making
decisions, executing tasks, and communicating outcomes. Yet there is no
standard protocol for how agents communicate with each other.

The Model Context Protocol (MCP) {{?MCP=DOI.10.2024.ANTHROPIC.MCP}} defines
agent-to-tool interaction — a client-server model where an agent calls
external tools. Handoff protocols define one-directional work transfer
between agents. Neither addresses full-duplex agent-to-agent messaging:
discovery, capability negotiation, bidirectional communication, shared task
coordination, and economic exchange.

IACP fills this gap. It is a peer-to-peer protocol where every agent is both
client and server. Agents discover each other, advertise capabilities,
exchange signed messages, negotiate work, and coordinate tasks — without
human intermediaries.

.#. Requirements Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and
"OPTIONAL" in this document are to be interpreted as described in BCP 14
{{!RFC2119}} {{!RFC8174}} when, and only when, they appear in all capitals,
as shown here.

.# Design Principles

IACP is built on five design principles that reflect the operational
characteristics of autonomous AI agents:

**Async-first:** Agents operate on different schedules — one may be
processing a long-running task while another sends a message. Messages MUST
be queued until the recipient is available. No synchronous requirement is
assumed.

**Identity-verified:** Every message MUST be signed with the sender's
cryptographic identity key. Recipients MUST verify signatures before
processing. Impersonation is detectable at the protocol level.

**Capability-aware:** Agents MUST advertise their capabilities before work
is assigned. A Capability Manifest (see Section 4) declares tool sets,
model capabilities, rate limits, and safety constraints.

**Transport-agnostic:** The protocol operates over HTTP, WebSocket, Unix
sockets, or message queues. Transport-specific binding documents define
how the message envelope is carried over each substrate.

**Self-describing:** Message format includes a schema version field.
Recipients MUST ignore unknown fields rather than rejecting the message.
Backward-compatible extensions are possible without protocol version
negotiation.

.#. Why Not Extend MCP?

MCP defines a client-server model (agent → tool) with a specific
initialization sequence, capability negotiation, and JSON-RPC message
format. Extending MCP to support agent-to-agent communication would require
fundamental changes to its model:

- MCP is client-server; agent communication is peer-to-peer.
- MCP tools are stateless; agents maintain conversational state across
  multiple message exchanges.
- MCP capability negotiation is tool-focused; agents need to declare domain
  expertise, language model capabilities, and trust scores.
- MCP does not define message queuing, TTL, or async delivery semantics.

IACP is designed as a companion protocol — agents MAY use MCP to call
tools AND IACP to communicate with other agents.

.# Message Envelope

All IACP messages are wrapped in an envelope that carries routing,
identity, and temporal metadata. The envelope is independent of the
message payload.

.#. YAML Representation

The canonical representation of the message envelope is YAML. JSON is
accepted as an equivalent wire format when content negotiation preferences
JSON over YAML. Binary encodings (e.g., CBOR) MAY be defined in transport
binding documents.

```yaml
envelope:
  version: "1.0"
  message_id: "<UUIDv7>"        # unique, time-ordered
  correlation_id: "<UUIDv7>"    # links request→response chains
  sender:
    agent_id: "<string>"
    identity_sig: "<hex-encoded-Ed25519-signature>"
  recipient:
    agent_id: "<string>"
    channel: "<string>"         # logical channel
  timestamp: "<RFC3339>"
  ttl_seconds: 3600
message:
  type: request | response | event | error | heartbeat
  intent: handoff | query | negotiate | notify | health
  payload: {}                   # type-dependent, defined in Section 4
```

.#. Field Definitions

**version:** Protocol version string in MAJOR.MINOR format. Version 1.0
MUST be supported by all implementations. Receivers MUST reject envelopes
with an unsupported MAJOR version and return an error message with the
list of supported versions.

**message_id:** UUIDv7 per {{?RFC9562}}. Provides unique identification and
time-based ordering without requiring clock synchronization. UUIDv7 is
chosen over UUIDv4 because the embedded timestamp enables ordered replay
and deduplication without external sequence numbers.

**correlation_id:** Links messages in a conversation chain. When agent A
sends a request to agent B, both the request and the response share the
same correlation_id. Implementations MUST propagate correlation_id through
multi-hop relay chains.

**sender.agent_id:** Unique agent identifier. Format is
`<namespace>:<host>:<name>` as defined in the Agent Identity Protocol
{{?AIP=I-D.vystartas-agent-identity}}. Example: `on-prem:cardiff-01:builder`.

**sender.identity_sig:** Ed25519 signature over the SHA-256 hash of the
canonical serialization of the envelope (excluding the signature field
itself). Recipients verify this signature against the sender's public key,
obtained via the Agent Identity Protocol discovery mechanism.

**recipient.agent_id:** Target agent identifier. Same format as
sender.agent_id. Wildcards (`*` for namespace/host) are permitted for
broadcast discovery messages.

**recipient.channel:** Logical communication channel. Channels partition
message streams by purpose. Standard channels: `handoff` (task transfer),
`query` (capability discovery), `coordination` (multi-agent planning),
`notification` (state change broadcasts), `health` (heartbeats).
Implementations MAY define custom channels prefixed with `x-`.

**timestamp:** ISO 8601 / RFC 3339 timestamp in UTC. Used for message
ordering, deduplication, and TTL calculation. Sender clock drift of up to
30 seconds SHOULD be tolerated.

**ttl_seconds:** Time-to-live in seconds from timestamp. After expiry, the
message MUST NOT be processed. Intermediaries MUST decrement a
recommended TTL proportionally to processing delay.

.#. Message Types

.#. request

A request message expects a response. The sender includes an intent that
describes the purpose and a payload specific to that intent:

| Intent | Payload | Purpose |
|--------|---------|---------|
| `handoff` | HandoffProtocol packet | Transfer a task to the recipient |
| `query` | Capability filters | Ask what the recipient can do |
| `negotiate` | Work proposal | Propose a task with terms |

**Error handling:** If a request cannot be fulfilled, the recipient MUST
respond with an `error` message (Section 3.6) within the TTL window. If no
response arrives within TTL, the sender SHOULD treat it as a timeout error.

.#. response

A response message is sent in reply to a request. The `correlation_id` MUST
match the original request's `message_id`. The payload mirrors the request's
intent:

| Intent | Payload |
|--------|---------|
| `handoff` | HandoffProtocol result packet |
| `query` | Capability manifest |
| `negotiate` | Accept / reject / counter-offer |

Responses MUST include a `status` field in the payload:
- `accepted` — request fulfilled successfully
- `rejected` — request declined (reason in `detail` field)
- `pending` — request queued, will respond later
- `counter` — alternative proposal follows

.#. event

Event messages are fire-and-forget — no response is expected. Used for
state change notifications, task progress updates, and system alerts.

Payload includes:
- `event_type`: machine-readable event identifier
- `detail`: human-readable description
- `severity`: `info` | `warning` | `critical`

Events MAY trigger automated responses (e.g., a `critical` severity
event in the `health` channel may trigger failover), but this is
implementation-defined.

.#. error

Error messages report failures. They MAY be sent in response to any
message type.

Payload:
- `code`: machine-readable error code (see Section 3.6.1)
- `message`: human-readable error description
- `detail`: optional structured error data
- `retryable`: boolean indicating whether the sender MAY retry

**Standard error codes:**

| Code | Description |
|------|-------------|
| `VERSION_UNSUPPORTED` | Envelope version not supported |
| `IDENTITY_INVALID` | Signature verification failed |
| `CAPABILITY_MISMATCH` | Agent cannot fulfill requested intent |
| `RATE_LIMITED` | Recipient is overloaded |
| `TIMEOUT` | Request expired before processing |
| `CHANNEL_UNKNOWN` | Recipient does not support the specified channel |
| `PAYLOAD_INVALID` | Message payload failed schema validation |
| `INTERNAL_ERROR` | Unspecified recipient error |

.#. heartbeat

Heartbeat messages are lightweight liveness signals. Sent periodically
(30–300 second intervals, configurable) to peers or fleet coordinators.

Payload:
- `status`: `alive` | `busy` | `draining` | `offline`
- `load`: 0.0–1.0 representing current capacity utilisation
- `active_tasks`: count of currently executing tasks
- `version`: agent software version

Fleet coordinators track heartbeats to detect crashed or stuck agents.
An agent that sends no heartbeat for a configurable timeout (default
600 seconds) SHOULD be considered `stuck` and its queued work MAY be
reassigned.

.#. Capability Discovery

Before task assignment, agents need to know what other agents can do.
IACP defines a capability discovery flow.

.#. Capability Query

A `request` with intent `query` carries a capability filter:

```yaml
payload:
  required:
    tools: ["terminal", "file", "web"]   # MUST have these
    models: ["llama3"]                    # MUST support this model
  preferred:
    domains: ["compliance", "security"]   # NICE to have
  constraints:
    max_latency_ms: 5000                  # response latency budget
    locality: "on-prem"                   # deployment preference
```

.#. Capability Manifest

A `response` to a capability query returns the agent's capability manifest:

```yaml
payload:
  status: accepted
  manifest:
    agent_id: "on-prem:cardiff-01:builder"
    tools: ["terminal", "file", "web", "delegation", "browser"]
    models: ["Llama-3.3-70B-OQ4", "Qwen2.5-8B-OQ4"]
    max_context_tokens: 131072
    domains: ["code-review", "compliance", "security"]
    rate_limit:
      requests_per_minute: 60
      tokens_per_minute: 100000
    trust_score: 0.92
    deployment: "on-prem"
    version: "1.2.0"
    uptime_seconds: 172800
```

The Capability Manifest is defined in full by the companion
Capability Manifest specification {{?CM=I-D.vystartas-capability-manifest}}.

.#. Transport Bindings

.#. HTTP/1.1 Binding

IACP over HTTP uses POST requests to a well-known endpoint:

```
POST /.well-known/iacp/v1/message
Content-Type: application/x-yaml
Authorization: Bearer <agent_identity_token>

<YAML-encoded envelope>
```

Responses use standard HTTP status codes:
- `202 Accepted` — message queued for async processing
- `200 OK` with body — synchronous response
- `429 Too Many Requests` — rate limited; Retry-After header
- `401 Unauthorized` — identity verification failed

The `.well-known` URI is per {{!RFC8615}}.

.#. WebSocket Binding

For persistent connections, agents MAY negotiate a WebSocket upgrade:

```
GET /.well-known/iacp/v1/connect
Upgrade: websocket
```

The WebSocket channel carries bidirectional message envelopes as text
frames. Pings serve as heartbeats.

.#. Message Queue Binding

For high-throughput deployments, agents MAY use a message queue (AMQP,
NATS, Kafka) as transport. Each agent subscribes to a topic matching its
agent_id, and publishes to topics matching recipient agent_ids.

.#. Security Considerations

**Identity Spoofing:** Without cryptographic identity verification, any
agent could impersonate another. IACP requires Ed25519 signatures on every
message envelope. Recipients MUST reject unsigned messages or messages
with invalid signatures.

**Replay Attacks:** An attacker capturing signed messages could replay them
to cause duplicate work. UUIDv7 message_ids provide temporal uniqueness.
Recipients SHOULD maintain a sliding window of processed message_ids and
reject duplicates within the TTL window.

**Denial of Service:** An agent flooding messages could overwhelm recipients.
Rate limiting is RECOMMENDED at both the transport and application layers.
The rate_limit field in capability manifests enables senders to self-throttle.

**Privacy of Message Content:** IACP does not encrypt message payloads at
the protocol layer. If payload confidentiality is required, transport-layer
encryption (TLS, WireGuard) MUST be used. End-to-end payload encryption MAY
be added in a future extension.

**Metadata Leakage:** Envelope fields (agent_ids, channels, timestamps)
reveal communication patterns even if payloads are encrypted. Deployments in
privacy-sensitive contexts SHOULD evaluate metadata exposure and consider
onion routing or batch delivery where appropriate.

.#. IANA Considerations

This document requests the registration of the `.well-known/iacp` URI
suffix per {{!RFC8615}}.

This document requests the creation of an "IACP Channel Names" registry
with the following initial entries:

| Channel | Description |
|---------|-------------|
| `handoff` | Task transfer between agents |
| `query` | Capability discovery |
| `coordination` | Multi-agent task planning |
| `notification` | State change broadcasts |
| `health` | Heartbeat and status |

New channel names are registered on a First Come First Served basis
{{!RFC8126}}.

This document requests the creation of an "IACP Error Codes" registry
with the initial entries listed in Section 3.6.1.

.#. Implementation Status

A reference implementation of IACP is maintained at
https://workswithagents.dev/specs/iacp.md and is available as a Python
library via `pip install workswithagents`.

The protocol has been tested in a multi-agent deployment with the following
workload:

- 3 agent types (builder, reviewer, coordinator)
- 150+ messages in a 3-hour window
- Handoff, query, negotiate, heartbeat message types
- HTTP transport with Ed25519 identity signatures
- Full audit trail generation for each message exchange

.#. Acknowledgements

The authors thank the agent infrastructure community for early feedback on
the protocol design, particularly the separation of concerns from MCP and
the choice of UUIDv7 for message ordering.

--- back

.#. Change Log

RFC Editor: Remove this section before publication.

- **draft-vystartas-iacp-00** (2026-05-06): Initial version.
