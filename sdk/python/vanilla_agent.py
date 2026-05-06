#!/usr/bin/env python3
"""
Vanilla Agent — Reference implementation of the Works With Agents OSI Model.
Full 7-layer stack. Single file. ZERO external dependencies beyond Python stdlib.
Copy, run, get a standards-compliant agent. CC BY 4.0.

Usage:
    python vanilla_agent.py --name "reviewer" --purpose "code review"
    python vanilla_agent.py --name "reviewer" --purpose "code review" --demo
"""

import argparse, hashlib, json, os, signal, sys, time, uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Callable, Optional

# ═══════════════════════════════════════════════════════════════════════
# L2 — Identity Protocol (Ed25519 via hashlib — reference only)
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class AgentIdentity:
    """Ed25519 identity for agent signing. Reference: use nacl/pyca for real crypto."""
    agent_id: str
    public_key_hex: str = field(default_factory=lambda: hashlib.sha256(os.urandom(32)).hexdigest())

    def sign(self, payload: dict) -> str:
        """Sign a payload. Reference impl uses SHA-256 of JSON."""
        msg = json.dumps(payload, sort_keys=True).encode()
        return hashlib.sha256(msg + self.public_key_hex.encode()).hexdigest()

    @staticmethod
    def verify(agent_id: str, payload: dict, signature: str, public_key: str) -> bool:
        msg = json.dumps(payload, sort_keys=True).encode()
        return hashlib.sha256(msg + public_key.encode()).hexdigest() == signature

# ═══════════════════════════════════════════════════════════════════════
# L4 — Handoff Protocol
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class HandoffProtocol:
    """Task transfer with complete context. Reference implementation."""

    def create_handoff(self, task_id: str, sender: AgentIdentity, task: dict,
                       quality_checklist: list[str] = None) -> dict:
        payload = {
            "handoff_id": str(uuid.uuid4()),
            "task_id": task_id,
            "sender": {"agent_id": sender.agent_id},
            "context": {
                "task_description": task.get("description", ""),
                "state_snapshot": task.get("state", {}),
                "quality_checklist": quality_checklist or [],
            },
        }
        payload["sender"]["identity_sig"] = sender.sign(payload)
        return payload

    def accept_handoff(self, handoff: dict, receiver: AgentIdentity) -> dict:
        sender_id = handoff.get("sender", {}).get("agent_id", "")
        return {
            "status": "accepted",
            "handoff_id": handoff.get("handoff_id", ""),
            "receiver": receiver.agent_id,
            "estimated_completion": datetime.now(timezone.utc).isoformat(),
        }

# ═══════════════════════════════════════════════════════════════════════
# L5 — Coordination Protocol
# ═══════════════════════════════════════════════════════════════════════

class AgentRole(Enum):
    LEADER = "leader"
    FOLLOWER = "follower"
    CANDIDATE = "candidate"

@dataclass
class CoordinationClient:
    """Leader election, work distribution, conflict resolution."""
    agent_id: str
    role: AgentRole = AgentRole.FOLLOWER
    term: int = 0
    leader_id: Optional[str] = None
    peers: list[str] = field(default_factory=list)
    _work_queue: dict = field(default_factory=dict)
    _conflict_log: dict = field(default_factory=dict)

    def start_election(self) -> dict:
        self.role = AgentRole.CANDIDATE
        self.term += 1
        return {"type": "elect", "candidate": self.agent_id, "term": self.term}

    def become_leader(self) -> dict:
        self.role = AgentRole.LEADER
        self.leader_id = self.agent_id
        return {"type": "heartbeat", "leader": self.agent_id, "term": self.term}

    def assign_work(self, target: str, task: dict, priority: int = 5) -> str:
        tid = f"task-{uuid.uuid4().hex[:8]}"
        self._work_queue[tid] = {"target": target, "task": task, "priority": priority, "status": "assigned"}
        return tid

    def get_status(self) -> dict:
        return {"role": self.role.value, "leader": self.leader_id, "term": self.term,
                "active_tasks": len(self._work_queue)}

