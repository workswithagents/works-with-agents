#!/usr/bin/env python3.11
"""Compliance Proxy — real-time validation of agent actions against regulations.

Standalone HTTP service. Sits between agents and their tools.
Validates every action against NHS DTAC, GDPR, FCA, or custom regulation packs.

Usage:
    python3.11 compliance-proxy.py --port 8496
    curl -X POST localhost:8496/v1/validate -H "Content-Type: application/json" \\
      -d '{"action":{"verb":"read","resource":"patient-data.csv","agent":"builder-01"}}'

Returns: {"passed": true} or {"passed": false, "violations": ["DTAC.1: Missing Caldicott Guardian approval"]}
"""

import argparse
import json
import os
import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

# ─── Regulation Packs ────────────────────────────────────────────────────

class RegulationPack:
    """A set of compliance rules for one regulation."""
    
    def __init__(self, name: str, rules: list):
        self.name = name
        self.rules = rules
    
    def validate(self, action: dict) -> list[str]:
        """Validate an action against this regulation. Returns violations."""
        violations = []
        for rule in self.rules:
            if not self._triggered(rule, action):
                continue
            for check in rule.get("validation", []):
                val = self._get_field(action, check["field"])
                if not self._evaluate(val, check["operator"], check.get("value")):
                    violations.append(f"{rule['id']}: {check['message']}")
        return violations
    
    def _triggered(self, rule: dict, action: dict) -> bool:
        trigger = rule.get("trigger", {})
        if not trigger:
            return True
        events = trigger.get("events", [])
        if events and action.get("verb") not in events:
            return False
        classifications = trigger.get("data_classification", [])
        if classifications:
            data_class = action.get("data_classification", "internal")
            if data_class not in classifications:
                return False
        return True
    
    def _get_field(self, obj: dict, field: str):
        parts = field.split(".")
        val = obj
        for p in parts:
            if isinstance(val, dict):
                val = val.get(p)
            else:
                return None
        return val
    
    def _evaluate(self, actual, operator: str, expected) -> bool:
        if operator == "equals":
            return actual == expected
        if operator == "exists":
            return actual is not None and actual != ""
        if operator == "in":
            return actual in (expected if isinstance(expected, list) else [expected])
        if operator == "not_in":
            return actual not in (expected if isinstance(expected, list) else [expected])
        if operator == "greater_than":
            return (actual or 0) > (expected or 0)
        if operator == "less_than":
            return (actual or 0) < (expected or 0)
        return False


# ─── Built-in Regulation Packs ───────────────────────────────────────────

NHS_DTAC_RULES = [
    {
        "id": "DTAC.CAL-1",
        "name": "Caldicott Guardian approval for patient data",
        "severity": "critical",
        "validation": [
            {"field": "data_classification", "operator": "not_in",
             "value": ["patient_data", "phi"],
             "message": "Patient data access requires Caldicott Guardian approval"}
        ],
        "trigger": {"data_classification": ["patient_data", "phi"]}
    },
    {
        "id": "DTAC.CAL-2",
        "name": "No automated clinical decisions",
        "severity": "critical",
        "validation": [
            {"field": "verb", "operator": "not_in",
             "value": ["diagnose", "prescribe", "triage"],
             "message": "Automated clinical decisions prohibited (DCB 0129)"}
        ]
    },
    {
        "id": "DTAC.TECH-1",
        "name": "Encryption at rest required",
        "severity": "high",
        "validation": [
            {"field": "storage.encrypted", "operator": "equals", "value": True,
             "message": "Data at rest must be encrypted (FileVault/BitLocker)"}
        ],
        "trigger": {"data_classification": ["patient_data", "phi", "sensitive"]}
    },
    {
        "id": "DTAC.AUDIT-1",
        "name": "Audit trail required",
        "severity": "high",
        "validation": [
            {"field": "audit_logged", "operator": "equals", "value": True,
             "message": "All actions must be audit-logged"}
        ]
    }
]

GDPR_RULES = [
    {
        "id": "GDPR.MIN-1",
        "name": "Data minimisation",
        "severity": "high",
        "validation": [
            {"field": "pii_included", "operator": "not_in", "value": [True],
             "message": "Processing PII without lawful basis (Art. 6/9)"}
        ]
    },
    {
        "id": "GDPR.TRANS-1",
        "name": "No international transfers",
        "severity": "critical",
        "validation": [
            {"field": "destination", "operator": "not_in",
             "value": ["external_api", "cloud", "non_eu"],
             "message": "Data transfer outside EU/UK requires adequacy decision (Art. 44)"}
        ]
    },
    {
        "id": "GDPR.RIGHTS-1",
        "name": "Erasure capability",
        "severity": "medium",
        "validation": [
            {"field": "deletable", "operator": "equals", "value": True,
             "message": "Data must be erasable on request (Art. 17)"}
        ],
        "trigger": {"data_classification": ["pii", "personal"]}
    }
]

