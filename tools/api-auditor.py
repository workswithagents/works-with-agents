#!/usr/bin/env python3
"""
API Integrity Auditor — CLI + JSON report generator
Usage:
  python api-auditor.py                          # cloud mode (all 5 domains)
  python api-auditor.py --mode local             # localhost ports
  python api-auditor.py --domain dev             # single domain
  python api-auditor.py --json > report.json     # JSON output
  python api-auditor.py --report audit-$(date +%Y%m%d).json
Works With Agents — https://workswithagents.com
"""

import argparse, json, sys, time, urllib.request, urllib.error, ssl
from datetime import datetime, timezone
from pathlib import Path

VERSION = "1.0.0"

# ── Endpoint Definitions ──────────────────────────────────────────────
ENDPOINTS = {
    "workswithagents.com": {
        "static": True,
        "cloud": "https://workswithagents.com",
        "local": "http://localhost:8484",
        "endpoints": [
            {"method": "GET", "path": "/", "expect": {"status": 200, "content_type": "text/html"}},
            {"method": "GET", "path": "/learn.html", "expect": {"status": 200}},
            {"method": "GET", "path": "/about.html", "expect": {"status": 200}},
            {"method": "GET", "path": "/standards.html", "expect": {"status": 200}},
            {"method": "GET", "path": "/newsletter.html", "expect": {"status": 200}},
            {"method": "GET", "path": "/contact.html", "expect": {"status": 200}},
            {"method": "GET", "path": "/llms.txt", "expect": {"status": 200}},
            {"method": "GET", "path": "/robots.txt", "expect": {"status": 200}},
            {"method": "GET", "path": "/sitemap.xml", "expect": {"status": 200}},
            {"method": "GET", "path": "/404-page-that-should-404", "expect": {"status": 404}},
        ]
    },
    "workswithagents.co.uk": {
        "static": True,
        "cloud": "https://workswithagents.co.uk",
        "local": "http://localhost:8485",
        "endpoints": [
            {"method": "GET", "path": "/", "expect": {"status": 200}},
            {"method": "GET", "path": "/llms.txt", "expect": {"status": 200}},
            {"method": "GET", "path": "/robots.txt", "expect": {"status": 200}},
            {"method": "GET", "path": "/sitemap.xml", "expect": {"status": 200}},
            {"method": "GET", "path": "/learn.html", "expect": {"status": 404}},
        ]
    },
    "workswithagents.dev": {
        "static": False,
        "cloud": "https://workswithagents.dev",
        "local": "http://localhost:8499",
        "endpoints": [
            {"method": "GET", "path": "/v1/health", "expect": {"status": 200}, "validate": "health"},
            {"method": "GET", "path": "/v1/facts", "expect": {"status": 200}, "validate": "facts"},
            {"method": "GET", "path": "/v1/facts/stats", "expect": {"status": 200}, "validate": "object"},
            {"method": "GET", "path": "/v1/skills", "expect": {"status": 200}, "validate": "skills"},
            {"method": "GET", "path": "/v1/pitfalls", "expect": {"status": 200}, "validate": "pitfalls"},
            {"method": "GET", "path": "/llms.txt", "expect": {"status": 200}},
            {"method": "GET", "path": "/llms-full.txt", "expect": {"status": 200}},
            {"method": "GET", "path": "/v1/openapi.json", "expect": {"status": 200}, "validate": "openapi"},
        ]
    },
    "workswithagents.io": {
        "static": False,
        "cloud": "https://workswithagents.io",
        "local": "http://localhost:8500",
        "endpoints": [
            {"method": "GET", "path": "/v1/health", "expect": {"status": 200}, "validate": "health"},
            {"method": "GET", "path": "/v1/blueprints", "expect": {"status": 200}, "validate": "blueprints"},
            {"method": "GET", "path": "/v1/blueprints/version", "expect": {"status": 200}, "validate": "version"},
        ]
    },
    "bastiongateway.com": {
        "static": False,
        "cloud": "https://bastiongateway.com",
        "local": "http://localhost:8498",
        "endpoints": [
            {"method": "GET", "path": "/v1/health", "expect": {"status": 200}, "validate": "health"},
            {"method": "GET", "path": "/v1/fleet/health", "expect": {"status": 200}, "validate": "fleet"},
            {"method": "GET", "path": "/", "expect": {"status": 200}},
        ]
    },
}

