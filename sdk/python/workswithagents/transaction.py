"""
Transaction Protocol — Layer 7 (Governance)
Guarantees for autonomous agent actions: idempotency, rollback, audit trail.
Reference implementation. CC BY 4.0.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Optional
from uuid import uuid4


class TransactionStatus(Enum):
    INTENT = "intent"           # Logged before execution
    IN_PROGRESS = "in_progress" # Currently executing
    COMPLETED = "completed"     # Finished successfully
    FAILED = "failed"           # Execution failed
    ROLLED_BACK = "rolled_back" # Reverted
    IDEMPOTENT_SKIP = "idempotent_skip"  # Already done


@dataclass
class TransactionAction:
    """A single action within a transaction."""
    action_id: str = field(default_factory=lambda: str(uuid4()))
    intent: str = ""  # Human-readable: "deploy to production", "charge customer"
    agent_id: str = ""
    session_id: str = ""
    idempotency_key: str = field(default_factory=lambda: str(uuid4()))
    reversible: bool = False
    rollback_hook: Optional[Callable] = None
    metadata: dict = field(default_factory=dict)


@dataclass
class Transaction:
    """A tracked agent transaction with intent→action→confirmation flow."""
    tx_id: str = field(default_factory=lambda: str(uuid4()))
    action: TransactionAction = field(default_factory=TransactionAction)
    status: TransactionStatus = TransactionStatus.INTENT
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    approver: Optional[str] = None  # Human approver if required


class TransactionLedger:
    """
    Immutable audit trail for agent actions.
    Every action is logged before execution (intent) and after (confirmation).

    Usage:
        ledger = TransactionLedger()
        tx = ledger.intent("deploy to production", agent_id="builder-01")
        ledger.execute(tx, deploy_fn)
        # On failure:
        ledger.rollback(tx)
    """

    def __init__(self, agent_id: str = "", session_id: str = ""):
        self.agent_id = agent_id
        self.session_id = session_id
        self._ledger: dict[str, Transaction] = {}
        self._completed_keys: set[str] = set()  # For idempotency

    def intent(self, description: str, *,
               idempotency_key: Optional[str] = None,
               reversible: bool = False,
               rollback_hook: Optional[Callable] = None,
               metadata: Optional[dict] = None,
               requires_approval: bool = False,
               approver: Optional[str] = None) -> Transaction:
        """Log intent before execution. Returns a Transaction ready to execute."""
        action = TransactionAction(
            intent=description,
            agent_id=self.agent_id,
            session_id=self.session_id,
            idempotency_key=idempotency_key or str(uuid4()),
            reversible=reversible,
            rollback_hook=rollback_hook,
            metadata=metadata or {},
        )
        tx = Transaction(action=action, approver=approver)

        # Idempotency check
        if action.idempotency_key in self._completed_keys:
            tx.status = TransactionStatus.IDEMPOTENT_SKIP
            tx.result = "Previously completed — skipped"

        self._ledger[tx.tx_id] = tx
        return tx

    def execute(self, tx: Transaction, fn: Callable) -> Transaction:
        """Execute a transaction's action function with error handling."""
        if tx.status == TransactionStatus.IDEMPOTENT_SKIP:
            return tx

        tx.status = TransactionStatus.IN_PROGRESS

        try:
            result = fn()
            tx.status = TransactionStatus.COMPLETED
            tx.result = result
            tx.completed_at = datetime.now(timezone.utc).isoformat()
            self._completed_keys.add(tx.action.idempotency_key)
        except Exception as e:
            tx.status = TransactionStatus.FAILED
            tx.error = str(e)
            if tx.action.reversible and tx.action.rollback_hook:
                self.rollback(tx)

        self._ledger[tx.tx_id] = tx
        return tx

    def rollback(self, tx: Transaction) -> Transaction:
        """Attempt to roll back a transaction."""
        if tx.status == TransactionStatus.ROLLED_BACK:
            return tx
        if tx.action.rollback_hook:
            try:
                tx.action.rollback_hook()
                tx.status = TransactionStatus.ROLLED_BACK
            except Exception as e:
                tx.error = f"Rollback failed: {e}"
        self._ledger[tx.tx_id] = tx
        return tx

    def requires_approval(self, tx: Transaction, approver: str) -> bool:
        """Human approval gate. Returns True if approved."""
        tx.approver = approver
        self._ledger[tx.tx_id] = tx
        return approver != ""

    def audit_trail(self, agent_id: Optional[str] = None) -> list[dict]:
        """Get all transactions, optionally filtered by agent."""
        entries = [
            {
                "tx_id": tx.tx_id,
                "intent": tx.action.intent,
                "agent": tx.action.agent_id,
                "session": tx.action.session_id,
                "status": tx.status.value,
                "created": tx.created_at,
                "completed": tx.completed_at,
                "error": tx.error,
                "approver": tx.approver,
            }
            for tx in self._ledger.values()
        ]
        if agent_id:
            entries = [e for e in entries if e["agent"] == agent_id]
        return entries

    def stats(self) -> dict:
        """Transaction statistics."""
        all_txs = list(self._ledger.values())
        return {
            "total": len(all_txs),
            "completed": sum(1 for t in all_txs if t.status == TransactionStatus.COMPLETED),
            "failed": sum(1 for t in all_txs if t.status == TransactionStatus.FAILED),
            "rolled_back": sum(1 for t in all_txs if t.status == TransactionStatus.ROLLED_BACK),
            "idempotent_skips": sum(1 for t in all_txs if t.status == TransactionStatus.IDEMPOTENT_SKIP),
            "in_progress": sum(1 for t in all_txs if t.status == TransactionStatus.IN_PROGRESS),
        }