# ═══════════════════════════════════════════════════════════════════════
# L7 — Transaction Protocol
# ═══════════════════════════════════════════════════════════════════════

class TransactionStatus(Enum):
    INTENT = "intent"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class Transaction:
    tx_id: str
    intent: str
    agent_id: str
    status: TransactionStatus = TransactionStatus.INTENT
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    result: any = None
    error: Optional[str] = None

class TransactionLedger:
    """Immutable audit trail for agent actions."""
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._ledger: dict[str, Transaction] = {}
        self._completed: set[str] = set()

    def intent(self, description: str, metadata: dict = None) -> Transaction:
        tx = Transaction(tx_id=str(uuid.uuid4()), intent=description, agent_id=self.agent_id)
        self._ledger[tx.tx_id] = tx
        return tx

    def execute(self, tx: Transaction, fn: Callable) -> Transaction:
        try:
            tx.result = fn()
            tx.status = TransactionStatus.COMPLETED
            tx.completed_at = datetime.now(timezone.utc).isoformat()
        except Exception as e:
            tx.status = TransactionStatus.FAILED
            tx.error = str(e)
        return tx

    def audit(self) -> list[dict]:
        return [{"id": t.tx_id, "intent": t.intent, "status": t.status.value,
                 "created": t.created_at, "error": t.error} for t in self._ledger.values()]

    def stats(self) -> dict:
        txs = list(self._ledger.values())
        return {"total": len(txs), "completed": sum(1 for t in txs if t.status == TransactionStatus.COMPLETED),
                "failed": sum(1 for t in txs if t.status == TransactionStatus.FAILED)}

# ═══════════════════════════════════════════════════════════════════════
# L3 — Capability Manifest
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class CapabilityManifest:
    agent_id: str
    name: str
    purpose: str
    tools: list[str]
    model: str = "vanilla"
    max_tokens: int = 131072
    trust_score: float = 50.0
    deployment: str = "local"

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}

# ═══════════════════════════════════════════════════════════════════════
# L7 — Compliance-as-Code (simplified for standalone)
# ═══════════════════════════════════════════════════════════════════════

class ComplianceGate:
    """Simple compliance rule engine. Extend with real regulation packs."""

    DEFAULT_RULES = {
        "nhs_dtac": [
            {"field": "data_classification", "operator": "not_in",
             "value": ["patient_identifiable", "clinical_confidential"],
             "message": "Patient data must not be processed without DPIA"},
        ],
        "gdpr": [
            {"field": "data_classification", "operator": "not_in",
             "value": ["personal_data_unconsented"],
             "message": "Unconsented personal data blocked"},
        ],
    }

    @classmethod
    def validate(cls, regulation: str, action: dict) -> dict:
        rules = cls.DEFAULT_RULES.get(regulation, [])
        violations = []
        for rule in rules:
            actual = action.get(rule["field"], "")
            if rule["operator"] == "not_in" and actual in rule["value"]:
                violations.append(rule["message"])
        return {"passed": len(violations) == 0, "violations": violations}

# ═══════════════════════════════════════════════════════════════════════
# Vanilla Agent — 7-Layer OSI Reference
# ═══════════════════════════════════════════════════════════════════════

