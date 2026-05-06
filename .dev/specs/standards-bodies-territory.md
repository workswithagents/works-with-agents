# Standards Body Territory Map — AI Agent Standards

**Version:** 1.0.0
**Status:** Strategic Analysis
**Date:** 2026-05-06

## Executive Summary

**No standards body has defined standards for AI agents yet.** ISO, IEEE, NIST, CEN-CENELEC, BSI, and IETF all have AI work — but none address agent-to-agent protocols, agent identity, agent trust, or agent compliance verification. This is a wide-open territory.

Works With Agents has 16 specifications ready for submission to 6 bodies across 3 jurisdictions.

## The Landscape

### ISO/IEC JTC 1/SC 42 — Artificial Intelligence
**Jurisdiction:** International
**What they have:** 18+ published standards (42001 AI management, 5259 data quality, 5338 lifecycle, 5339 applications, 5392 engineering)
**What's MISSING:** Agent interoperability. Agent identity. Agent trust scores. Agent-to-agent protocols.
**Our opportunity:** Propose a **New Work Item Proposal (NWIP)** for "AI Agent Interoperability Framework" — covers Handoff Protocol + IACP + Trust Score.
**Status:** Open for proposals. UK national body (BSI) can submit on our behalf.

### CEN-CENELEC JTC 21 — AI (EU)
**Jurisdiction:** European Union
**What they have:** Developing harmonized standards for EU AI Act compliance. Working groups on: legal conformity, ethics, security, risk management.
**What's MISSING:** Compliance verification standards for autonomous/AI systems. Agent-specific conformity assessment.
**Our opportunity:** Propose **CWA (CEN Workshop Agreement)** for "Compliance-as-Code for Autonomous AI Systems." Directly supports EU AI Act Article 40 (harmonized standards).
**Status:** CWA process is fast (12-18 months vs 3-5 years for EN). Open to any organization.

### IEEE — Autonomous Intelligent Systems
**Jurisdiction:** USA / International
**What they have:** IEEE 7000-2022 (ethical design), P7001 (transparency), P7007 (ontological standard for ethically driven robotics)
**What's MISSING:** Agent skill format standard. Agent capability description standard.
**Our opportunity:** Propose **IEEE P7014** — "Standard for Agent Skill Format Interchange (ASFS)." ASFS is ready.
**Status:** IEEE standards process open. Requires working group formation (6-12 months).

### IETF — Internet Engineering Task Force
**Jurisdiction:** International (Internet standards)
**What they have:** No AI agent-specific RFCs. MCP (Model Context Protocol) is NOT an IETF standard.
**What's MISSING:** Agent-to-agent communication protocol over the internet.
**Our opportunity:** Submit **Internet-Draft** for IACP (Inter-Agent Communication Protocol). Position as an application-layer protocol. Already has a reference implementation.
**Status:** Internet-Drafts accepted from anyone. RFC process takes 12-24 months.

### NIST — AI Risk Management Framework (USA)
**Jurisdiction:** United States
**What they have:** AI RMF 1.0 (2023), AI 100-1 (2024), various profiles.
**What's MISSING:** Agent-specific risk profile. Compliance verification framework for autonomous systems.
**Our opportunity:** Contribute **NIST AI RMF Profile for Autonomous Agent Systems** — mapping our 6 compliance gates to RMF functions (Govern, Map, Measure, Manage).
**Status:** NIST accepts public input. Profiles are lighter than full standards.

### BSI — British Standards Institution
**Jurisdiction:** United Kingdom
**What they have:** AI ethics PAS, AI risk management PAS. UK AI Standards Hub coordinator.
**What's MISSING:** UK-specific AI agent standards. NHS-aligned agent certification.
**Our opportunity:** Submit **BSI PAS for Agent Identity and Trust** — covers Identity Protocol + Trust Score + Reputation Ledger. UK-first, then push to ISO via BSI.
**Status:** PAS process takes 12-18 months. Fast track available.

## Submission Priority Matrix

| Priority | Body | What to Submit | Our Specs | Timeframe | Impact |
|----------|------|---------------|-----------|-----------|--------|
| 🥇 | CEN-CENELEC | Compliance-as-Code CWA | compliance-as-code + SLA | 12-18 months | EU AI Act alignment = mandatory adoption |
| 🥇 | IETF | IACP Internet-Draft | iacp.md | 12-24 months | Internet standard = universal adoption |
| 🥈 | BSI | Agent Identity PAS | identity + trust-score + reputation | 12-18 months | UK + ISO pathway |
| 🥈 | IEEE | ASFS Standard | asfs.md + converter | 12-24 months | Cross-platform skill format |
| 🥉 | ISO | Agent Interoperability NWIP | handoff + iacp + trust-score | 3-5 years | Global ISO standard |
| 🥉 | NIST | AI RMF Agent Profile | compliance-as-code + gates | 6-12 months | US government adoption |

## Immediate Actions (This Week)

1. **Draft IETF Internet-Draft for IACP** — lowest barrier to entry, most impact. Format: RFC-style markdown with ASCII art protocol diagrams.
2. **Register for CEN-CENELEC CWA** — contact JTC 21 secretariat to express interest in proposing Compliance-as-Code CWA.
3. **Prepare IEEE P7014 proposal** — draft the PAR (Project Authorization Request) for ASFS standard.
4. **Contact BSI** — inquire about PAS fast-track for agent identity standards.

## Where Nobody Is Looking

The biggest unclaimed territory is **agent-to-agent standards.** Every standards body is focused on:
- AI safety for humans
- AI ethics and bias
- AI data quality
- AI management systems

Nobody is asking: "How do agents talk to each other? How does agent A verify agent B's identity? How does an agent prove it completed work? How do agents discover each other's capabilities?"

**We already have the answers.** We just need to submit them.

## Companion Documents

- `iacp.md` — IACP specification (ready for IETF submission)
- `asfs.md` — ASFS specification (ready for IEEE submission)
- `compliance-as-code.md` — Compliance-as-Code spec (ready for CWA)
- `identity-protocol.md` — Identity Protocol (ready for BSI PAS)
- `handoff-protocol.md` — Handoff Protocol (already submitted to MCP SEP #2683, A2A #1817)
- `agent-osi-model.md` — Framework document (supporting material for all submissions)
