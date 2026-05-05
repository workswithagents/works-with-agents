#!/usr/bin/env bash
# Works With Agents — Shell SDK
# Curl wrapper functions for all Agent OSI Model protocols.
# Zero dependencies. Source this file. CC BY 4.0.
#
# Usage: source workswithagents.sh

WWA_API="${WWA_API:-https://workswithagents.dev}"

_wwa_req() {
  local method="$1" path="$2" data="$3"
  if [ -n "$data" ]; then
    curl -s -X "$method" "$WWA_API$path" \
      -H "Content-Type: application/json" \
      -d "$data"
  else
    curl -s -X "$method" "$WWA_API$path" \
      -H "Content-Type: application/json"
  fi
}

# ── Trust Score ──────────────────────────────────────────────────────

wwa_trust_get() {
  _wwa_req GET "/v1/trust/$1"
}

wwa_trust_report() {
  # wwa_trust_report <agent_id> <success_rate> [pitfalls] [skills]
  local agent_id="$1" success_rate="$2" pitfalls="${3:-0}" skills="${4:-0}"
  _wwa_req POST "/v1/trust/report" \
    "{\"agent_id\":\"$agent_id\",\"success_rate\":$success_rate,\"pitfalls_contributed\":$pitfalls,\"skills_published\":$skills}"
}

wwa_trust_rate() {
  _wwa_req POST "/v1/trust/rate" \
    "{\"from_agent\":\"$1\",\"to_agent\":\"$2\",\"rating\":$3}"
}

wwa_trust_list() {
  _wwa_req GET "/v1/trust?tier=trusted"
}

# ── Deployment Manifest ──────────────────────────────────────────────

wwa_fleet_deploy() {
  # wwa_fleet_deploy <manifest.yaml|manifest.json>
  local file="$1"
  if [[ "$file" == *.yaml || "$file" == *.yml ]]; then
    # Convert YAML to JSON using Python (available on most systems)
    python3 -c "import json,yaml;print(json.dumps(yaml.safe_load(open('$file'))))" 2>/dev/null | \
      _wwa_req POST "/v1/fleets/deploy" "$(cat)"
  else
    _wwa_req POST "/v1/fleets/deploy" "$(cat "$file")"
  fi
}

wwa_fleet_status() {
  _wwa_req GET "/v1/fleets/$1/status"
}

# ── SLA Framework ────────────────────────────────────────────────────

wwa_sla_report() {
  # wwa_sla_report <fleet_id> <agent_id> <action_id> <duration_seconds> <success>
  _wwa_req POST "/v1/sla/report" \
    "{\"fleet_id\":\"$1\",\"agent_id\":\"$2\",\"action_id\":\"$3\",\"duration_seconds\":$4,\"success\":$5}"
}

wwa_sla_status() {
  _wwa_req GET "/v1/sla/$1/status"
}

# ── Identity Protocol ────────────────────────────────────────────────

wwa_identity_register() {
  _wwa_req POST "/v1/identity/register" \
    "{\"agent_id\":\"$1\",\"public_key\":\"$2\"}"
}

wwa_identity_verify() {
  _wwa_req POST "/v1/identity/verify" \
    "{\"agent_id\":\"$1\",\"message\":$2,\"signature\":\"$3\"}"
}

wwa_identity_revoke() {
  _wwa_req POST "/v1/identity/$1/revoke" "{\"reason\":\"${2:-manual}\"}"
}

# ── Compliance-as-Code ───────────────────────────────────────────────

wwa_compliance_validate() {
  # wwa_compliance_validate <regulation> <action_json>
  _wwa_req POST "/v1/compliance/validate" \
    "{\"regulation\":\"$1\",\"action\":$2}"
}

wwa_compliance_packs() {
  _wwa_req GET "/v1/compliance/packs"
}

# ── Onboarding ───────────────────────────────────────────────────────

wwa_onboard_interview() {
  # wwa_onboard_interview <name> <purpose> <capabilities_json_array>
  _wwa_req POST "/v1/onboard/interview" \
    "{\"agent_name\":\"$1\",\"purpose\":\"$2\",\"capabilities\":$3}"
}

wwa_onboard_generate() {
  _wwa_req POST "/v1/onboard/$1/generate"
}

wwa_onboard_calibrate() {
  _wwa_req POST "/v1/onboard/$1/calibrate"
}

wwa_onboard_register() {
  _wwa_req POST "/v1/onboard/$1/register"
}

# ── Health ────────────────────────────────────────────────────────────

wwa_health() {
  _wwa_req GET "/v1/health"
}

echo "Works With Agents Shell SDK loaded. Try: wwa_health"
