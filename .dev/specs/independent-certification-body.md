# Independent Agent Certification Body — Strategic Concept

**Version:** 1.0.0-concept
**Status:** Investigation
**License:** CC BY 4.0

## 1. Thesis

Become the **B Corp for AI agent platforms** — an independent certification body that sets the industry standard for what a trustworthy, safe, and capable agent platform looks like.

Today, anyone can claim their agent platform is "production-ready" or "enterprise-grade." There is no independent verification. No industry standard. No trusted badge that procurement teams can look for.

We fill that gap.

## 2. What It Is (and Isn't)

**IS:**
- An independent certification body with a board, published criteria, and audit process
- A badge that says "this agent platform meets the industry standard"
- A procurement shortcut for regulated industries (NHS, finance, government)
- A revenue stream from certification fees + annual audits

**IS NOT:**
- A Works With Agents product badge (that's L1-L3 certification — already built)
- A regulatory approval (doesn't replace DTAC, FCA, FDA)
- A self-certification (must have independent governance)

## 3. Governance Separation (Critical)

The certification body MUST be legally and operationally separate from Works With Agents.

### Proposed Structure

```
Independent Agent Certification Foundation (IACF)
├── Board of Trustees (3-5 members, industry + academic)
├── Technical Committee (defines test criteria)
├── Audit Committee (oversees certification process)
└── Certification Authority (issues badges, maintains registry)

Works With Agents (product company)
├── Builds the certification test suite (open source)
├── Provides reference implementations
├── Can BE certified (but not self-certify)
└── Board seat on IACF (minority — max 1 of 5)
```

### Legal Structure Options

| Structure | Jurisdiction | Pros | Cons |
|-----------|-------------|------|------|
| UK CIC (Community Interest Company) | UK | Asset lock, community purpose, FCA-compatible | Setup time 4-8 weeks |
| UK Charitable Incorporated Organisation | UK | Tax benefits, trust | Slow setup, charity commission oversight |
| Non-profit Ltd by Guarantee | UK | Flexible, fast setup | Less trust than CIO |
| Foundation (Stichting) | Netherlands | EU-friendly, flexible | Cross-border complexity |

**Recommendation:** UK CIC. Asset lock prevents capture. Community purpose aligns with regulated industry goals. FCA-compatible for insurance play. Setup: 4-8 weeks, £500-1000.

## 4. Certification Criteria (Draft)

### Tier 1 — Registered
- Publicly documented APIs
- Published model cards for all models used
- Contact information for security issues
- Free. Self-attestation. Badge: silver.

### Tier 2 — Verified
- All Tier 1 requirements
- Independent audit of claims
- 7-agent test suite passed
- Security penetration test (annual)
- GDPR compliance verified
- £X/year. Badge: gold.

### Tier 3 — Regulated-Ready
- All Tier 2 requirements
- NHS DTAC alignment verified
- FCA/PRA compliance framework
- Continuous monitoring (audit trail + heartbeats)
- Insurance-ready (actuarial data available)
- £X/year. Badge: platinum.

### Specializations
- **Local-First** — zero cloud dependency verified
- **Healthcare** — DTAC + Caldicott compliant
- **Finance** — FCA Senior Managers Regime compatible
- **Government** — GDS Service Standard aligned

## 5. Market Opportunity

### Who needs this?

| Buyer | Pain Point | Certification Solves |
|-------|-----------|---------------------|
| NHS Trust CIO | "Is this agent platform safe for patient data?" | DTAC-verified badge = procurement shortcut |
| Bank CISO | "Can I prove to FCA that our agents are controlled?" | Regulated-Ready badge = audit evidence |
| Government CTO | "Which agent platforms meet GDS standards?" | Government specialization = pre-vetted list |
| Enterprise VP Eng | "How do I choose between 50 agent platforms?" | Verified badge = trust signal |

### Market Size (UK)

- NHS trusts: 215
- FCA-regulated firms: 50,000+
- Government departments: 400+
- FTSE 350: 350

Target: 100 certified platforms in Year 3 = £500K-£1M annual revenue.

## 6. Competitive Landscape (Empty)

**Nobody is doing this.** Existing certification bodies:
- ISO 27001 — information security, not agent-specific
- SOC 2 — US-centric, cloud-focused, not agent-aware
- B Corp — social/environmental, not technical
- NHS DTAC — health-specific, not agent-specific

**We would be first mover in a category that doesn't exist yet.**

## 7. Revenue Model

| Tier | Annual Fee | Target Volume (Y3) | Annual Revenue |
|------|-----------|-------------------|----------------|
| Registered | Free | 500 | £0 |
| Verified | £2,500 | 75 | £187,500 |
| Regulated-Ready | £10,000 | 25 | £250,000 |
| **Total** | | | **£437,500** |

Additional: audit fees, specialization add-ons, training/certification for auditors.

## 8. Path to Credibility

Year 1:
- Establish CIC legal structure
- Recruit 3 independent board members (academic + ex-regulator + industry)
- Publish certification criteria v1.0
- Certify 3-5 platforms (including Works With Agents products, independently audited)
- Apply for UKAS accreditation (voluntary but adds credibility)

Year 2:
- 20+ certified platforms
- First Regulated-Ready certifications
- NHS DTAC recognition (listed as accepted certification in procurement guidance)
- FCA regulatory sandbox engagement

Year 3:
- 100+ certified platforms
- UKAS accredited
- International expansion (EU via Dublin office, US via Delaware non-profit)

## 9. Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| No platforms apply | High (Y1) | Start with free tier. Certify our own products to bootstrap. |
| Perceived conflict of interest | High | Strict governance separation. Independent board majority. |
| Regulatory indifference | Medium | Engage early. DTAC alignment is our Trojan horse. |
| Competitor launches similar | Medium | First-mover advantage. Publish criteria as open standard. |
| Too early — market not ready | Medium | Build framework now, launch when 10+ platforms exist. |

## 10. Recommendation

**Verdict: PURSUE — but as Phase 2 framework, not immediate launch.**

**Phase 1 (NOW):**
- Publish this concept as a specification
- Build the certification test suite (leveraging existing quality gates)
- Draft governance charter
- Identify potential board members (academic contacts, ex-regulators)

**Phase 2 (Q3-Q4 2026):**
- Establish CIC legal structure
- Recruit board
- Certify first 3 platforms
- Publish certification registry at cert.workswithagents.com

**Phase 3 (2027):**
- Full launch with 20+ certified platforms
- Regulated-Ready tier operational
- UKAS accreditation application

**Gate:** Require at minimum 10 L3-certified platforms before launching independent body. Until then, operate certification as a Works With Agents product (which we've already built with L1-L3 badges).

---

*This is a strategic exploration. Board recruitment, legal advice, and market validation are prerequisites for execution.*
