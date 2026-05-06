# Local-First Certification (Cross-Cutting)

**Layer:** Cross-Cutting (L0-L7)
**Status:** Specification v1.0
**License:** CC BY 4.0

## Abstract

Local-First Certification verifies that an AI agent or agent infrastructure operates entirely on-premises without external API dependencies. Certified agents guarantee data sovereignty, offline operation, and zero third-party data transmission.

## Certification Levels

| Level | Name | Requirements |
|-------|------|-------------|
| L1 | **Local Inference** | Model runs locally. No cloud API calls for inference. |
| L2 | **Local Data** | All data processing happens on-prem. No external storage. |
| L3 | **Fully Air-Gapped** | Zero outbound connections. Operates on isolated network. |

## Verification

1. Agent declares target certification level
2. Automated audit runs network capture during operation
3. Any outbound call to non-approved endpoints fails certification
4. Certified agents receive `local-first.svg` badge

## Badge

`![Local-First Certified](https://workswithagents.io/badges/local-first.svg)`

## Related Protocols

- Identity Protocol (L2) — agents must have cryptographic identity before certification
- Trust Score (L3) — Local-First certification contributes positively to trust score
- Onboarding Protocol (L1) — certification is part of agent provisioning
