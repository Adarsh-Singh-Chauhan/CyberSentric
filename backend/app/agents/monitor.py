"""
CyberSentric Monitor Agent
Tracks system activity in real-time, logs events, sends dashboard updates.
"""
import asyncio
import random
from datetime import datetime
from typing import Any, Callable, Optional
from app.agents.base_agent import AgentStatus, BaseAgent, Severity


class MonitorAgent(BaseAgent):
    def __init__(self):
        super().__init__("Monitor")
        self._subscribers: list[Callable] = []
        self._system_metrics: list[dict] = []
        self._running = False
        self.total_events_logged = 0

    def subscribe(self, callback: Callable):
        self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable):
        self._subscribers = [s for s in self._subscribers if s != callback]

    async def _notify_subscribers(self, event_type: str, data: dict):
        for cb in self._subscribers:
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(event_type, data)
                else:
                    cb(event_type, data)
            except Exception:
                pass

    async def process(self, data: dict) -> dict:
        self.status = AgentStatus.PROCESSING
        self.processed_count += 1
        self.total_events_logged += 1

        event_type = data.get("event_type", "system_event")
        event_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "source": data.get("source", "system"),
            "severity": data.get("severity", "none"),
            "message": data.get("message", ""),
            "details": data.get("details", {}),
        }

        await self._notify_subscribers(event_type, event_data)

        self.emit_event(event_type, event_data,
                        severity=Severity(data.get("severity", "none"))
                        if data.get("severity") in ("low", "medium", "high", "critical") else Severity.NONE)

        self.status = AgentStatus.IDLE
        return {"logged": True, "event_id": self.events[-1].event_id if self.events else None}

    async def log_threat(self, threat_result: dict, response_result: dict):
        await self.process({
            "event_type": "threat_response",
            "source": "orchestrator",
            "severity": threat_result.get("severity", "none"),
            "message": f"Threat: {threat_result.get('threat_type', 'unknown')} | "
                       f"Actions: {len(response_result.get('actions_taken', []))}",
            "details": {"threat": threat_result, "response": response_result},
        })

    async def log_system_metric(self, metric: dict):
        metric["timestamp"] = datetime.utcnow().isoformat()
        self._system_metrics.append(metric)
        self._system_metrics = self._system_metrics[-500:]
        await self._notify_subscribers("system_metric", metric)

    def get_system_metrics(self, limit: int = 50) -> list[dict]:
        return self._system_metrics[-limit:]

    async def start_heartbeat(self, interval: float = 5.0):
        self._running = True
        while self._running:
            metric = {
                "cpu_usage": round(random.uniform(15, 85), 1),
                "memory_usage": round(random.uniform(30, 75), 1),
                "active_connections": random.randint(5, 150),
                "threats_per_minute": random.randint(0, 12),
                "agents_active": 5,
                "uptime_seconds": self.processed_count * 5,
            }
            await self.log_system_metric(metric)
            await asyncio.sleep(interval)

    def stop_heartbeat(self):
        self._running = False
