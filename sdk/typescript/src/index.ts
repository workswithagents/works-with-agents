/**
 * Works With Agents — TypeScript SDK
 * Reference implementations for all Agent OSI Model protocols.
 * Zero dependencies. Copy-pasteable. CC BY 4.0.
 */

export const DEFAULT_API = "https://workswithagents.dev";

// ── Coordination (Layer 5) ────────────────────────────────────────────
export { CoordinationClient, AgentRole } from "./coordination";
export type { CoordinationMessage } from "./coordination";

// ── Transaction (Layer 6) ─────────────────────────────────────────────
export { TransactionLedger, TransactionStatus } from "./transaction";
export type { Transaction, TransactionAction } from "./transaction";

// ── Fleet Insurance (Layer 7) ─────────────────────────────────────────
export { FleetInsurance } from "./fleet_insurance";
export type { RiskProfile, Policy, Claim } from "./fleet_insurance";

// ── Trust Score (Layer 3/5) ───────────────────────────────────────────
export { TrustScoreClient } from "./trust_score";

// ── Deployment Manifest (Cross-Layer) ─────────────────────────────────
export { DeploymentManifest } from "./deployment";

// ── SLA Framework (Layer 7) ───────────────────────────────────────────
export { SLAMetrics } from "./sla";
export type { SLATier, SLATargets } from "./sla";

// ── Identity Protocol (Layer 2/3) ─────────────────────────────────────
export { AgentIdentity } from "./identity";

// ── Compliance-as-Code (Layer 7) ──────────────────────────────────────
export { ComplianceEngine, RegulationPack, safeExecute } from "./compliance";
export type { ComplianceResult, ComplianceRule } from "./compliance";

// ── IACP (Layer 4) ────────────────────────────────────────────────────
export { IACPClient } from "./iacp";
export type { IACPMessage } from "./iacp";

// ── Economics (Cross-Layer) ───────────────────────────────────────────
export { EconomicsClient } from "./economics";

// ── Reputation (Layer 5) ──────────────────────────────────────────────
export { ReputationClient } from "./reputation";

// ── Onboarding (Layer 1/3) ────────────────────────────────────────────
export { OnboardingClient } from "./onboarding";
export type { OnboardingInterview } from "./onboarding";
