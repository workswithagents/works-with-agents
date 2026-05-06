"""
IACP — Inter-Agent Communication Protocol client.
Zero dependencies. Copy-pasteable.

Usage:
    from workswithagents.iacp import IACPClient
    
    client = IACPClient("builder-01")
    peers = client.discover("code_review")
    msg_id = client.send("reviewer-02", "handoff", {"task": "Review src/main.py"})
    inbox = client.poll()
"""

import json
import time
import uuid
import urllib.request
import urllib.error

DEFAULT_API = "https://workswithagents.dev"


class IACPClient:
    """Inter-Agent Communication Protocol client."""

    def __init__(self, agent_id: str, api: str = DEFAULT_API):
        self.agent_id = agent_id
        self.api = api.rstrip("/")

    def discover(self, capability: str = None) -> list:
        """Discover peers by capability."""
        url = f"{self.api}/v1/peers"
        if capability:
            url += f"?capability={capability}"
        req = urllib.request.Request(
            url,
            headers={"X-Agent-ID": self.agent_id, "Accept": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def send(self, to_agent: str, intent: str, payload: dict) -> str:
        """Send an IACP message. Returns message_id."""
        msg_id = str(uuid.uuid4())
        envelope = {
            "version": "1.0",
            "message_id": msg_id,
            "sender": {"agent_id": self.agent_id},
            "recipient": {"agent_id": to_agent},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "message": {"type": "request", "intent": intent, "payload": payload},
        }
        data = json.dumps(envelope).encode()
        req = urllib.request.Request(
            f"{self.api}/v1/messages",
            data=data,
            method="POST",
            headers={"Content-Type": "application/json", "X-Agent-ID": self.agent_id},
        )
        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read())
            return result.get("message_id", msg_id)
        except urllib.error.HTTPError as e:
            return json.dumps({"error": e.code, "message": e.read().decode()})

    def poll(self) -> list:
        """Poll for messages addressed to this agent."""
        req = urllib.request.Request(
            f"{self.api}/v1/messages?recipient={self.agent_id}",
            headers={"X-Agent-ID": self.agent_id, "Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return [{"error": e.code, "message": e.read().decode()}]

    def heartbeat(self, status: str = "idle", load: float = 0.0) -> dict:
        """Send a heartbeat with status and load."""
        return self.send("registry", "health", {"status": status, "load": load})
