#!/usr/bin/env python3.11
"""
Tiny newsletter handler for local dev.
Replace with ConvertKit/Buttondown when ready to deploy.
"""
import json, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent / "newsletter-subs.json"
PORT = 8498


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def _load(self):
        if DATA_FILE.exists():
            return json.loads(DATA_FILE.read_text())
        return []

    def _save(self, data):
        DATA_FILE.write_text(json.dumps(data, indent=2))

    def do_POST(self):
        if self.path != "/v1/newsletter/subscribe":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length)) if length else {}
        email = body.get("email", "").strip().lower()

        if not email or "@" not in email:
            self.send_response(400)
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps({"detail": "Invalid email"}).encode())
            return

        subs = self._load()
        existing = [s for s in subs if s["email"] == email]
        if existing:
            self.send_response(200)
            self._cors()
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Already subscribed"}).encode())
            return

        subs.append({
            "email": email,
            "subscribed_at": datetime.now(timezone.utc).isoformat(),
            "source": "local-dev"
        })
        self._save(subs)

        self.send_response(200)
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps({"message": "Subscribed! You'll hear from us soon."}).encode())
        print(f"[newsletter] +{email}  (total: {len(subs)})")

    def log_message(self, format, *args):
        pass  # quiet


if __name__ == "__main__":
    print(f"[newsletter] Listening on :{PORT}  → {DATA_FILE}")
    HTTPServer(("", PORT), Handler).serve_forever()
