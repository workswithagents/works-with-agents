<!-- STATUS: Specification — API not yet deployed. Lastmod: 2026-05-05 -->

# Architecture Decisions

Master reference for cross-domain architectural decisions.

---

## Theme

- **Agent-facing:** Markdown — no CSS, no theme. AI agents consume text.
- **Human-facing:** Light default (Vilius' preference). Dark via `prefers-color-scheme`. Toggle in `localStorage`.
- **Implementation:** Every rendered page has light + dark CSS variables. `@media (prefers-color-scheme: dark)` override. JS toggle respects system preference on first visit.

---

## Internationalisation

- **Primary:** English.
- **URL structure:** `/{lang}/` prefix — `/ja/llms.txt`, `/de/llms-full.txt`.
- **Content negotiation:** `Accept-Language` header returns redirect or translated content.
- **Canonical URLs:** `<link rel="canonical">` to English primary. Prevents duplicate agent ingestion.
- **Priority:** Japanese (developer market), German (EU compliance), Welsh (UK public sector — Welsh Language Act 1993, Measure 2011).
- **Current:** English only. Architecture supports additions without restructuring.

---

## Agent Discovery

- **`llms.txt`** — Documentation index. llmstxt.org proposed standard.
- **`/v1/openapi.json`** — OpenAPI 3.1 API contract.
- **No custom discovery format.** Real standards only.

---

## API Versioning

- **URL-prefix:** `/v1/`, `/v2/`.
- **Deprecation:** 6 months notice via `Deprecation` + `Sunset` HTTP headers.
- **Breaking changes:** New version number. Backwards-compatible additions in same version.
- **Error format:** `{ "error": { "code": "...", "message": "...", "details": {} } }`

---

## Security

- **TLS:** 1.3 minimum. HTTP → HTTPS redirect.
- **CORS:** Restricted to known origins. Configurable per key.
- **Input validation:** JSON Schema on all inputs. Parameterized SQL (FactBase already uses `?` placeholders).
- **Rate limiting:** Per-key. `429 Too Many Requests` with `Retry-After`.
- **Audit:** All writes logged (key ID, timestamp, IP). Owner-readable.
- **Key rotation:** Self-service. Old key expires 24h after rotation.
- **Scopes:** read:facts, write:facts, read:skills, write:skills, heartbeat, pitfalls:read, pitfalls:write.

---

## GDPR & Data Privacy

- **Role:** Data processor for facts, pitfalls, heartbeats.
- **Location:** UK/EU data centres only. UK-only option.
- **Deletion:** Self-service API. Hard delete within 30 days.
- **Export:** Full JSON export via API.
- **DPA:** Available for Pro+ tiers.
- **Subprocessors:** Cloudflare (notified on change).

---

## Handoff Protocol — Standards Submission

### Primary venue: MCP SEP (Specification Enhancement Proposal)
MCP's SEP-2133 Extensions framework defines how to propose optional protocol extensions. Perfect fit for Handoff Protocol as an MCP extension.

**Process:**
1. GitHub issue on `modelcontextprotocol/modelcontextprotocol`
2. Request maintainer sponsorship
3. Draft SEP following template
4. Community review
5. Implementation

### Secondary venue: Google A2A (Agent-to-Agent Protocol)
A2A is purpose-built for agent communication. Handoff Protocol extends A2A's task model with compliance fields.

**Repo:** `github.com/a2aproject/a2a`

### Long-term: IETF Internet-Draft
If adoption warrants standards-track treatment.

---

## Content Freshness

- `<!-- lastmod: YYYY-MM-DD -->` HTML comment on every page.
- Agents check before re-ingesting.
- Simpler than `Last-Modified` headers.

---

## Cross-Domain Linking

- **API always at dev.** `.com` and `.co.uk` never duplicate API references.
- **Each domain self-describing.** Agents discover full ecosystem from any entry point.
- **`llms.txt` is the index** for each domain.

---

## Founders

**Vilius Vystartas** — Technical founder. Built Bastion. Power Platform Architect. Cardiff.
**Pelin Kayhan** — Co-owner. Business operations, compliance, client relationships. Non-technical.
