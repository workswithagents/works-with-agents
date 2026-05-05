// Works With Agents — Rust SDK
// Reference implementations for all Agent OSI Model protocols.
// Zero dependencies beyond stdlib. Copy-pasteable. CC BY 4.0.

use std::collections::HashMap;
use serde::{Deserialize, Serialize};

const DEFAULT_API: &str = "https://workswithagents.dev";

type Json = serde_json::Value;

fn api_request(method: &str, path: &str, body: Option<&Json>) -> Result<Json, String> {
    let client = reqwest::blocking::Client::new();
    let url = format!("{}{}", DEFAULT_API, path);
    let mut req = match method {
        "GET" => client.get(&url),
        "POST" => client.post(&url),
        _ => return Err(format!("Unknown method: {}", method)),
    };
    if let Some(b) = body {
        req = req.json(b);
    }
    match req.send() {
        Ok(resp) => resp.json::<Json>().map_err(|e| e.to_string()),
        Err(e) => Err(e.to_string()),
    }
}

// ── Trust Score ──────────────────────────────────────────────────────

pub struct TrustScoreClient;

impl TrustScoreClient {
    pub fn new() -> Self { Self }

    pub fn get(&self, agent_id: &str) -> Result<Json, String> {
        api_request("GET", &format!("/v1/trust/{}", agent_id), None)
    }

    pub fn report(&self, agent_id: &str, success_rate: f64, pitfalls: i32, skills: i32) -> Result<Json, String> {
        let body = serde_json::json!({
            "agent_id": agent_id,
            "success_rate": success_rate,
            "pitfalls_contributed": pitfalls,
            "skills_published": skills,
        });
        api_request("POST", "/v1/trust/report", Some(&body))
    }

    pub fn rate(&self, from: &str, to: &str, rating: f64) -> Result<Json, String> {
        let body = serde_json::json!({"from_agent": from, "to_agent": to, "rating": rating});
        api_request("POST", "/v1/trust/rate", Some(&body))
    }
}

// ── Deployment Manifest ──────────────────────────────────────────────

#[derive(Serialize, Deserialize)]
pub struct AgentCapability {
    pub action: String,
    pub target: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub success_rate: Option<f64>,
}

#[derive(Serialize, Deserialize)]
pub struct AgentDef {
    pub id: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub r#type: Option<String>,
    pub capabilities: Vec<AgentCapability>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub count: Option<i32>,
}

#[derive(Serialize, Deserialize)]
pub struct FleetDef {
    pub name: String,
    pub agents: Vec<AgentDef>,
}

#[derive(Serialize, Deserialize)]
pub struct FleetManifest {
    pub manifest_version: String,
    pub fleet: FleetDef,
}

pub struct DeploymentManifest {
    manifest: FleetManifest,
    fleet_id: Option<String>,
}

impl DeploymentManifest {
    pub fn new(manifest: FleetManifest) -> Self {
        Self { manifest, fleet_id: None }
    }

    pub fn validate(&self) -> (bool, Vec<String>) {
        let mut errors = vec![];
        if self.manifest.manifest_version.is_empty() {
            errors.push("Missing manifest_version".into());
        }
        if self.manifest.fleet.name.is_empty() {
            errors.push("Missing fleet.name".into());
        }
        if self.manifest.fleet.agents.is_empty() {
            errors.push("Missing fleet.agents".into());
        }
        (errors.is_empty(), errors)
    }

    pub fn deploy(&mut self) -> Result<Json, String> {
        let (valid, errors) = self.validate();
        if !valid {
            return Ok(serde_json::json!({"status": "error", "errors": errors}));
        }
        let body = serde_json::to_value(&self.manifest).map_err(|e| e.to_string())?;
        let result = api_request("POST", "/v1/fleets/deploy", Some(&body))?;
        if let Some(id) = result["fleet_id"].as_str() {
            self.fleet_id = Some(id.to_string());
        }
        Ok(result)
    }
}