# ── Validators ────────────────────────────────────────────────────────
def validate_health(data: dict) -> dict:
    """Check health response has required fields."""
    issues = []
    discoveries = {}
    if "status" not in data:
        issues.append("missing 'status' field")
    elif data["status"] != "ok":
        issues.append(f"status='{data['status']}' (expected 'ok')")
    if "version" in data:
        discoveries["api_version"] = data["version"]
    else:
        issues.append("missing 'version' field")
    if "timestamp" not in data:
        issues.append("missing 'timestamp' field")
    # .io-specific
    if "registry_version" in data:
        discoveries["registry_version"] = data["registry_version"]
    if "registry_updated" in data:
        discoveries["registry_updated"] = data["registry_updated"]
    return {"valid": len(issues) == 0, "issues": issues, "discoveries": discoveries}


def validate_array(data) -> dict:
    if isinstance(data, list):
        return {"valid": True, "issues": [], "discoveries": {"count": len(data)}}
    return {"valid": False, "issues": [f"expected array, got {type(data).__name__}"], "discoveries": {}}


def validate_object(data: dict) -> dict:
    if isinstance(data, dict):
        return {"valid": True, "issues": [], "discoveries": {"keys": list(data.keys())}}
    return {"valid": False, "issues": [f"expected object, got {type(data).__name__}"], "discoveries": {}}


def validate_openapi(data: dict) -> dict:
    issues = []
    if not isinstance(data, dict):
        return {"valid": False, "issues": ["not a JSON object"], "discoveries": {}}
    if "openapi" not in data:
        issues.append("missing 'openapi' version field")
    if "info" not in data:
        issues.append("missing 'info' section")
    elif "version" in data.get("info", {}):
        return {"valid": len(issues) == 0, "issues": issues,
                "discoveries": {"openapi_spec_version": data["openapi"], "spec_info_version": data["info"]["version"]}}
    return {"valid": len(issues) == 0, "issues": issues, "discoveries": {}}


def validate_fleet(data: dict) -> dict:
    if not isinstance(data, dict):
        return {"valid": False, "issues": ["not a JSON object"], "discoveries": {}}
    issues = []
    discoveries = {}
    for key in ["agents", "counts", "timestamp"]:
        if key not in data:
            issues.append(f"missing '{key}' field")
    if "counts" in data:
        discoveries["fleet_counts"] = data["counts"]
    return {"valid": len(issues) == 0, "issues": issues, "discoveries": discoveries}


def validate_version(data: dict) -> dict:
    if not isinstance(data, dict):
        return {"valid": False, "issues": ["not a JSON object"], "discoveries": {}}
    issues = []
    discoveries = {}
    for key in ["version", "count"]:
        if key not in data:
            issues.append(f"missing '{key}' field")
        else:
            discoveries[key] = data[key]
    if "updated" in data:
        discoveries["updated"] = data["updated"]
    return {"valid": len(issues) == 0, "issues": issues, "discoveries": discoveries}


def validate_wrapped(key: str):
    """Factory: validates dict with a specific wrapped array key."""
    def _v(data):
        if not isinstance(data, dict):
            return {"valid": False, "issues": [f"expected object, got {type(data).__name__}"], "discoveries": {}}
        issues = []
        if key not in data:
            issues.append(f"missing '{key}' field")
        elif not isinstance(data[key], list):
            issues.append(f"'{key}' should be array, got {type(data[key]).__name__}")
        else:
            return {"valid": True, "issues": [], "discoveries": {"count": len(data[key])}}
        return {"valid": len(issues) == 0, "issues": issues, "discoveries": {}}
    return _v