# ─── FCA (Financial Conduct Authority) Rules ────────────────────────────

FCA_RULES = [
    {
        "id": "FCA.SMR-1",
        "name": "Senior Managers Regime — accountability",
        "severity": "critical",
        "validation": [
            {"field": "accountable_person", "operator": "exists",
             "message": "Every agent action must have an accountable SMF holder (Senior Managers Regime)"}
        ]
    },
    {
        "id": "FCA.CON-1",
        "name": "Consumer Duty — fair outcomes",
        "severity": "high",
        "validation": [
            {"field": "consumer_impact", "operator": "not_in",
             "value": ["adverse", "unfair", "discriminatory"],
             "message": "Agent actions must not produce unfair consumer outcomes (Consumer Duty 2023)"}
        ],
        "trigger": {"events": ["recommend", "price", "deny", "classify"]}
    },
    {
        "id": "FCA.SYG-1",
        "name": "SYSC — systems and controls",
        "severity": "high",
        "validation": [
            {"field": "audit_logged", "operator": "equals", "value": True,
             "message": "All automated decisions must be audit-logged (SYSC 4.1.1)"}
        ],
        "trigger": {"events": ["decide", "approve", "reject", "classify"]}
    },
    {
        "id": "FCA.OPS-1",
        "name": "Operational resilience",
        "severity": "high",
        "validation": [
            {"field": "sla_breach", "operator": "not_in", "value": [True],
             "message": "SLA breaches on important business services must be reported (PS21/3)"}
        ]
    },
]

COMPLIANCE_PACKS = {
    "nhs_dtac": RegulationPack("NHS DTAC", NHS_DTAC_RULES),
    "gdpr": RegulationPack("GDPR", GDPR_RULES),
    "fca": RegulationPack("FCA", FCA_RULES),
}


# ─── HTTP Server ──────────────────────────────────────────────────────────

class ComplianceHandler(BaseHTTPRequestHandler):
    """HTTP handler for the Compliance Proxy."""
    
    packs = COMPLIANCE_PACKS
    
    def log_message(self, format, *args):
        """Log to stderr with timestamp."""
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        print(f"[{ts}] {args[0]}", file=sys.stderr)
    
    def do_GET(self):
        if self.path == "/v1/health":
            self._json(200, {
                "status": "ok",
                "service": "compliance-proxy",
                "packs": list(self.packs.keys()),
                "version": "0.1.0-beta"
            })
        elif self.path == "/v1/packs":
            self._json(200, {
                "packs": {name: {"name": p.name, 
                                 "rules_count": len(p.rules)}
                          for name, p in self.packs.items()}
            })
        elif self.path.startswith("/v1/packs/"):
            pack_name = self.path.split("/")[-1]
            pack = self.packs.get(pack_name)
            if pack:
                self._json(200, {"name": pack.name, "rules": pack.rules})
            else:
                self._json(404, {"error": f"Pack '{pack_name}' not found"})
        else:
            self._json(404, {"error": "Not found"})
    
    def do_POST(self):
        if self.path == "/v1/validate":
            body = self._read_body()
            if not body:
                return
            
            action = body.get("action", {})
            regulations = body.get("regulations", list(self.packs.keys()))
            
            all_violations = []
            for reg_name in regulations:
                pack = self.packs.get(reg_name)
                if not pack:
                    all_violations.append(f"Unknown regulation: {reg_name}")
                    continue
                violations = pack.validate(action)
                all_violations.extend(violations)
            
            passed = len(all_violations) == 0
            result = {
                "passed": passed,
                "action": action.get("verb", "unknown"),
                "regulations_checked": regulations,
                "violations": all_violations,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            self._json(200 if passed else 422, result)
        else:
            self._json(404, {"error": "Not found"})
    
    def _read_body(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            return json.loads(raw)
        except Exception as e:
            self._json(400, {"error": f"Invalid JSON: {e}"})
            return {}
    
    def _json(self, status: int, data: dict):
        body = json.dumps(data, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)


def main():
    parser = argparse.ArgumentParser(description="Compliance Proxy")
    parser.add_argument("--port", "-p", type=int, default=8496,
                        help="Port to listen on (default: 8496)")
    parser.add_argument("--host", default="127.0.0.1",
                        help="Host to bind to (default: 127.0.0.1)")
    args = parser.parse_args()
    
    print(f"Compliance Proxy v0.1.0-beta")
    print(f"  Packs loaded: {', '.join(COMPLIANCE_PACKS.keys())}")
    print(f"  Listening on http://{args.host}:{args.port}")
    print(f"  Health: http://{args.host}:{args.port}/v1/health")
    print(f"  Validate: POST http://{args.host}:{args.port}/v1/validate")
    print()
    
    server = HTTPServer((args.host, args.port), ComplianceHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.", file=sys.stderr)
        server.shutdown()


if __name__ == "__main__":
    main()
