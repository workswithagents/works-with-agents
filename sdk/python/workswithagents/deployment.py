"""
Agent Deployment Manifest — Cross-Layer
Docker Compose for agent fleets. Deploy from YAML.

Usage:
    from workswithagents import DeploymentManifest
    
    dm = DeploymentManifest.from_file("fleet.yaml")
    dm.validate()
    dm.deploy()
    dm.status()
"""

import json
import urllib.request
import urllib.error
from typing import Optional
from pathlib import Path

DEFAULT_API = "https://workswithagents.dev"


class DeploymentManifest:
    """Parse, validate, and deploy agent fleet manifests."""
    
    def __init__(self, manifest: dict, api_url: str = DEFAULT_API):
        self.manifest = manifest
        self.api = api_url.rstrip("/")
        self.fleet_id = None
    
    @classmethod
    def from_file(cls, path: str, api_url: str = DEFAULT_API) -> "DeploymentManifest":
        """Load manifest from YAML or JSON file."""
        content = Path(path).read_text()
        if path.endswith('.json'):
            import json
            return cls(json.loads(content), api_url)
        else:
            # Try YAML, fall back to JSON
            try:
                import yaml
                return cls(yaml.safe_load(content), api_url)
            except ImportError:
                # Minimal YAML parser for common cases
                return cls(_parse_simple_yaml(content), api_url)
    
    @classmethod
    def minimal(cls, name: str, agent_id: str, 
                capabilities: list, api_url: str = DEFAULT_API) -> "DeploymentManifest":
        """Create a minimal manifest for a single agent."""
        return cls({
            "manifest_version": "1.0.0-draft",
            "fleet": {
                "name": name,
                "agents": [{
                    "id": agent_id,
                    "type": "hermes",
                    "capabilities": capabilities
                }]
            }
        }, api_url)
    
    def validate(self) -> dict:
        """Validate manifest structure. Returns {valid, errors}."""
        errors = []
        mf = self.manifest
        
        if "manifest_version" not in mf:
            errors.append("Missing manifest_version")
        if "fleet" not in mf:
            errors.append("Missing fleet section")
            return {"valid": False, "errors": errors}
        
        fleet = mf["fleet"]
        if "name" not in fleet:
            errors.append("Missing fleet.name")
        if "agents" not in fleet or not fleet["agents"]:
            errors.append("Missing fleet.agents (at least one required)")
        
        for i, agent in enumerate(fleet.get("agents", [])):
            if "id" not in agent:
                errors.append(f"Agent[{i}]: missing id")
            if "capabilities" not in agent:
                errors.append(f"Agent[{i}]: missing capabilities")
        
        return {"valid": len(errors) == 0, "errors": errors}
    
    def deploy(self) -> dict:
        """Deploy fleet from manifest."""
        validation = self.validate()
        if not validation["valid"]:
            return {"status": "error", "errors": validation["errors"]}
        
        result = self._request("POST", "/v1/fleets/deploy", self.manifest)
        if "fleet_id" in result:
            self.fleet_id = result["fleet_id"]
        return result
    
    def status(self) -> dict:
        """Get fleet status."""
        if not self.fleet_id:
            return {"error": "Fleet not deployed. Call deploy() first."}
        return self._request("GET", f"/v1/fleets/{self.fleet_id}/status")
    
    def scale(self, agent_type: str, count: int) -> dict:
        """Scale an agent type up or down."""
        if not self.fleet_id:
            return {"error": "Fleet not deployed."}
        return self._request("POST", f"/v1/fleets/{self.fleet_id}/scale", {
            "agent_type": agent_type,
            "count": count
        })
    
    def _request(self, method: str, path: str, data: Optional[dict] = None) -> dict:
        url = f"{self.api}{path}"
        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, method=method)
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return {"error": e.code, "message": e.read().decode()}


def _parse_simple_yaml(text: str) -> dict:
    """Minimal YAML parser for common manifest patterns. Falls back to JSON."""
    # Try JSON first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Basic YAML: only handles simple key: value and nested dicts
    # For full YAML support: pip install pyyaml
    result = {}
    current = result
    stack = []
    indent_level = 0
    
    for line in text.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        
        # Calculate indent
        indent = len(line) - len(line.lstrip())
        
        if ':' in stripped:
            key, _, value = stripped.partition(':')
            key = key.strip()
            value = value.strip()
            
            if value == '':
                # Start of nested dict
                current[key] = {}
                stack.append(current)
                current = current[key]
            else:
                # Simple key: value
                # Try parsing value
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value.isdigit():
                    value = int(value)
                elif value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                current[key] = value
    
    return result