class VanillaAgent:
    """A standards-compliant AI agent implementing the full 7-layer OSI Model."""

    def __init__(self, name: str, purpose: str, tools: list[str] = None):
        self.name = name
        self.purpose = purpose
        self.agent_id = f"agent-{name}-{uuid.uuid4().hex[:6]}"
        self.tools = tools or ["terminal", "file", "web"]
        self.started_at = datetime.now(timezone.utc).isoformat()
        self._running = False

        # L2: Identity
        self.identity = AgentIdentity(self.agent_id)
        # L3: Capabilities
        self.capabilities = CapabilityManifest(self.agent_id, name, purpose, self.tools)
        # L4: Handoff
        self.handoff = HandoffProtocol()
        self._handoff_queue: list[dict] = []
        # L5: Coordination
        self.coord = CoordinationClient(self.agent_id)
        # L6: Task tracking
        self.tasks_done = 0
        self.tasks_failed = 0
        # L7: Governance
        self.ledger = TransactionLedger(self.agent_id)

    # ── Bootstrap ────────────────────────────────────────────────────
    def boot(self) -> dict:
        """L1-L3: Generate identity and publish capabilities."""
        return {
            "agent_id": self.agent_id,
            "identity": self.identity.public_key_hex[:16] + "...",
            "capabilities": self.capabilities.to_dict(),
            "status": "ready",
        }

    # ── L4: Handoff ──────────────────────────────────────────────────
    def receive_task(self, task: dict) -> dict:
        """Accept a task from another agent via Handoff Protocol."""
        task_id = task.get("task_id", str(uuid.uuid4()))
        handoff = self.handoff.create_handoff(
            task_id, self.identity, task,
            quality_checklist=task.get("checklist", ["Verify output", "Run tests"]),
        )
        response = self.handoff.accept_handoff(handoff, self.identity)
        self._handoff_queue.append({"handoff": handoff, "accepted": response["status"]})

        # Execute with compliance + audit
        result = self.execute(task)
        return {**response, "result": result}

    def handoff_to(self, target_agent: str, task: dict) -> dict:
        """Transfer a task to another agent."""
        task_id = str(uuid.uuid4())
        handoff = self.handoff.create_handoff(task_id, self.identity, task)
        return {"handoff_id": handoff["handoff_id"], "target": target_agent, "task_id": task_id}

    # ── L5: Coordination ─────────────────────────────────────────────
    def join_fleet(self, peers: list[str] = None) -> dict:
        """Join a fleet and coordinate."""
        self.coord.peers = peers or []
        self.coord.start_election()
        return self.coord.get_status()

    # ── L6-L7: Execute with compliance gates ─────────────────────────
    def execute(self, task: dict) -> dict:
        """Execute a task with compliance validation and audit trail."""

        # L7: Compliance check before execution
        for regulation in ["nhs_dtac", "gdpr"]:
            result = ComplianceGate.validate(regulation, task)
            if not result["passed"]:
                return {"status": "blocked", "reason": "compliance",
                        "violations": result["violations"]}

        # L7: Transaction intent → execution → confirmation
        tx = self.ledger.intent(task.get("description", "execute task"))

        try:
            ok = self._run(task)
            self.ledger.execute(tx, lambda: {"ok": ok})
            self.tasks_done += 1
            status = "completed"
        except Exception as e:
            self.ledger.execute(tx, lambda: (_ for _ in ()).throw(e))
            self.tasks_failed += 1
            status = "failed"

        return {"status": status, "tx_id": tx.tx_id,
                "tasks_done": self.tasks_done, "tasks_failed": self.tasks_failed}

    def _run(self, task: dict) -> bool:
        """Simulate tool execution. Replace with actual tool calls."""
        tool = task.get("tool", "echo")
        print(f"  [{self.agent_id}] Running {tool}...")
        return True

    # ── Stats ────────────────────────────────────────────────────────
    def report(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "purpose": self.purpose,
            "tools": self.tools,
            "uptime_s": int((datetime.now(timezone.utc) -
                             datetime.fromisoformat(self.started_at)).total_seconds()),
            "tasks_done": self.tasks_done,
            "tasks_failed": self.tasks_failed,
            "handoffs_received": len(self._handoff_queue),
            "coordination": self.coord.get_status(),
            "audit": self.ledger.stats(),
            "identity": self.identity.public_key_hex[:16] + "...",
        }

    # ── Run loop ─────────────────────────────────────────────────────
    def start(self):
        self._running = True
        boot = self.boot()
        print(f"╔══════════════════════════════════╗")
        print(f"║  {self.agent_id}  ║")
        print(f"║  {self.name:28s}  ║")
        print(f"║  {self.purpose:28s}  ║")
        print(f"║  ID: {boot['identity']:21s}  ║")
        print(f"║  Tools: {', '.join(self.tools):18s}  ║")
        print(f"╚══════════════════════════════════╝")
        print()

        while self._running:
            time.sleep(1)

    def stop(self):
        self._running = False


