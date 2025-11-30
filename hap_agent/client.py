import base64
import hashlib
import json
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple

import requests
from ecdsa import SigningKey, NIST256p


def b64url_decode(s: str) -> bytes:
    padding = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + padding)


def b64url_encode(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


@dataclass
class AgentConfig:
    api_base: str           # e.g. "https://api.sanatdhir.com"
    agent_id: str           # e.g. "agent_..."
    private_key_b64: str    # privateKeyBase64 from agents.html


class HapAgentClient:
    """
    Low-level HAP client that:
    - builds the signing string
    - signs with ES256 (P-256 ECDSA)
    - attaches HAP headers
    - sends HTTP requests
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self._sk = self._load_signing_key()

    def _load_signing_key(self) -> SigningKey:
        raw = b64url_decode(self.config.private_key_b64)
        if len(raw) != 32:
            raise ValueError(f"Expected 32 bytes for P-256 private key, got {len(raw)}")
        return SigningKey.from_string(raw, curve=NIST256p)

    def _build_signing_string(
        self,
        method: str,
        path_with_query: str,
        body_bytes: bytes,
        timestamp: str,
    ) -> str:
        body_hash = hashlib.sha256(body_bytes or b"").hexdigest()
        return f"{method.upper()}\n{path_with_query}\n{timestamp}\n{body_hash}"

    def sign_request(
        self,
        method: str,
        path_with_query: str,
        body: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, str], bytes]:
        if body is None:
            body_bytes = b""
        else:
            body_bytes = json.dumps(body, separators=(",", ":"), sort_keys=True).encode(
                "utf-8"
            )

        ts = str(int(time.time()))
        signing_string = self._build_signing_string(method, path_with_query, body_bytes, ts)
        sig_bytes = self._sk.sign(signing_string.encode("utf-8"))
        sig_b64 = b64url_encode(sig_bytes)

        headers = {
            "Sec-Client-Class": "agent",
            "HAP-Agent-Id": self.config.agent_id,
            "X-HAP-Timestamp": ts,
            "HAP-Signature": f"v0:{sig_b64}",
            "Content-Type": "application/json",
        }
        return headers, body_bytes

    def request(
        self,
        method: str,
        path: str,
        query: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        from urllib.parse import urlencode

        query = query or {}
        if query:
            qs = urlencode(query)
            path_with_query = f"{path}?{qs}"
        else:
            path_with_query = path

        headers, body_bytes = self.sign_request(method, path_with_query, json_body)
        url = f"{self.config.api_base}{path_with_query}"

        data = body_bytes if method.upper() in ("POST", "PUT", "PATCH") else None
        resp = requests.request(method, url, headers=headers, data=data)
        return resp
