/**
 * Coordination Protocol — Layer 5 (TypeScript)
 * Leader election, work distribution, conflict resolution, liveness checking.
 * Reference implementation. CC BY 4.0.
 */

export enum AgentRole {
  LEADER = "leader",
  FOLLOWER = "follower",
  CANDIDATE = "candidate",
}

export interface CoordinationMessage {
  message_id: string;
  sender_id: string;
  message_type: "elect" | "heartbeat" | "assign" | "conflict" | "ack";
  payload: Record<string, unknown>;
  timestamp: string;
  term: number;
}

export class CoordinationClient {
  agent_id: string;
  role: AgentRole = AgentRole.FOLLOWER;
  term = 0;
  leader_id: string | null = null;
  peers: string[] = [];
  private workQueue: Map<string, Record<string, unknown>> = new Map();
  private conflictLog: Map<string, Record<string, unknown>> = new Map();

  constructor(agent_id: string, peers: string[] = []) {
    this.agent_id = agent_id;
    this.peers = peers;
  }

  startElection(): CoordinationMessage {
    this.role = AgentRole.CANDIDATE;
    this.term += 1;
    return {
      message_id: crypto.randomUUID(),
      sender_id: this.agent_id,
      message_type: "elect",
      payload: { candidate: this.agent_id, term: this.term },
      timestamp: new Date().toISOString(),
      term: this.term,
    };
  }

  becomeLeader(): CoordinationMessage {
    this.role = AgentRole.LEADER;
    this.leader_id = this.agent_id;
    return {
      message_id: crypto.randomUUID(),
      sender_id: this.agent_id,
      message_type: "heartbeat",
      payload: { leader: this.agent_id, term: this.term, peers: this.peers },
      timestamp: new Date().toISOString(),
      term: this.term,
    };
  }

  follow(leader_id: string, term: number): void {
    this.role = AgentRole.FOLLOWER;
    this.leader_id = leader_id;
    this.term = term;
  }

  assignWork(target_agent: string, task: Record<string, unknown>,
             priority = 5): CoordinationMessage {
    if (this.role !== AgentRole.LEADER) {
      throw new Error(`Cannot assign work as ${this.role}`);
    }
    const task_id = `task-${crypto.randomUUID()}`;
    this.workQueue.set(task_id, {
      assigned_to: target_agent,
      task,
      priority,
      status: "assigned",
    });
    return {
      message_id: crypto.randomUUID(),
      sender_id: this.agent_id,
      message_type: "assign",
      payload: { task_id, target: target_agent, task, priority },
      timestamp: new Date().toISOString(),
      term: this.term,
    };
  }

  resolveConflict(conflict_id: string, decision: Record<string, unknown>): CoordinationMessage {
    this.conflictLog.set(conflict_id, {
      decision,
      resolved_by: this.agent_id,
      resolved_at: new Date().toISOString(),
    });
    return {
      message_id: crypto.randomUUID(),
      sender_id: this.agent_id,
      message_type: "conflict",
      payload: { conflict_id, decision, resolved_by: this.agent_id },
      timestamp: new Date().toISOString(),
      term: this.term,
    };
  }

  heartbeat(): CoordinationMessage {
    return {
      message_id: crypto.randomUUID(),
      sender_id: this.agent_id,
      message_type: "heartbeat",
      payload: {
        status: this.role,
        leader: this.leader_id,
        active_tasks: this.workQueue.size,
      },
      timestamp: new Date().toISOString(),
      term: this.term,
    };
  }

  isLeader(): boolean { return this.role === AgentRole.LEADER; }

  getWorkStatus(): Record<string, unknown> {
    return {
      role: this.role,
      leader: this.leader_id,
      term: this.term,
      active_tasks: this.workQueue.size,
      conflicts_resolved: this.conflictLog.size,
      peers: this.peers,
    };
  }
}