VALIDATORS = {
    "health": validate_health,
    "array": validate_array,
    "object": validate_object,
    "openapi": validate_openapi,
    "fleet": validate_fleet,
    "version": validate_version,
    "facts": validate_wrapped("facts"),
    "skills": validate_wrapped("skills"),
    "pitfalls": validate_wrapped("pitfalls"),
    "blueprints": validate_wrapped("blueprints"),
}


# ── HTTP Client ───────────────────────────────────────────────────────
def fetch(method: str, url: str, timeout: int = 15) -> dict:
    """Fetch URL and return status, headers, body, latency."""
    ctx = ssl.create_default_context()
    # Allow localhost self-signed certs in local mode
    if "localhost" in url or "127.0.0.1" in url:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    start = time.monotonic()
    try:
        req = urllib.request.Request(url, method=method)
        req.add_header("User-Agent", f"WWA-API-Auditor/{VERSION}")
        req.add_header("Accept", "application/json, text/html, */*")
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            latency_ms = round((time.monotonic() - start) * 1000)
            body = resp.read().decode("utf-8", errors="replace")
            return {
                "status": resp.status,
                "headers": dict(resp.headers),
                "body": body,
                "latency_ms": latency_ms,
                "error": None,
            }
    except urllib.error.HTTPError as e:
        latency_ms = round((time.monotonic() - start) * 1000)
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return {
            "status": e.code,
            "headers": dict(e.headers) if e.headers else {},
            "body": body,
            "latency_ms": latency_ms,
            "error": f"HTTP {e.code}",
        }
    except Exception as e:
        latency_ms = round((time.monotonic() - start) * 1000)
        return {
            "status": 0,
            "headers": {},
            "body": "",
            "latency_ms": latency_ms,
            "error": str(e),
        }


# ── Core Logic ────────────────────────────────────────────────────────
def audit_domain(domain: str, config: dict, base_url: str) -> list:
    """Audit all endpoints for a domain."""
    results = []
    for ep in config["endpoints"]:
        url = f"{base_url}{ep['path']}"
        resp = fetch(ep["method"], url)

        result = {
            "domain": domain,
            "method": ep["method"],
            "path": ep["path"],
            "url": url,
            "status": resp["status"],
            "latency_ms": resp["latency_ms"],
            "error": resp["error"],
            "passed": False,
            "issues": [],
            "discoveries": {},
        }

        # Status check
        expected_status = ep.get("expect", {}).get("status")
        if expected_status and resp["status"] != expected_status:
            result["issues"].append(
                f"status {resp['status']} (expected {expected_status})"
            )
        elif resp["error"] and resp["status"] != expected_status:
            result["issues"].append(resp["error"])

        # Content-type check
        expected_ct = ep.get("expect", {}).get("content_type")
        if expected_ct:
            ct = resp.get("headers", {}).get("Content-Type", resp.get("headers", {}).get("content-type", ""))
            if expected_ct not in ct:
                result["issues"].append(f"content-type '{ct[:50]}' (expected '{expected_ct}')")

        # JSON validation
        validate_type = ep.get("validate")
        if validate_type and resp["status"] == 200 and not resp["error"]:
            try:
                data = json.loads(resp["body"])
                v = VALIDATORS[validate_type](data)
                result["issues"].extend(v["issues"])
                result["discoveries"] = v["discoveries"]
                if not v["valid"]:
                    result["issues"].append(f"schema validation failed: {validate_type}")
            except json.JSONDecodeError as e:
                result["issues"].append(f"invalid JSON: {e}")

        result["passed"] = len(result["issues"]) == 0
        results.append(result)

    return results


def generate_report(all_results: list, mode: str) -> dict:
    """Generate summary report."""
    total = len(all_results)
    passed = sum(1 for r in all_results if r["passed"])
    failed = total - passed
    domains_audited = list(set(r["domain"] for r in all_results))
    errors = [r for r in all_results if not r["passed"]]

    # Collect versions
    versions = {}
    for r in all_results:
        if "api_version" in r.get("discoveries", {}):
            d = r["domain"]
            v = r["discoveries"]["api_version"]
            if d not in versions:
                versions[d] = v
            elif versions[d] != v:
                versions[d] = f"{versions[d]} / {v} (INCONSISTENT)"

    return {
        "audit_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "auditor_version": VERSION,
        "mode": mode,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_endpoints": total,
            "passed": passed,
            "failed": failed,
            "health": "PASS" if failed == 0 else "FAIL",
            "domains_audited": domains_audited,
            "versions_detected": versions,
        },
        "failures": [
            {
                "domain": r["domain"],
                "method": r["method"],
                "path": r["path"],
                "status": r["status"],
                "latency_ms": r["latency_ms"],
                "issues": r["issues"],
            }
            for r in errors
        ],
        "all_results": all_results,
    }


