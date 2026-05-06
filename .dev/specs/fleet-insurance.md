# Agent Fleet Insurance — Strategic Concept

**Version:** 1.0.0-concept
**Status:** Exploration
**License:** CC BY 4.0

## 1. Thesis

When AI agents make autonomous decisions in regulated industries, the question "who pays when things go wrong?" has no answer. Humans carry professional indemnity insurance. Companies carry cyber insurance. Agents carry nothing.

Agent Fleet Insurance is a new insurance product category: coverage for the financial consequences of agent errors, hallucinations, compliance violations, and data breaches — priced by trust score and auditable by design.

## 2. Why Now

- **Agent autonomy is crossing a threshold.** Agents don't just suggest — they execute: write code, send emails, modify databases, interact with patients.
- **Regulated industries are adopting.** NHS trusts, banks, and government agencies are deploying agent fleets. Their compliance teams need insurance products to sign off.
- **Existing insurance doesn't cover agents.** Cyber insurance covers data breaches, not agent hallucinations. Professional indemnity covers human errors, not model errors.
- **We have the actuarial data.** Trust Score + SLA Framework + Audit Trail = the underwriting data insurers need.

## 3. Market Structure

| Layer | Who | What |
|-------|-----|------|
| **Insured** | Fleet operators (NHS trusts, banks, govt agencies) | Policy covering agent fleet errors |
| **Broker** | Works With Agents | Underwriting data, risk scoring, claims verification |
| **Insurer** | Existing insurance company (white-label partner) | Balance sheet, regulatory license, claims handling |
| **Reinsurer** | Lloyd's syndicate (future) | Catastrophic risk pooling |

**We do NOT become an insurer.** We provide the technology layer: risk scoring, audit trail verification, and claims evidence. Partner with established insurers for the regulated product.

## 4. Actuarial Model

### Risk Scoring

```
Risk Score = f(
    trust_score,        # 0-100, from Trust Score Protocol
    sla_compliance,     # % of SLAs met
    audit_trail_depth,  # days of continuous audit coverage
    model_safety,       # quality gate pass rate
    data_classification # internal / sensitive / patient
)
```

### Premium Tiers

| Tier | Risk Score | Annual Premium (per agent) | Coverage |
|------|-----------|---------------------------|----------|
| Platinum | 90+ | £50 | £500K |
| Gold | 75-89 | £150 | £250K |
| Silver | 60-74 | £400 | £100K |
| Bronze | 40-59 | £1,200 | £50K |
| Below 40 | — | Uninsurable | — |

### Claims Triggers

| Event | Evidence Required | Payout |
|-------|------------------|--------|
| Agent hallucination causes financial loss | Audit log + human verification | Policy limit |
| Agent violates compliance rule | Compliance-as-Code violation log | Remediation cost |
| Agent data breach | Audit log + ICO notification | Breach response cost |
| Agent SLA breach cascade | SLA Framework metrics | Consequential loss |

## 5. Integration Points

| Product | Role in Insurance |
|---------|------------------|
| **Agent Foundry** | Audit trail provider — continuous, tamper-evident |
| **Trust Score** | Primary underwriting input |
| **SLA Framework** | Breach detection + evidence |
| **Compliance-as-Code** | Automated compliance violation detection |
| **Reputation Ledger** | Claims history across organizations |
| **Blueprint Registry** | Model risk assessment for underwriting |

## 6. Business Model

- **Revenue:** 15-20% commission on premiums (industry standard for MGAs)
- **Unit economics:** 100-agent fleet × £150 avg premium = £15K gross → £2.5K commission
- **Target:** 20 fleets in Year 1 = £50K commission revenue
- **Cost:** Underwriting API + claims verification platform (already built — Foundry + Trust Score)
- **Regulatory:** Operate as MGA (Managing General Agent) under partner insurer's license

## 7. Risks & Open Questions

- **Will insurers underwrite AI risk?** Unknown. The actuarial data doesn't exist yet. We'd be creating the category.
- **Regulatory approval timeline.** FCA authorization for insurance intermediation takes 6-12 months.
- **Moral hazard.** If agents are insured, do operators take fewer precautions? Deductibles and co-pay structures needed.
- **Model update risk.** What happens to premiums when a model is updated? Continuous underwriting required.
- **Jurisdiction.** UK-regulated product first (FCA + PRA). EU expansion via passporting.

---

*This is a strategic exploration, not a product commitment. Feedback from insurance industry partners needed before proceeding.*
