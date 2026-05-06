//! Vanilla Agent — Rust reference implementation.
//! Full 7-layer OSI Model. Single file. Zero dependencies beyond stdlib.
//! Copy, build, run. CC BY 4.0.
//!
//! Usage: cargo run -- --demo

use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};
use sha2::{Sha256, Digest};

// ═══════════════════════════════════════════════════════════════════════
// Helpers
// ═══════════════════════════════════════════════════════════════════════

fn rand_hex(n: usize) -> String {
    let mut buf = vec![0u8; n];
    getrandom::getrandom(&mut buf).ok();
    hex::encode(Sha256::digest(&buf)).chars().take(n * 2).collect()
}

fn sha256_hex(data: &str) -> String {
    hex::encode(Sha256::digest(data.as_bytes()))
}

fn now_iso() -> String {
    SystemTime::now().duration_since(UNIX_EPOCH).map(|d| {
        chrono::DateTime::from_timestamp(d.as_secs() as i64, 0)
            .map(|t| t.to_rfc3339())
    }).ok().flatten().unwrap_or_default()
}

// ═══════════════════════════════════════════════════════════════════════
// L2 — Identity Protocol
// ═══════════════════════════════════════════════════════════════════════

struct AgentIdentity {
    agent_id: String,
    public_key_hex: String,
}

impl AgentIdentity {
    fn new(agent_id: &str) -> Self {
        Self { agent_id: agent_id.to_string(), public_key_hex: rand_hex(32) }
    }

    fn sign(&self, payload: &str) -> String {
        sha256_hex(&format!("{}{}", payload, self.public_key_hex))
    }
}

// ═══════════════════════════════════════════════════════════════════════
// L4 — Handoff Protocol
// ═══════════════════════════════════════════════════════════════════════

struct HandoffProtocol;

impl HandoffProtocol {
    fn create_handoff(&self, task_id: &str, sender: &AgentIdentity, task: &HashMap<String, String>) -> HashMap<String, String> {
        let mut payload = HashMap::new();
        payload.insert("handoff_id".into(), format!("ho-{}", rand_hex(4)));
        payload.insert("task_id".into(), task_id.into());
        payload.insert("sender_id".into(), sender.agent_id.clone());
        let sig = sender.sign(&format!("{}:{}", task_id, sender.agent_id));
        payload.insert("identity_sig".into(), sig);
        payload
    }

    fn accept_handoff(&self, handoff: &HashMap<String, String>, receiver: &AgentIdentity) -> HashMap<String, String> {
        let mut resp = HashMap::new();
        resp.insert("status".into(), "accepted".into());
        resp.insert("handoff_id".into(), handoff.get("handoff_id").cloned().unwrap_or_default());
        resp.insert("receiver".into(), receiver.agent_id.clone());
        resp
    }
}

// ═══════════════════════════════════════════════════════════════════════
// L5 — Coordination Protocol
// ═══════════════════════════════════════════════════════════════════════

#[derive(PartialEq)]
enum AgentRole { Leader, Follower, Candidate }

struct CoordinationClient {
    agent_id: String,
    role: AgentRole,
    term: u32,
    leader_id: Option<String>,
    peers: Vec<String>,
}

impl CoordinationClient {
    fn new(agent_id: &str) -> Self {
        Self { agent_id: agent_id.into(), role: AgentRole::Follower, term: 0, leader_id: None, peers: vec![] }
    }

    fn start_election(&mut self) -> HashMap<String, String> {
        self.role = AgentRole::Candidate;
        self.term += 1;
        let mut m = HashMap::new();
        m.insert("type".into(), "elect".into());
        m.insert("candidate".into(), self.agent_id.clone());
        m.insert("term".into(), self.term.to_string());
        m
    }

    fn become_leader(&mut self) -> HashMap<String, String> {
        self.role = AgentRole::Leader;
        self.leader_id = Some(self.agent_id.clone());
        let mut m = HashMap::new();
        m.insert("type".into(), "heartbeat".into());
        m.insert("leader".into(), self.agent_id.clone());
        m.insert("term".into(), self.term.to_string());
        m
    }

    fn get_status(&self) -> HashMap<String, String> {
        let mut m = HashMap::new();
        let role_str = match self.role { AgentRole::Leader => "leader", AgentRole::Follower => "follower", AgentRole::Candidate => "candidate" };
        m.insert("role".into(), role_str.into());
        m.insert("leader".into(), self.leader_id.clone().unwrap_or_default());
        m.insert("term".into(), self.term.to_string());
        m
    }
}

// ═══════════════════════════════════════════════════════════════════════
// L7 — Transaction Protocol
// ═══════════════════════════════════════════════════════════════════════

#[derive(Clone, PartialEq)]
enum TxStatus { Intent, Completed, Failed }

struct Transaction {
    tx_id: String,
    intent: String,
    agent_id: String,
    status: TxStatus,
    error: Option<String>,
}

struct TransactionLedger {
    agent_id: String,
    ledger: Vec<Transaction>,
}

impl TransactionLedger {
    fn new(agent_id: &str) -> Self { Self { agent_id: agent_id.into(), ledger: vec![] } }

    fn intent(&mut self, description: &str) -> usize {
        let idx = self.ledger.len();
        self.ledger.push(Transaction {
            tx_id: format!("tx-{}", rand_hex(4)),
            intent: description.into(),
            agent_id: self.agent_id.clone(),
            status: TxStatus::Intent,
            error: None,
        });
        idx
    }

