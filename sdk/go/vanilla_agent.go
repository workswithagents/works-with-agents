// Vanilla Agent — Go reference implementation.
// Full 7-layer OSI Model. Single file. Zero dependencies beyond stdlib.
// Copy, build, run. CC BY 4.0.
//
// Usage: go run vanilla_agent.go --demo

package main

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"flag"
	"fmt"
	"time"

	"crypto/sha256"
	"encoding/hex"
)

// ═══════════════════════════════════════════════════════════════════════
// L2 — Identity Protocol
// ═══════════════════════════════════════════════════════════════════════

type Identity struct {
	AgentID      string
	PublicKeyHex string
}

func NewIdentity(agentID string) *Identity {
	b := make([]byte, 32)
	rand.Read(b)
	h := sha256.Sum256(b)
	return &Identity{AgentID: agentID, PublicKeyHex: hex.EncodeToString(h[:])}
}

func (id *Identity) Sign(payload map[string]interface{}) string {
	j, _ := json.Marshal(payload)
	h := sha256.Sum256(append(j, []byte(id.PublicKeyHex)...))
	return hex.EncodeToString(h[:])
}

// ═══════════════════════════════════════════════════════════════════════
// L4 — Handoff Protocol
// ═══════════════════════════════════════════════════════════════════════

type HandoffPayload struct {
	HandoffID string            `json:"handoff_id"`
	TaskID    string            `json:"task_id"`
	Sender    map[string]string `json:"sender"`
	Context   map[string]interface{} `json:"context"`
}

type HandoffProtocol struct{}

func (h *HandoffProtocol) CreateHandoff(taskID string, id *Identity, task map[string]interface{}, checklist []string) HandoffPayload {
	payload := HandoffPayload{
		HandoffID: fmt.Sprintf("%x", make([]byte,16)),
		TaskID:    taskID,
		Sender:    map[string]string{"agent_id": id.AgentID},
		Context: map[string]interface{}{
			"task_description":  task["description"],
			"state_snapshot":    task["state"],
			"quality_checklist": checklist,
		},
	}
	raw := map[string]interface{}{
		"handoff_id": payload.HandoffID,
		"task_id":    payload.TaskID,
		"sender":     payload.Sender,
	}
	payload.Sender["identity_sig"] = id.Sign(raw)
	return payload
}

func (h *HandoffProtocol) AcceptHandoff(handoff HandoffPayload, id *Identity) map[string]interface{} {
	return map[string]interface{}{
		"status":               "accepted",
		"handoff_id":           handoff.HandoffID,
		"receiver":             id.AgentID,
		"estimated_completion": time.Now().UTC().Format(time.RFC3339),
	}
}

// ═══════════════════════════════════════════════════════════════════════
// L5 — Coordination Protocol
// ═══════════════════════════════════════════════════════════════════════

type AgentRole string

const (
	Leader    AgentRole = "leader"
	Follower  AgentRole = "follower"
	Candidate AgentRole = "candidate"
)

type CoordinationClient struct {
	AgentID   string
	Role      AgentRole
	Term      int
	LeaderID  string
	Peers     []string
	WorkQueue map[string]map[string]interface{}
}

func NewCoordinationClient(agentID string) *CoordinationClient {
	return &CoordinationClient{
		AgentID:   agentID,
		Role:      Follower,
		WorkQueue: make(map[string]map[string]interface{}),
	}
}

func (c *CoordinationClient) StartElection() map[string]interface{} {
	c.Role = Candidate
	c.Term++
	return map[string]interface{}{"type": "elect", "candidate": c.AgentID, "term": c.Term}
}

func (c *CoordinationClient) BecomeLeader() map[string]interface{} {
	c.Role = Leader
	c.LeaderID = c.AgentID
	return map[string]interface{}{"type": "heartbeat", "leader": c.AgentID, "term": c.Term}
}

func (c *CoordinationClient) AssignWork(target string, task map[string]interface{}, priority int) string {
	tid := "task-" + fmt.Sprintf("%x", make([]byte,4))[:8]
	c.WorkQueue[tid] = map[string]interface{}{"target": target, "task": task, "priority": priority, "status": "assigned"}
	return tid
}

func (c *CoordinationClient) GetStatus() map[string]interface{} {
	return map[string]interface{}{"role": c.Role, "leader": c.LeaderID, "term": c.Term, "active_tasks": len(c.WorkQueue)}
}

// ═══════════════════════════════════════════════════════════════════════
// L7 — Transaction Protocol
// ═══════════════════════════════════════════════════════════════════════

type TxStatus string

const (
	TxIntent    TxStatus = "intent"
	TxCompleted TxStatus = "completed"
	TxFailed    TxStatus = "failed"
)

type Transaction struct {
	TxID        string      `json:"tx_id"`
	Intent      string      `json:"intent"`
	AgentID     string      `json:"agent_id"`
	Status      TxStatus    `json:"status"`
	CreatedAt   string      `json:"created_at"`
	CompletedAt string      `json:"completed_at"`
	Result      interface{} `json:"result"`
	Error       string      `json:"error"`
}

