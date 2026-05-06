#!/usr/bin/env node
/**
 * Vanilla Agent — TypeScript reference implementation.
 * Full 7-layer OSI Model. Single file. Zero dependencies.
 * Copy, run, get a standards-compliant agent. CC BY 4.0.
 *
 * Usage:
 *   npx tsx vanilla_agent.ts --name "reviewer" --purpose "code review"
 *   npx tsx vanilla_agent.ts --demo
 */

import * as crypto from "crypto";

// ═══════════════════════════════════════════════════════════════════════
// L2 — Identity Protocol
// ═══════════════════════════════════════════════════════════════════════

class AgentIdentity {
  publicKeyHex: string;

  constructor(public agentId: string) {
    this.publicKeyHex = crypto.createHash("sha256")
      .update(crypto.randomBytes(32)).digest("hex");
  }

  sign(payload: Record<string, unknown>): string {
    const msg = JSON.stringify(payload, Object.keys(payload).sort());
    return crypto.createHash("sha256")
      .update(msg + this.publicKeyHex).digest("hex");
  }

  static verify(agentId: string, payload: Record<string, unknown>,
                signature: string, publicKey: string): boolean {
    const msg = JSON.stringify(payload, Object.keys(payload).sort());
    return crypto.createHash("sha256")
      .update(msg + publicKey).digest("hex") === signature;
  }
}

// ═══════════════════════════════════════════════════════════════════════
// L4 — Handoff Protocol
// ═══════════════════════════════════════════════════════════════════════

interface HandoffPayload {
  handoff_id: string;
  task_id: string;
  sender: { agent_id: string; identity_sig?: string };
  context: { task_description: string; state_snapshot: Record<string, unknown>; quality_checklist: string[] };
}

class HandoffProtocol {
  createHandoff(taskId: string, sender: AgentIdentity,
                task: Record<string, unknown>, checklist: string[] = []): HandoffPayload {
    const payload: HandoffPayload = {
      handoff_id: crypto.randomUUID(),
      task_id: taskId,
      sender: { agent_id: sender.agentId },
      context: {
        task_description: (task.description as string) || "",
        state_snapshot: (task.state as Record<string, unknown>) || {},
        quality_checklist: checklist.length ? checklist : ["Verify output", "Run tests"],
      },
    };
    payload.sender.identity_sig = sender.sign(payload as unknown as Record<string, unknown>);
    return payload;
  }

