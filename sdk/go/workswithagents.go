// Works With Agents — Go SDK
// Reference implementations for all Agent OSI Model protocols.
// Zero dependencies beyond stdlib. Copy-pasteable. CC BY 4.0.
package workswithagents

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

const DefaultAPI = "https://workswithagents.dev"

func apiRequest(method, path string, body interface{}) (map[string]interface{}, error) {
	var b []byte
	if body != nil {
		var err error
		b, err = json.Marshal(body)
		if err != nil {
			return nil, err
		}
	}
	req, err := http.NewRequest(method, DefaultAPI+path, bytes.NewReader(b))
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", "application/json")
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	data, _ := io.ReadAll(resp.Body)
	var result map[string]interface{}
	json.Unmarshal(data, &result)
	return result, nil
}

// ── Trust Score ──────────────────────────────────────────────────────

type TrustScoreClient struct{}

func NewTrustScoreClient() *TrustScoreClient { return &TrustScoreClient{} }

func (t *TrustScoreClient) Get(agentID string) (map[string]interface{}, error) {
	return apiRequest("GET", "/v1/trust/"+agentID, nil)
}

func (t *TrustScoreClient) Report(agentID string, successRate float64, pitfalls, skills int) (map[string]interface{}, error) {
	return apiRequest("POST", "/v1/trust/report", map[string]interface{}{
		"agent_id":            agentID,
		"success_rate":        successRate,
		"pitfalls_contributed": pitfalls,
		"skills_published":    skills,
	})
}

func (t *TrustScoreClient) Rate(fromAgent, toAgent string, rating float64) (map[string]interface{}, error) {
	return apiRequest("POST", "/v1/trust/rate", map[string]interface{}{
		"from_agent": fromAgent, "to_agent": toAgent, "rating": rating,
	})
}

func (t *TrustScoreClient) ListTrusted() (map[string]interface{}, error) {
	return apiRequest("GET", "/v1/trust?tier=trusted", nil)
}

// ── Deployment Manifest ──────────────────────────────────────────────

type AgentCapability struct {
	Action      string  `json:"action"`
	Target      string  `json:"target"`
	SuccessRate float64 `json:"success_rate,omitempty"`
}

type AgentDef struct {
	ID           string            `json:"id"`
	Type         string            `json:"type,omitempty"`
	Capabilities []AgentCapability `json:"capabilities"`
	Count        int               `json:"count,omitempty"`
	Skills       []string          `json:"skills,omitempty"`
}

type FleetDef struct {
	Name    string     `json:"name"`
	Agents  []AgentDef `json:"agents"`
	Registry string    `json:"registry,omitempty"`
}

type FleetManifest struct {
	Version string   `json:"manifest_version"`
	Fleet   FleetDef `json:"fleet"`
}

type DeploymentManifest struct {
	Manifest FleetManifest
	FleetID  string
}

func NewDeploymentManifest(m FleetManifest) *DeploymentManifest {
	return &DeploymentManifest{Manifest: m}
}

func (d *DeploymentManifest) Validate() (bool, []string) {
	var errors []string
	if d.Manifest.Version == "" {
		errors = append(errors, "Missing manifest_version")
	}
	if d.Manifest.Fleet.Name == "" {
		errors = append(errors, "Missing fleet.name")
	}
	if len(d.Manifest.Fleet.Agents) == 0 {
		errors = append(errors, "Missing fleet.agents")
	}
	return len(errors) == 0, errors
}

func (d *DeploymentManifest) Deploy() (map[string]interface{}, error) {
	valid, errs := d.Validate()
	if !valid {
		return map[string]interface{}{"status": "error", "errors": errs}, nil
	}
	result, err := apiRequest("POST", "/v1/fleets/deploy", d.Manifest)
	if err == nil {
		if id, ok := result["fleet_id"].(string); ok {
			d.FleetID = id
		}
	}
	return result, err
}

func (d *DeploymentManifest) Status() (map[string]interface{}, error) {
	if d.FleetID == "" {
		return map[string]interface{}{"error": "Not deployed"}, nil
	}
	return apiRequest("GET", "/v1/fleets/"+d.FleetID+"/status", nil)
}

// ── SLA Framework ────────────────────────────────────────────────────

type SLAMetrics struct {
	FleetID string
	Tier    string
}

var SLATiers = map[string]map[string]float64{
	"best_effort": {"uptime": 0.95, "accuracy": 0.80},
	"production":  {"uptime": 0.995, "accuracy": 0.90, "latency_p95": 300, "recovery": 0.95},
	"regulated":   {"uptime": 0.999, "accuracy": 0.95, "latency_p99": 120, "compliance": 1.0, "recovery": 0.99},
}

func NewSLAMetrics(fleetID, tier string) *SLAMetrics {
	return &SLAMetrics{FleetID: fleetID, Tier: tier}
}

