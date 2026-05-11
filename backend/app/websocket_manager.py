"""
CyberSentric WebSocket Manager
Real-time event broadcasting to connected frontend clients.
"""
import asyncio
import json
from datetime import datetime
from typing import Any
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self.active.append(ws)

    async def disconnect(self, ws: WebSocket):
        async with self._lock:
            if ws in self.active:
                self.active.remove(ws)

    async def broadcast(self, event_type: str, data: Any):
        msg = json.dumps({"type": event_type, "data": data,
                          "timestamp": datetime.utcnow().isoformat()}, default=str)
        async with self._lock:
            dead = []
            for ws in self.active:
                try:
                    await ws.send_text(msg)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                self.active.remove(ws)

    @property
    def count(self) -> int:
        return len(self.active)


ws_manager = ConnectionManager()