    fn execute(&mut self, idx: usize, ok: bool, err: Option<String>) {
        if let Some(tx) = self.ledger.get_mut(idx) {
            tx.status = if ok { TxStatus::Completed } else { TxStatus::Failed };
            tx.error = err;
        }
    }

    fn stats(&self) -> HashMap<String, usize> {
        let mut m = HashMap::new();
        m.insert("total".into(), self.ledger.len());
        m.insert("completed".into(), self.ledger.iter().filter(|t| t.status == TxStatus::Completed).count());
        m.insert("failed".into(), self.ledger.iter().filter(|t| t.status == TxStatus::Failed).count());
        m
    }
}

// ═══════════════════════════════════════════════════════════════════════
// L7 — Compliance Gate
// ═══════════════════════════════════════════════════════════════════════

fn compliance_check(regulation: &str, classification: &str) -> Option<String> {
    match (regulation, classification) {
        ("nhs_dtac", "patient_identifiable") | ("nhs_dtac", "clinical_confidential") =>
            Some("Patient data must not be processed without DPIA".into()),
        ("gdpr", "personal_data_unconsented") =>
            Some("Unconsented personal data blocked".into()),
        _ => None,
    }
}

// ═══════════════════════════════════════════════════════════════════════
// Vanilla Agent
// ═══════════════════════════════════════════════════════════════════════

struct VanillaAgent {
    name: String,
    purpose: String,
    agent_id: String,
    tools: Vec<String>,
    identity: AgentIdentity,
    handoff: HandoffProtocol,
    coord: CoordinationClient,
    ledger: TransactionLedger,
    tasks_done: u32,
    tasks_failed: u32,
}

impl VanillaAgent {
    fn new(name: &str, purpose: &str, tools: Vec<&str>) -> Self {
        let agent_id = format!("agent-{}-{}", name, rand_hex(3));
        Self {
            name: name.into(), purpose: purpose.into(),
            tools: tools.iter().map(|s| s.to_string()).collect(),
            identity: AgentIdentity::new(&agent_id),
            handoff: HandoffProtocol,
            coord: CoordinationClient::new(&agent_id),
            ledger: TransactionLedger::new(&agent_id),
            agent_id, tasks_done: 0, tasks_failed: 0,
        }
    }

    fn boot(&self) {
        println!("  {} ready — {:?}", self.agent_id, self.tools);
    }

    fn execute(&mut self, description: &str, tool: &str, classification: &str) {
        for regulation in &["nhs_dtac", "gdpr"] {
            if let Some(violation) = compliance_check(regulation, classification) {
                let idx = self.ledger.intent(description);
                self.ledger.execute(idx, false, Some(violation));
                println!("  BLOCKED: {}", description);
                self.tasks_failed += 1;
                return;
            }
        }

        let idx = self.ledger.intent(description);
        println!("  [{}] Running {}...", self.agent_id, tool);
        self.ledger.execute(idx, true, None);
        self.tasks_done += 1;
    }

    fn report(&self) {
        println!("  {}: {} done, {} failed, {:?}",
            self.agent_id, self.tasks_done, self.tasks_failed, self.ledger.stats());
    }
}

// ═══════════════════════════════════════════════════════════════════════
// Demo
// ═══════════════════════════════════════════════════════════════════════

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if !args.contains(&"--demo".to_string()) {
        println!("Vanilla Agent — Rust. Use --demo for the OSI demo.");
        return;
    }

    println!("{}", "═".repeat(60));
    println!("  Vanilla Agent — OSI Reference (Rust)");
    println!("  Works With Agents · CC BY 4.0");
    println!("{}", "═".repeat(60));
    println!();

    let mut builder = VanillaAgent::new("builder", "build software", vec!["terminal", "file", "git"]);
    let mut reviewer = VanillaAgent::new("reviewer", "review code", vec!["terminal", "file", "web"]);

    println!("── L1-L3: Boot ──");
    builder.boot();
    reviewer.boot();
    println!();

    println!("── L4: Handoff ──");
    let mut task = HashMap::new();
    task.insert("description".into(), "Build API endpoint".into());
    let handoff = builder.handoff.create_handoff("task-001", &builder.identity, &task);
    let accept = builder.handoff.accept_handoff(&handoff, &reviewer.identity);
    println!("  Handoff: {}", accept.get("status").unwrap_or(&"unknown".into()));
    println!();

    println!("── L5: Coordination ──");
    let election = builder.coord.start_election();
    println!("  {}: election term {}", builder.agent_id, election.get("term").unwrap_or(&"0".into()));
    builder.coord.become_leader();
    println!("  {} became leader", builder.agent_id);
    println!();

    println!("── L6-L7: Execute + Governance ──");
    builder.execute("Run unit tests", "terminal", "internal");
    builder.execute("Process patient data", "file", "patient_identifiable");
    println!();

    println!("── L7: Audit Trail ──");
    for tx in &builder.ledger.ledger {
        let status = match tx.status { TxStatus::Completed => "completed", TxStatus::Failed => "failed", TxStatus::Intent => "intent" };
        let err = tx.error.as_deref().unwrap_or("");
        println!("  [{}] {} {}", status, tx.intent, if err.is_empty() { "" } else { err });
    }
    println!();

    println!("── Reports ──");
    builder.report();
    reviewer.report();
    println!();
    println!("{}", "═".repeat(60));
    println!("  Demo complete. 7 layers, 2 agents.");
    println!("{}", "═".repeat(60));
}