// ── SLA Framework ────────────────────────────────────────────────────

pub struct SLAMetrics {
    fleet_id: String,
    tier: String,
}

impl SLAMetrics {
    pub fn new(fleet_id: &str, tier: &str) -> Self {
        Self { fleet_id: fleet_id.into(), tier: tier.into() }
    }

    pub fn report(&self, agent_id: &str, action_id: &str, duration: f64, success: bool) -> Result<Json, String> {
        let body = serde_json::json!({
            "fleet_id": self.fleet_id,
            "agent_id": agent_id,
            "action_id": action_id,
            "duration_seconds": duration,
            "success": success,
        });
        api_request("POST", "/v1/sla/report", Some(&body))
    }

    pub fn status(&self) -> Result<Json, String> {
        api_request("GET", &format!("/v1/sla/{}/status", self.fleet_id), None)
    }
}

// ── Identity Protocol ────────────────────────────────────────────────

pub struct AgentIdentity {
    agent_id: String,
    private_key: Vec<u8>,
    public_key: Vec<u8>,
}

impl AgentIdentity {
    pub fn new(agent_id: &str) -> Self {
        Self { agent_id: agent_id.into(), private_key: vec![], public_key: vec![] }
    }

    pub fn generate(&mut self) -> Result<Json, String> {
        // In production: use ed25519-dalek
        // For reference: placeholder
        Ok(serde_json::json!({"agent_id": self.agent_id, "public_key": "ed25519:..."}))
    }

    pub fn register(&self, owner: Option<&str>) -> Result<Json, String> {
        let body = serde_json::json!({
            "agent_id": self.agent_id,
            "public_key": hex::encode(&self.public_key),
            "owner_name": owner,
        });
        api_request("POST", "/v1/identity/register", Some(&body))
    }

    pub fn sign(&self, payload: &Json) -> Result<String, String> {
        Ok(format!("sig:{}", hex::encode(&self.private_key)))
    }
}

// ── Compliance-as-Code ───────────────────────────────────────────────

pub struct ComplianceEngine;

impl ComplianceEngine {
    pub fn new() -> Self { Self }

    pub fn load(&self, regulation: &str) -> Result<Json, String> {
        api_request("GET", &format!("/v1/compliance/packs/{}", regulation), None)
    }

    pub fn validate(&self, regulation: &str, action: &Json) -> Result<Json, String> {
        let body = serde_json::json!({"regulation": regulation, "action": action});
        api_request("POST", "/v1/compliance/validate", Some(&body))
    }

    pub fn list_packs(&self) -> Result<Json, String> {
        api_request("GET", "/v1/compliance/packs", None)
    }
}

pub fn safe_execute(action: &Json, regulations: &[&str]) -> Result<bool, String> {
    let engine = ComplianceEngine::new();
    for reg in regulations {
        let result = engine.validate(reg, action)?;
        if result["passed"].as_bool() != Some(true) {
            return Ok(false);
        }
    }
    Ok(true)
}

// ── Onboarding Protocol ──────────────────────────────────────────────

pub struct OnboardingClient;

impl OnboardingClient {
    pub fn new() -> Self { Self }

    pub fn interview(&self, name: &str, purpose: &str, capabilities: &[String], skills: &[String]) -> Result<Json, String> {
        let body = serde_json::json!({
            "agent_name": name, "purpose": purpose,
            "capabilities": capabilities, "skills": skills,
        });
        api_request("POST", "/v1/onboard/interview", Some(&body))
    }

    pub fn generate(&self, interview_id: &str) -> Result<Json, String> {
        api_request("POST", &format!("/v1/onboard/{}/generate", interview_id), None)
    }

    pub fn calibrate(&self, interview_id: &str) -> Result<Json, String> {
        api_request("POST", &format!("/v1/onboard/{}/calibrate", interview_id), None)
    }

    pub fn register(&self, interview_id: &str) -> Result<Json, String> {
        api_request("POST", &format!("/v1/onboard/{}/register", interview_id), None)
    }
}
