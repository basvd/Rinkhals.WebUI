from __future__ import annotations

import json
import os
import random
import socket
from typing import Any, Dict, Optional


_DEFAULT_SOCKET = "/tmp/unix_uds1"
_SOCKET_ENV = "KLIPPY_SOCKET_PATH"
_MESSAGE_TERMINATOR = "\x03"


class KlippyError(RuntimeError):
    """Raised when Klippy connection fails or returns an error payload."""


class KlippyClient:
    """Client to interact with the Klippy API socket."""

    def __init__(self, socket_path: Optional[str] = None, timeout: float = 3.0) -> None:
        self.socket_path = socket_path or os.getenv(_SOCKET_ENV, _DEFAULT_SOCKET)
        self.timeout = timeout

    def call(self, method: str, params: Optional[Dict[str, Any]] = None, request_id: Optional[int] = None) -> Dict[str, Any]:
        """Send a JSON-RPC command and return the decoded response."""

        payload = {
            "method": method,
            "params": params or {},
            "id": request_id or random.randint(1, 1_000_000),
        }
        response = self._send_request(payload)
        if "error" in response:
            raise KlippyError(response["error"])
        return response

    def _send_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        message = json.dumps(payload) + _MESSAGE_TERMINATOR
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)

        try:
            sock.connect(self.socket_path)
            sock.sendall(message.encode("utf-8"))

            chunks = []
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
        except OSError as e:
            raise KlippyError(f"Unable to reach Klippy on {self.socket_path}: {e}") from e
        finally:
            try:
                sock.close()
            except OSError:
                pass

        if not chunks:
            raise KlippyError("Klippy returned an empty response")

        raw = b"".join(chunks).decode("utf-8").strip().rstrip(_MESSAGE_TERMINATOR)
        try:
            return json.loads(raw)
        except ValueError as exc:
            raise KlippyError(f"Klippy returned invalid JSON: {raw}") from exc