# ═══════════════════════════════════════════════════════════════════════
# Demo
# ═══════════════════════════════════════════════════════════════════════

def demo():
    """Run a full 7-layer demo with two agents coordinating."""
    print("=" * 60)
    print("  Vanilla Agent — OSI Reference Implementation")
    print("  Works With Agents · CC BY 4.0")
    print("=" * 60)
    print()

    # Create two agents
    builder = VanillaAgent("builder", "build software", ["terminal", "file", "git"])
    reviewer = VanillaAgent("reviewer", "review code", ["terminal", "file", "web"])

    # Boot
    print("── L1-L3: Boot, Identity, Capabilities ──")
    b_boot = builder.boot()
    r_boot = reviewer.boot()
    print(f"  {b_boot['agent_id']} ready — {b_boot['capabilities']['tools']}")
    print(f"  {r_boot['agent_id']} ready — {r_boot['capabilities']['tools']}")
    print()

    # Handoff
    print("── L4: Handoff Protocol ──")
    task = {"task_id": "task-001", "description": "Build API endpoint",
            "tool": "file", "data_classification": "internal",
            "checklist": ["Tests pass", "No secrets in code"]}
    result = reviewer.receive_task(task)
    print(f"  {reviewer.agent_id} received task: {result['status']}")
    print(f"  TxID: {result.get('result', {}).get('tx_id', '')}")
    print()

    # Coordination
    print("── L5: Coordination Protocol ──")
    fleet = builder.join_fleet([reviewer.agent_id])
    print(f"  {builder.agent_id} fleet: {fleet['role']} (term {fleet['term']})")

    # Assign work via leader
    task_id = builder.coord.assign_work(reviewer.agent_id,
        {"description": "Review PR #42", "tool": "terminal", "data_classification": "internal"})
    print(f"  {builder.agent_id} assigned {task_id} to {reviewer.agent_id}")
    print()

    # Execute with compliance
    print("── L6-L7: Execute + Governance ──")
    # Safe task
    result = builder.execute({"description": "Run unit tests", "tool": "terminal",
                              "data_classification": "internal"})
    print(f"  Safe task: {result['status']}")

    # Blocked task
    result = builder.execute({"description": "Process patient data", "tool": "file",
                              "data_classification": "patient_identifiable"})
    print(f"  Blocked task: {result['status']} — {result.get('violations', [])}")
    print()

    # Audit trail
    print("── L7: Audit Trail ──")
    for entry in builder.ledger.audit():
        print(f"  [{entry['status']}] {entry['intent']}")
    print()

    # Reports
    print("── Agent Reports ──")
    for agent in [builder, reviewer]:
        r = agent.report()
        print(f"  {r['agent_id']}: {r['tasks_done']} done, {r['tasks_failed']} failed, "
              f"{len(agent._handoff_queue)} handoffs")

    print()
    print("=" * 60)
    print("  Demo complete. 7 layers, 2 agents, 0 external deps.")
    print("  pip install workswithagents  →  full SDK with 12 protocols")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vanilla Agent — OSI Reference Implementation")
    parser.add_argument("--name", default="agent", help="Agent name")
    parser.add_argument("--purpose", default="general-purpose", help="Agent purpose")
    parser.add_argument("--tools", default="terminal,file", help="Comma-separated tools")
    parser.add_argument("--demo", action="store_true", help="Run full 7-layer demo")
    args = parser.parse_args()

    if args.demo:
        demo()
    else:
        agent = VanillaAgent(
            name=args.name,
            purpose=args.purpose,
            tools=[t.strip() for t in args.tools.split(",")],
        )
        def handle(sig, frame):
            agent.stop()
            sys.exit(0)
        signal.signal(signal.SIGINT, handle)
        signal.signal(signal.SIGTERM, handle)
        agent.start()