type TransactionLedger struct {
	AgentID string
	ledger  map[string]*Transaction
}

func NewTransactionLedger(agentID string) *TransactionLedger {
	return &TransactionLedger{AgentID: agentID, ledger: make(map[string]*Transaction)}
}

func (tl *TransactionLedger) Intent(description string) *Transaction {
	tx := &Transaction{
		TxID:      fmt.Sprintf("%x", make([]byte,16)),
		Intent:    description,
		AgentID:   tl.AgentID,
		Status:    TxIntent,
		CreatedAt: time.Now().UTC().Format(time.RFC3339),
	}
	tl.ledger[tx.TxID] = tx
	return tx
}

func (tl *TransactionLedger) Execute(tx *Transaction, fn func() (interface{}, error)) *Transaction {
	result, err := fn()
	if err != nil {
		tx.Status = TxFailed
		tx.Error = err.Error()
	} else {
		tx.Status = TxCompleted
		tx.Result = result
		tx.CompletedAt = time.Now().UTC().Format(time.RFC3339)
	}
	return tx
}

func (tl *TransactionLedger) Audit() []map[string]interface{} {
	var entries []map[string]interface{}
	for _, tx := range tl.ledger {
		entries = append(entries, map[string]interface{}{
			"id": tx.TxID, "intent": tx.Intent, "status": tx.Status, "error": tx.Error,
		})
	}
	return entries
}

func (tl *TransactionLedger) Stats() map[string]interface{} {
	completed, failed := 0, 0
	for _, tx := range tl.ledger {
		switch tx.Status {
		case TxCompleted:
			completed++
		case TxFailed:
			failed++
		}
	}
	return map[string]interface{}{"total": len(tl.ledger), "completed": completed, "failed": failed}
}

// ═══════════════════════════════════════════════════════════════════════
// L7 — Compliance Gate
// ═══════════════════════════════════════════════════════════════════════

type ComplianceRule struct {
	Field    string
	Operator string
	Value    []string
	Message  string
}

var complianceRules = map[string][]ComplianceRule{
	"nhs_dtac": {
		{Field: "data_classification", Operator: "not_in",
			Value: []string{"patient_identifiable", "clinical_confidential"},
			Message: "Patient data must not be processed without DPIA"},
	},
	"gdpr": {
		{Field: "data_classification", Operator: "not_in",
			Value: []string{"personal_data_unconsented"},
			Message: "Unconsented personal data blocked"},
	},
}

func validateCompliance(regulation string, action map[string]interface{}) map[string]interface{} {
	rules := complianceRules[regulation]
	var violations []string
	for _, rule := range rules {
		actual := fmt.Sprintf("%v", action[rule.Field])
		if rule.Operator == "not_in" {
			for _, v := range rule.Value {
				if actual == v {
					violations = append(violations, rule.Message)
				}
			}
		}
	}
	return map[string]interface{}{"passed": len(violations) == 0, "violations": violations}
}

// ═══════════════════════════════════════════════════════════════════════
// Vanilla Agent
// ═══════════════════════════════════════════════════════════════════════

type VanillaAgent struct {
	Name          string
	Purpose       string
	AgentID       string
	Tools         []string
	StartedAt     string
	Identity      *Identity
	Handoff       *HandoffProtocol
	Coord         *CoordinationClient
	Ledger        *TransactionLedger
	HandoffQueue  []map[string]interface{}
	TasksDone     int
	TasksFailed   int
}

func NewVanillaAgent(name, purpose string, tools []string) *VanillaAgent {
	agentID := fmt.Sprintf("agent-%s-%s", name, "c487aa")
	return &VanillaAgent{
		Name:     name,
		Purpose:  purpose,
		AgentID:  agentID,
		Tools:    tools,
		StartedAt: time.Now().UTC().Format(time.RFC3339),
		Identity: NewIdentity(agentID),
		Handoff:  &HandoffProtocol{},
		Coord:    NewCoordinationClient(agentID),
		Ledger:   NewTransactionLedger(agentID),
	}
}

func (a *VanillaAgent) Boot() map[string]interface{} {
	return map[string]interface{}{
		"agent_id":     a.AgentID,
		"capabilities": map[string]interface{}{"name": a.Name, "purpose": a.Purpose, "tools": a.Tools},
		"status":       "ready",
	}
}

func (a *VanillaAgent) ReceiveTask(task map[string]interface{}) map[string]interface{} {
	taskID := fmt.Sprintf("%v", task["task_id"])
	if taskID == "" || taskID == "<nil>" {
		taskID = fmt.Sprintf("%x", make([]byte,16))
	}
	checklist := []string{"Verify output", "Run tests"}
	handoff := a.Handoff.CreateHandoff(taskID, a.Identity, task, checklist)
	response := a.Handoff.AcceptHandoff(handoff, a.Identity)
	a.HandoffQueue = append(a.HandoffQueue, map[string]interface{}{"handoff": handoff, "accepted": response["status"]})
	result := a.Execute(task)
	response["result"] = result
	return response
}