def print_report(report: dict):
    """Pretty-print report to terminal."""
    s = report["summary"]
    print(f"\n{'='*60}")
    print(f"  API Integrity Audit — {report['audit_id']}")
    print(f"  Mode: {report['mode']}  |  Auditor v{report['auditor_version']}")
    print(f"{'='*60}")
    print(f"  Endpoints: {s['total_endpoints']}  |  Passed: {s['passed']}  |  Failed: {s['failed']}")
    print(f"  Health: {s['health']}")
    print(f"  Domains: {', '.join(s['domains_audited'])}")
    if s["versions_detected"]:
        print(f"  Versions:")
        for d, v in s["versions_detected"].items():
            print(f"    {d}: {v}")

    if report["failures"]:
        print(f"\n  --- FAILURES ---")
        for f in report["failures"]:
            print(f"  ✗ {f['domain']}{f['path']}  [{f['status']}]")
            for issue in f["issues"]:
                print(f"      {issue}")

    # Per-domain summary
    print(f"\n  --- Per-Domain ---")
    for domain in s["domains_audited"]:
        domain_results = [r for r in report["all_results"] if r["domain"] == domain]
        dp = sum(1 for r in domain_results if r["passed"])
        df = len(domain_results) - dp
        avg_lat = round(sum(r["latency_ms"] for r in domain_results) / len(domain_results)) if domain_results else 0
        icon = "✓" if df == 0 else "✗"
        print(f"  {icon} {domain}: {dp}/{len(domain_results)} passed, {avg_lat}ms avg latency")


# ── CLI ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="WWA API Integrity Auditor")
    parser.add_argument("--mode", choices=["cloud", "local"], default="cloud",
                        help="cloud = production URLs, local = localhost ports")
    parser.add_argument("--domain", help="Audit specific domain only (dev, io, com, co.uk, bastion)")
    parser.add_argument("--json", action="store_true", help="Output JSON report to stdout")
    parser.add_argument("--report", help="Save report to file (JSON)")
    parser.add_argument("--timeout", type=int, default=15, help="Request timeout in seconds")
    args = parser.parse_args()

    # Friendly name mapping
    ALIASES = {"dev": "workswithagents.dev", "io": "workswithagents.io",
               "com": "workswithagents.com", "co.uk": "workswithagents.co.uk",
               "couk": "workswithagents.co.uk", "bastion": "bastiongateway.com"}
    if args.domain and args.domain in ALIASES:
        args.domain = ALIASES[args.domain]

    domains_to_audit = [args.domain] if args.domain else list(ENDPOINTS.keys())
    all_results = []

    for domain in domains_to_audit:
        if domain not in ENDPOINTS:
            print(f"Unknown domain: {domain}", file=sys.stderr)
            print(f"Available: {', '.join(ENDPOINTS.keys())}", file=sys.stderr)
            sys.exit(1)

        config = ENDPOINTS[domain]
        base_url = config["local"] if args.mode == "local" else config["cloud"]
        if not args.json:
            print(f"\n  Auditing {domain} ({base_url})...")

        results = audit_domain(domain, config, base_url)
        all_results.extend(results)

        if not args.json:
            for r in results:
                icon = "✓" if r["passed"] else "✗"
                print(f"    {icon} {r['method']:4} {r['path']:30} [{r['status']}] {r['latency_ms']}ms")

    report = generate_report(all_results, args.mode)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)

    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        with open(args.report, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\n  Report saved: {args.report}")

    # Exit code: non-zero if any failures
    if report["summary"]["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