func (s *SLAMetrics) Report(agentID, actionID string, durationSeconds float64, success bool, guaranteeLevel string) (map[string]interface{}, error) {
	body := map[string]interface{}{
		"fleet_id":         s.FleetID,
		"agent_id":         agentID,
		"action_id":        actionID,
		"duration_seconds": durationSeconds,
		"success":          success,
		"timestamp":        time.Now().Unix(),
	}
	if guaranteeLevel != "" {
		body["guarantee_level"] = guaranteeLevel
	}
	return apiRequest("POST", "/v1/sla/report", body)
}

func (s *SLAMetrics) Status() (map[string]interface{}, error) {
	return apiRequest("GET", "/v1/sla/"+s.FleetID+"/status", nil)
}

// ── Identity Protocol ────────────────────────────────────────────────

type AgentIdentity struct {
	AgentID    string
	PrivateKey []byte
	PublicKey  []byte
}

func NewAgentIdentity(agentID string) *AgentIdentity {
	return &AgentIdentity{AgentID: agentID}
}

func (a *AgentIdentity) Generate() (map[string]interface{}, error) {
	// In production: use crypto/ed25519
	// For reference: placeholder key generation
	return map[string]interface{}{
		"agent_id":   a.AgentID,
		"public_key": fmt.Sprintf("ed25519:%x", a.PublicKey),
	}, nil
}

func (a *AgentIdentity) Register(ownerName, ownerEmail string) (map[string]interface{}, error) {
	body := map[string]interface{}{
		"agent_id":   a.AgentID,
		"public_key": fmt.Sprintf("ed25519:%x", a.PublicKey),
	}
	if ownerName != "" {
		body["owner_name"] = ownerName
	}
	if ownerEmail != "" {
		body["owner_email"] = ownerEmail
	}
	return apiRequest("POST", "/v1/identity/register", body)
}

func (a *AgentIdentity) Sign(payload map[string]interface{}) (string, error) {
	return fmt.Sprintf("sig:%x", a.PrivateKey), nil
}

func (a *AgentIdentity) Rotate() (map[string]interface{}, error) {
	oldPub := fmt.Sprintf("%x", a.PublicKey)
	a.Generate()
	return apiRequest("POST", "/v1/identity/"+a.AgentID+"/rotate", map[string]interface{}{
		"new_public_key": fmt.Sprintf("%x", a.PublicKey),
		"old_public_key": oldPub,
	})
}

// ── Compliance-as-Code ───────────────────────────────────────────────

type ComplianceEngine struct{}

func NewComplianceEngine() *ComplianceEngine { return &ComplianceEngine{} }

func (c *ComplianceEngine) Load(regulation string) (map[string]interface{}, error) {
	return apiRequest("GET", "/v1/compliance/packs/"+regulation, nil)
}

func (c *ComplianceEngine) Validate(regulation string, action map[string]interface{}) (map[string]interface{}, error) {
	return apiRequest("POST", "/v1/compliance/validate", map[string]interface{}{
		"regulation": regulation,
		"action":     action,
	})
}

func (c *ComplianceEngine) ListPacks() (map[string]interface{}, error) {
	return apiRequest("GET", "/v1/compliance/packs", nil)
}

// ── Onboarding Protocol ──────────────────────────────────────────────

type OnboardingClient struct{}

func NewOnboardingClient() *OnboardingClient { return &OnboardingClient{} }

func (o *OnboardingClient) Interview(name, purpose string, capabilities []string, skills []string) (map[string]interface{}, error) {
	return apiRequest("POST", "/v1/onboard/interview", map[string]interface{}{
		"agent_name":   name,
		"purpose":      purpose,
		"capabilities": capabilities,
		"skills":       skills,
	})
}

func (o *OnboardingClient) Generate(interviewID string) (map[string]interface{}, error) {
	return apiRequest("POST", "/v1/onboard/"+interviewID+"/generate", nil)
}

func (o *OnboardingClient) Calibrate(interviewID string) (map[string]interface{}, error) {
	return apiRequest("POST", "/v1/onboard/"+interviewID+"/calibrate", nil)
}

func (o *OnboardingClient) Register(interviewID string) (map[string]interface{}, error) {
	return apiRequest("POST", "/v1/onboard/"+interviewID+"/register", nil)
}

// ── Convenience ──────────────────────────────────────────────────────

func SafeExecute(action map[string]interface{}, regulations []string) (bool, error) {
	engine := NewComplianceEngine()
	for _, reg := range regulations {
		result, err := engine.Validate(reg, action)
		if err != nil {
			return false, err
		}
		if passed, ok := result["passed"].(bool); ok && !passed {
			return false, nil
		}
	}
	return true, nil
}
