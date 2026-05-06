/**
 * Transaction Protocol — Layer 7 Governance (TypeScript)
 * Guarantees for autonomous agent actions: idempotency, rollback, audit trail.
 * Reference implementation. CC BY 4.0.
 */

export enum TransactionStatus {
  INTENT = "intent",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  FAILED = "failed",
  ROLLED_BACK = "rolled_back",
  IDEMPOTENT_SKIP = "idempotent_skip",
}

export interface TransactionAction {
  action_id: string;
  intent: string;
  agent_id: string;
  session_id: string;
  idempotency_key: string;
  reversible: boolean;
  rollback_hook?: () => void;
  metadata: Record<string, unknown>;
}

export interface Transaction {
  tx_id: string;
  action: TransactionAction;
  status: TransactionStatus;
  created_at: string;
  completed_at: string | null;
  result: unknown;
  error: string | null;
  approver: string | null;
}

export class TransactionLedger {
  private ledger: Map<string, Transaction> = new Map();
  private completedKeys: Set<string> = new Set();
  agent_id: string;
  session_id: string;

  constructor(agent_id = "", session_id = "") {
    this.agent_id = agent_id;
    this.session_id = session_id;
  }

  intent(description: string, opts: {
    idempotency_key?: string;
    reversible?: boolean;
    rollback_hook?: () => void;
    metadata?: Record<string, unknown>;
    approver?: string;
  } = {}): Transaction {
    const action: TransactionAction = {
      action_id: crypto.randomUUID(),
      intent: description,
      agent_id: this.agent_id,
      session_id: this.session_id,
      idempotency_key: opts.idempotency_key || crypto.randomUUID(),
      reversible: opts.reversible || false,
      rollback_hook: opts.rollback_hook,
      metadata: opts.metadata || {},
    };

    const tx: Transaction = {
      tx_id: crypto.randomUUID(),
      action,
      status: TransactionStatus.INTENT,
      created_at: new Date().toISOString(),
      completed_at: null,
      result: null,
      error: null,
      approver: opts.approver || null,
    };

    if (this.completedKeys.has(action.idempotency_key)) {
      tx.status = TransactionStatus.IDEMPOTENT_SKIP;
      tx.result = "Previously completed — skipped";
    }

    this.ledger.set(tx.tx_id, tx);
    return tx;
  }

  execute(tx: Transaction, fn: () => unknown): Transaction {
    if (tx.status === TransactionStatus.IDEMPOTENT_SKIP) return tx;

    tx.status = TransactionStatus.IN_PROGRESS;
    try {
      tx.result = fn();
      tx.status = TransactionStatus.COMPLETED;
      tx.completed_at = new Date().toISOString();
      this.completedKeys.add(tx.action.idempotency_key);
    } catch (e) {
      tx.status = TransactionStatus.FAILED;
      tx.error = e instanceof Error ? e.message : String(e);
      if (tx.action.reversible && tx.action.rollback_hook) {
        this.rollback(tx);
      }
    }
    this.ledger.set(tx.tx_id, tx);
    return tx;
  }

  rollback(tx: Transaction): Transaction {
    if (tx.status === TransactionStatus.ROLLED_BACK) return tx;
    if (tx.action.rollback_hook) {
      try {
        tx.action.rollback_hook();
        tx.status = TransactionStatus.ROLLED_BACK;
      } catch (e) {
        tx.error = `Rollback failed: ${e instanceof Error ? e.message : String(e)}`;
      }
    }
    this.ledger.set(tx.tx_id, tx);
    return tx;
  }

  requiresApproval(tx: Transaction, approver: string): boolean {
    tx.approver = approver;
    this.ledger.set(tx.tx_id, tx);
    return approver !== "";
  }

  auditTrail(agent_id?: string): Record<string, unknown>[] {
    const entries = Array.from(this.ledger.values()).map(tx => ({
      tx_id: tx.tx_id,
      intent: tx.action.intent,
      agent: tx.action.agent_id,
      session: tx.action.session_id,
      status: tx.status,
      created: tx.created_at,
      completed: tx.completed_at,
      error: tx.error,
      approver: tx.approver,
    }));
    return agent_id ? entries.filter(e => e.agent === agent_id) : entries;
  }

  stats(): Record<string, number> {
    const txs = Array.from(this.ledger.values());
    return {
      total: txs.length,
      completed: txs.filter(t => t.status === TransactionStatus.COMPLETED).length,
      failed: txs.filter(t => t.status === TransactionStatus.FAILED).length,
      rolled_back: txs.filter(t => t.status === TransactionStatus.ROLLED_BACK).length,
      idempotent_skips: txs.filter(t => t.status === TransactionStatus.IDEMPOTENT_SKIP).length,
      in_progress: txs.filter(t => t.status === TransactionStatus.IN_PROGRESS).length,
    };
  }
}