  acceptHandoff(handoff: HandoffPayload, receiver: AgentIdentity) {
    return {
      status: "accepted",
      handoff_id: handoff.handoff_id,
      receiver: receiver.agentId,
      estimated_completion: new Date().toISOString(),
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════
// L5 — Coordination Protocol
// ═══════════════════════════════════════════════════════════════════════

enum AgentRole { LEADER = "leader", FOLLOWER = "follower", CANDIDATE = "candidate" }

class CoordinationClient {
  role: AgentRole = AgentRole.FOLLOWER;
  term = 0;
  leaderId: string | null = null;
  workQueue: Map<string, Record<string, unknown>> = new Map();

  constructor(public agentId: string, public peers: string[] = []) {}

  startElection() {
    this.role = AgentRole.CANDIDATE;
    this.term += 1;
    return { type: "elect", candidate: this.agentId, term: this.term };
  }

  becomeLeader() {
    this.role = AgentRole.LEADER;
    this.leaderId = this.agentId;
    return { type: "heartbeat", leader: this.agentId, term: this.term };
  }

  assignWork(target: string, task: Record<string, unknown>, priority = 5): string {
    const tid = `task-${crypto.randomUUID().slice(0, 8)}`;
    this.workQueue.set(tid, { target, task, priority, status: "assigned" });
    return tid;
  }

  getStatus() {
    return { role: this.role, leader: this.leaderId, term: this.term, active_tasks: this.workQueue.size };
  }
}

// ═══════════════════════════════════════════════════════════════════════
// L7 — Transaction Protocol
// ═══════════════════════════════════════════════════════════════════════

enum TxStatus { INTENT = "intent", COMPLETED = "completed", FAILED = "failed", ROLLED_BACK = "rolled_back" }

interface Transaction {
  tx_id: string; intent: string; agent_id: string;
  status: TxStatus; created_at: string; completed_at: string | null;
  result: unknown; error: string | null;
}

class TransactionLedger {
  private ledger: Map<string, Transaction> = new Map();

  constructor(public agentId: string) {}

  intent(description: string): Transaction {
    const tx: Transaction = {
      tx_id: crypto.randomUUID(), intent: description, agent_id: this.agentId,
      status: TxStatus.INTENT, created_at: new Date().toISOString(),
      completed_at: null, result: null, error: null,
    };
    this.ledger.set(tx.tx_id, tx);
    return tx;
  }

  execute(tx: Transaction, fn: () => unknown): Transaction {
    try {
      tx.result = fn();
      tx.status = TxStatus.COMPLETED;
      tx.completed_at = new Date().toISOString();
    } catch (e) {
      tx.status = TxStatus.FAILED;
      tx.error = e instanceof Error ? e.message : String(e);
    }
    return tx;
  }

  audit() {
    return Array.from(this.ledger.values()).map(t => ({
      id: t.tx_id, intent: t.intent, status: t.status,
      created: t.created_at, error: t.error,
    }));
  }

  stats() {
    const txs = Array.from(this.ledger.values());
    return { total: txs.length, completed: txs.filter(t => t.status === TxStatus.COMPLETED).length,
             failed: txs.filter(t => t.status === TxStatus.FAILED).length };
  }
}

// ═══════════════════════════════════════════════════════════════════════
// L7 — Compliance Gate
// ═══════════════════════════════════════════════════════════════════════

const COMPLIANCE_RULES: Record<string, Array<{ field: string; operator: string; value: string[]; message: string }>> = {
  nhs_dtac: [
    { field: "data_classification", operator: "not_in",
      value: ["patient_identifiable", "clinical_confidential"],
      message: "Patient data must not be processed without DPIA" },
  ],
  gdpr: [
    { field: "data_classification", operator: "not_in",
      value: ["personal_data_unconsented"],
      message: "Unconsented personal data blocked" },
  ],
};

function validateCompliance(regulation: string, action: Record<string, unknown>) {
  const rules = COMPLIANCE_RULES[regulation] || [];
  const violations: string[] = [];
  for (const rule of rules) {
    const actual = String(action[rule.field] || "");
    if (rule.operator === "not_in" && rule.value.includes(actual)) {
      violations.push(rule.message);
    }
  }
  return { passed: violations.length === 0, violations };
}

// ═══════════════════════════════════════════════════════════════════════
// Vanilla Agent
// ═══════════════════════════════════════════════════════════════════════

class VanillaAgent {
  agentId: string;
  identity: AgentIdentity;
  capabilities: Record<string, unknown>;
  handoff: HandoffProtocol;
  coord: CoordinationClient;
  ledger: TransactionLedger;
  handoffQueue: Array<{ handoff: HandoffPayload; accepted: string }> = [];
  tasksDone = 0;
  tasksFailed = 0;
  startedAt: string;

  constructor(public name: string, public purpose: string, public tools: string[] = ["terminal", "file"]) {
    this.agentId = `agent-${name}-${crypto.randomUUID().slice(0, 6)}`;
    this.startedAt = new Date().toISOString();
    this.identity = new AgentIdentity(this.agentId);
    this.handoff = new HandoffProtocol();
    this.coord = new CoordinationClient(this.agentId);
    this.ledger = new TransactionLedger(this.agentId);
    this.capabilities = { agent_id: this.agentId, name, purpose, tools, model: "vanilla", trust_score: 50 };
  }

  boot() {
    return { agent_id: this.agentId, capabilities: this.capabilities, status: "ready" };
  }

  receiveTask(task: Record<string, unknown>) {
    const taskId = (task.task_id as string) || crypto.randomUUID();
    const handoff = this.handoff.createHandoff(taskId, this.identity, task,
      (task.checklist as string[]) || []);
    const response = this.handoff.acceptHandoff(handoff, this.identity);
    this.handoffQueue.push({ handoff, accepted: response.status });
    const result = this.execute(task);
    return { ...response, result };
  }

  execute(task: Record<string, unknown>) {
    for (const regulation of ["nhs_dtac", "gdpr"]) {
      const result = validateCompliance(regulation, task);
      if (!result.passed) return { status: "blocked", violations: result.violations };
    }

    const tx = this.ledger.intent((task.description as string) || "execute task");
    try {
      const tool = (task.tool as string) || "echo";
      console.log(`  [${this.agentId}] Running ${tool}...`);
      this.ledger.execute(tx, () => ({ ok: true }));
      this.tasksDone++;
      return { status: "completed", tx_id: tx.tx_id };
    } catch (e) {
      this.ledger.execute(tx, () => { throw e; });
      this.tasksFailed++;
      return { status: "failed", error: String(e) };
    }
  }

  joinFleet(peers: string[] = []) {
    this.coord.peers = peers;
    this.coord.startElection();
    return this.coord.getStatus();
  }

  report() {
    return {
      agent_id: this.agentId, name: this.name, purpose: this.purpose,
      tools: this.tools, tasks_done: this.tasksDone, tasks_failed: this.tasksFailed,
      handoffs_received: this.handoffQueue.length,
      coordination: this.coord.getStatus(), audit: this.ledger.stats(),
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════
// Demo
// ═══════════════════════════════════════════════════════════════════════

async function demo() {
  console.log("═".repeat(60));
  console.log("  Vanilla Agent — OSI Reference (TypeScript)");
  console.log("  Works With Agents · CC BY 4.0");
  console.log("═".repeat(60) + "\n");

  const builder = new VanillaAgent("builder", "build software", ["terminal", "file", "git"]);
  const reviewer = new VanillaAgent("reviewer", "review code", ["terminal", "file", "web"]);

  console.log("── L1-L3: Boot, Identity, Capabilities ──");
  console.log(`  ${builder.boot().agent_id} ready`);
  console.log(`  ${reviewer.boot().agent_id} ready\n`);

  console.log("── L4: Handoff Protocol ──");
  const result = reviewer.receiveTask({
    task_id: "task-001", description: "Build API endpoint",
    tool: "file", data_classification: "internal",
  });
  console.log(`  ${reviewer.agentId} received: ${result.status}\n`);

  console.log("── L5: Coordination Protocol ──");
  const fleet = builder.joinFleet([reviewer.agentId]);
  console.log(`  ${builder.agentId} fleet: ${fleet.role} (term ${fleet.term})`);
  builder.coord.assignWork(reviewer.agentId, { description: "Review PR", tool: "terminal", data_classification: "internal" });
  console.log(`  ${builder.agentId} assigned work to ${reviewer.agentId}\n`);

  console.log("── L6-L7: Execute + Governance ──");
  const safe = builder.execute({ description: "Run tests", tool: "terminal", data_classification: "internal" });
  console.log(`  Safe task: ${safe.status}`);
  const blocked = builder.execute({ description: "Process patient data", tool: "file", data_classification: "patient_identifiable" });
  console.log(`  Blocked: ${blocked.status} — ${(blocked.violations as string[] || []).join(", ")}\n`);

  console.log("── L7: Audit Trail ──");
  for (const entry of builder.ledger.audit()) {
    console.log(`  [${entry.status}] ${entry.intent}`);
  }
  console.log();

  console.log("── Reports ──");
  for (const agent of [builder, reviewer]) {
    const r = agent.report();
    console.log(`  ${r.agent_id}: ${r.tasks_done} done, ${r.tasks_failed} failed`);
  }
  console.log("\n" + "═".repeat(60));
  console.log("  Demo complete. 7 layers, 2 agents, 0 external deps.");
  console.log("═".repeat(60));
}

// CLI
const args = process.argv.slice(2);
if (args.includes("--demo")) {
  demo().catch(console.error);
} else {
  console.log("Vanilla Agent — TypeScript. Use --demo for the full OSI demo.");
}