func (a *VanillaAgent) Execute(task map[string]interface{}) map[string]interface{} {
	for _, regulation := range []string{"nhs_dtac", "gdpr"} {
		result := validateCompliance(regulation, task)
		if !result["passed"].(bool) {
			return map[string]interface{}{"status": "blocked", "violations": result["violations"]}
		}
	}

	desc := fmt.Sprintf("%v", task["description"])
	tx := a.Ledger.Intent(desc)

	a.Ledger.Execute(tx, func() (interface{}, error) {
		tool := fmt.Sprintf("%v", task["tool"])
		fmt.Printf("  [%s] Running %s...\n", a.AgentID, tool)
		return map[string]bool{"ok": true}, nil
	})

	if tx.Status == TxCompleted {
		a.TasksDone++
		return map[string]interface{}{"status": "completed", "tx_id": tx.TxID}
	}
	a.TasksFailed++
	return map[string]interface{}{"status": "failed", "error": tx.Error}
}

func (a *VanillaAgent) JoinFleet(peers []string) map[string]interface{} {
	a.Coord.Peers = peers
	a.Coord.StartElection()
	return a.Coord.GetStatus()
}

func (a *VanillaAgent) Report() map[string]interface{} {
	return map[string]interface{}{
		"agent_id":           a.AgentID,
		"name":               a.Name,
		"purpose":            a.Purpose,
		"tools":              a.Tools,
		"tasks_done":         a.TasksDone,
		"tasks_failed":       a.TasksFailed,
		"handoffs_received":  len(a.HandoffQueue),
		"coordination":       a.Coord.GetStatus(),
		"audit":              a.Ledger.Stats(),
	}
}

// ═══════════════════════════════════════════════════════════════════════
// Demo
// ═══════════════════════════════════════════════════════════════════════

func main() {
	demoFlag := flag.Bool("demo", false, "Run full 7-layer demo")
	flag.Parse()

	if !*demoFlag {
		fmt.Println("Vanilla Agent — Go. Use --demo for the full OSI demo.")
		return
	}

	fmt.Println(strings.Repeat("=", 60))
	fmt.Println("  Vanilla Agent — OSI Reference (Go)")
	fmt.Println("  Works With Agents · CC BY 4.0")
	fmt.Println(strings.Repeat("=", 60))
	fmt.Println()

	builder := NewVanillaAgent("builder", "build software", []string{"terminal", "file", "git"})
	reviewer := NewVanillaAgent("reviewer", "review code", []string{"terminal", "file", "web"})

	fmt.Println("── L1-L3: Boot, Identity, Capabilities ──")
	fmt.Printf("  %s ready\n", builder.Boot()["agent_id"])
	fmt.Printf("  %s ready\n\n", reviewer.Boot()["agent_id"])

	fmt.Println("── L4: Handoff Protocol ──")
	result := reviewer.ReceiveTask(map[string]interface{}{
		"task_id": "task-001", "description": "Build API endpoint",
		"tool": "file", "data_classification": "internal",
	})
	fmt.Printf("  %s received: %v\n\n", reviewer.AgentID, result["status"])

	fmt.Println("── L5: Coordination Protocol ──")
	fleet := builder.JoinFleet([]string{reviewer.AgentID})
	fmt.Printf("  %s fleet: %v (term %v)\n", builder.AgentID, fleet["role"], fleet["term"])
	builder.Coord.AssignWork(reviewer.AgentID, map[string]interface{}{"description": "Review PR", "tool": "terminal"}, 5)
	fmt.Printf("  %s assigned work to %s\n\n", builder.AgentID, reviewer.AgentID)

	fmt.Println("── L6-L7: Execute + Governance ──")
	safe := builder.Execute(map[string]interface{}{"description": "Run tests", "tool": "terminal", "data_classification": "internal"})
	fmt.Printf("  Safe task: %v\n", safe["status"])
	blocked := builder.Execute(map[string]interface{}{"description": "Process patient data", "tool": "file", "data_classification": "patient_identifiable"})
	fmt.Printf("  Blocked: %v\n\n", blocked["status"])

	fmt.Println("── L7: Audit Trail ──")
	for _, entry := range builder.Ledger.Audit() {
		fmt.Printf("  [%v] %v\n", entry["status"], entry["intent"])
	}
	fmt.Println()

	fmt.Println("── Reports ──")
	for _, agent := range []*VanillaAgent{builder, reviewer} {
		r := agent.Report()
		fmt.Printf("  %v: %v done, %v failed\n", r["agent_id"], r["tasks_done"], r["tasks_failed"])
	}
	fmt.Println()
	fmt.Println(strings.Repeat("=", 60))
	fmt.Println("  Demo complete. 7 layers, 2 agents, 0 external deps.")
	fmt.Println(strings.Repeat("=", 60))
}
