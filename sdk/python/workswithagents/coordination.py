"""
Coordination Protocol — Layer 5
Leader election, work distribution, conflict resolution, liveness checking.
Reference implementation. CC BY 4.0.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4


class AgentRole(Enum):
    LEADER = "leader"
    FOLLOWER = "follower"
    CANDIDATE = "candidate"


@dataclass
class CoordinationMessage:
    """A coordination message between agents in a fleet."""
    message_id: str = field(default_factory=lambda: str(uuid4()))
    sender_id: str = ""
    message_type: str = ""  # elect, heartbeat, assign, conflict, ack
    payload: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    term: int = 0  # Leader election term


class CoordinationClient:
    """
    Reference client for the Agent Coordination Protocol.
    Handles leader election, work distribution, conflict resolution, and liveness.

    Usage:
        coord = CoordinationClient(agent_id="builder-01")
        coord.start_election()  # Become leader or follow
        coord.assign_work("compiler-agent", {"task": "build release"})
        coord.resolve_conflict("disagree-1", decision={"action": "retry"})
    """

    def __init__(self, agent_id: str, peers: Optional[list[str]] = None):
        self.agent_id = agent_id
        self.role = AgentRole.FOLLOWER
        self.term = 0
        self.leader_id: Optional[str] = None
        self.peers: list[str] = peers or []
        self._work_queue: dict[str, dict] = {}
        self._conflict_log: dict[str, dict] = {}

    def start_election(self) -> CoordinationMessage:
        """Begin leader election. If no leader exists, become candidate."""
        self.role = AgentRole.CANDIDATE
        self.term += 1
        return CoordinationMessage(
            sender_id=self.agent_id,
            message_type="elect",
            payload={"candidate": self.agent_id, "term": self.term},
            term=self.term,
        )

    def become_leader(self) -> CoordinationMessage:
        """Assume leadership role."""
        self.role = AgentRole.LEADER
        self.leader_id = self.agent_id
        return CoordinationMessage(
            sender_id=self.agent_id,
            message_type="heartbeat",
            payload={"leader": self.agent_id, "term": self.term, "peers": self.peers},
            term=self.term,
        )

    def follow(self, leader_id: str, term: int) -> None:
        """Accept a leader and become follower."""
        self.role = AgentRole.FOLLOWER
        self.leader_id = leader_id
        self.term = term

    def assign_work(self, target_agent: str, task: dict,
                    priority: int = 5) -> CoordinationMessage:
        """Distribute work to a target agent. Must be leader."""
        if self.role != AgentRole.LEADER:
            raise ValueError(f"Cannot assign work as {self.role.value}")
        task_id = f"task-{uuid4()}"
        self._work_queue[task_id] = {
            "assigned_to": target_agent,
            "task": task,
            "priority": priority,
            "status": "assigned",
        }
        return CoordinationMessage(
            sender_id=self.agent_id,
            message_type="assign",
            payload={
                "task_id": task_id,
                "target": target_agent,
                "task": task,
                "priority": priority,
            },
            term=self.term,
        )

    def resolve_conflict(self, conflict_id: str, decision: dict) -> CoordinationMessage:
        """Resolve a conflict between agents. Must be leader."""
        self._conflict_log[conflict_id] = {
            "decision": decision,
            "resolved_by": self.agent_id,
            "resolved_at": datetime.now(timezone.utc).isoformat(),
        }
        return CoordinationMessage(
            sender_id=self.agent_id,
            message_type="conflict",
            payload={
                "conflict_id": conflict_id,
                "decision": decision,
                "resolved_by": self.agent_id,
            },
            term=self.term,
        )

    def heartbeat(self) -> CoordinationMessage:
        """Send a liveness heartbeat."""
        return CoordinationMessage(
            sender_id=self.agent_id,
            message_type="heartbeat",
            payload={
                "status": self.role.value,
                "leader": self.leader_id,
                "active_tasks": len(self._work_queue),
            },
            term=self.term,
        )

    def is_leader(self) -> bool:
        return self.role == AgentRole.LEADER

    def get_work_status(self) -> dict:
        """Get current work distribution status."""
        return {
            "role": self.role.value,
            "leader": self.leader_id,
            "term": self.term,
            "active_tasks": len(self._work_queue),
            "conflicts_resolved": len(self._conflict_log),
            "peers": self.peers,
        }
