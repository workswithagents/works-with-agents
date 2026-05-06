# Works With Agents — Moats Execution Plan

## Status: May 2026

16 specifications published. 8 SDK modules. 4 certification badges. Compliance Proxy running.
2 GitHub proposals (Handoff Protocol: MCP SEP #2683, A2A #1817).

## Built Moats (16)

| # | Moat | Layer | Type | Status |
|---|------|------|------|--------|
| 1 | Agent OSI Model | Framework | Intellectual property | ✅ Published |
| 2 | Onboarding Protocol | L1/L3 | Ecosystem lock-in | ✅ Spec + SDK |
| 3 | Identity Protocol | L2/L3 | Security | ✅ Spec + SDK |
| 4 | Agent Capability Manifest | L3 | Discovery | ✅ Spec |
| 5 | Trust Score | L3/L5 | Network effect | ✅ Spec + SDK |
| 6 | Handoff Protocol | L4 | Standardization | ✅ Spec + MCP/A2A proposals |
| 7 | Coordination Protocol | L5 | Orchestration | ✅ Spec |
| 8 | IACP — Inter-Agent Communication | L5 | Platform | ✅ Spec + ref client |
| 9 | Deployment Manifest | Cross-layer | Standardization | ✅ Spec + SDK |
| 10 | Compliance-as-Code | L7 | Regulatory capture | ✅ Spec + SDK + proxy |
| 11 | Transaction Protocol | L7 | Governance | ✅ Spec |
| 12 | SLA Framework | L7 | Legal/Procurement | ✅ Spec + SDK |
| 13 | Agent Economics Protocol | L7 | Platform | ✅ Spec + ref client |
| 14 | Reputation Ledger | Cross-layer | Network effect | ✅ Spec + ref client |
| 15 | ASFS — Agent Skill Format Standard | Cross-framework | Ecosystem lock-in | ✅ Spec + converter |
| 16 | Local-First Agent Certification | Cross-layer | Trust | ✅ Badges + criteria |

## Strategic Concepts

| # | Concept | Status |
|---|---------|--------|
| C1 | Agent Fleet Insurance | ✅ Exploration doc |
| C2 | Independent Certification Body ("B Corp for Agents") | 🔜 Investigating |

## Services Built

| Service | Type | Status |
|---------|------|--------|
| Compliance Proxy | Real-time DTAC/GDPR validator | ✅ v0.1.0-beta |
| ASFS Converter | Hermes↔ASFS skill format | ✅ Working |
| Blueprint Registry | Verified LLM configs | ✅ Live on .io |
| Knowledge Platform | Facts, skills, pitfalls API | ✅ Live on .dev |

## SDK Coverage

| Language | Modules | Package |
|----------|---------|---------|
| Python | 8 (trust_score, deployment, sla, identity, compliance, onboarding, asfs_convert, compliance_proxy) | `pip install workswithagents` |
| TypeScript | 5 (TrustScore, DeploymentManifest, SLAMetrics, AgentIdentity, ComplianceEngine) + Onboarding, IACP client, Economics client, Reputation client | `npm install @workswithagents/agent-foundry` |

## Revenue Paths (All Coming Soon)

| Moat | Revenue Model |
|------|--------------|
| Compliance Proxy | Per-agent/month + regulation pack licensing |
| Certification (L3) | Annual certification fee per platform |
| Blueprint Registry | Enterprise on-prem license |
| Trust Score | Freemium → enterprise API |
| Fleet Insurance | Commission on premiums (MGA model) |
| Independent Cert Body | Accreditation fees + annual audits |

## Next Priority Actions

1. **Launch Independent Certification Body framework** (#8 — investigating)
2. Publish IACP to MCP/A2A as formal proposal
3. Build Reputation Ledger SQLite reference implementation
4. Add FCA regulation pack to Compliance Proxy
5. First paying engagement (break the "0 clients" barrier)
