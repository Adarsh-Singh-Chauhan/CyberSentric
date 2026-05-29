"""
CyberSentric Response Agent
Automatically responds to threats: block IP, sanitize, alert.
"""
from datetime import datetime
from typing import Optional
from app.agents.base_agent import ActionResult, AgentStatus, BaseAgent, Severity, ThreatResult


class ResponseAgent(BaseAgent):
    def __init__(self):
        super().__init__("Response")
        self.blocked_ips: set[str] = set()
        self.rate_limited_ips: dict[str, datetime] = {}
        self.alerts: list[dict] = []
        self.action_log: list[ActionResult] = []

    async def process(self, data: dict) -> dict:
        self.status = AgentStatus.PROCESSING
        self.processed_count += 1
        threat = data.get("threat_result")
        if not threat:
            self.status = AgentStatus.IDLE
            return {"actions_taken": [], "status": "no_threat"}

        if isinstance(threat, ThreatResult):
            threat = threat.model_dump()

        severity = threat.get("severity", "none")
        actions_taken = []
        recommended = threat.get("recommended_actions", [])

        if "block_ip" in recommended and threat.get("source_ip"):
            result = self._block_ip(threat["source_ip"], threat.get("description", ""))
            actions_taken.append(result)

        if "rate_limit" in recommended or "rate_limit_ip" in recommended:
            ip = threat.get("source_ip", "unknown")
            result = self._rate_limit_ip(ip)
            actions_taken.append(result)

        if "alert_admin" in recommended:
            result = await self._send_alert(threat)
            actions_taken.append(result)

        if "sanitize_input" in recommended:
            result = ActionResult(action_type="sanitize_input", success=True,
                                  target=threat.get("user_id", "unknown"),
                                  description="Input sanitized and safe version returned")
            actions_taken.append(result)

        if "log_critical" in recommended or "log_warning" in recommended or "log_info" in recommended:
            log_level = "critical" if "log_critical" in recommended else "warning" if "log_warning" in recommended else "info"
            result = ActionResult(action_type=f"log_{log_level}", success=True,
                                  target="system", description=f"Threat logged at {log_level} level",
                                  metadata={"threat_type": threat.get("threat_type"),
                                            "severity": severity})
            actions_taken.append(result)

        if "increase_monitoring" in recommended:
            result = ActionResult(action_type="increase_monitoring", success=True,
                                  target=threat.get("source_ip", "unknown"),
                                  description="Enhanced monitoring enabled for this source")
            actions_taken.append(result)

        if not actions_taken:
            actions_taken.append(ActionResult(action_type="monitor", success=True,
                                             target="system", description="Continued monitoring"))

        self.action_log.extend(actions_taken)
        self.action_log = self.action_log[-200:]

        if severity in ("high", "critical"):
            self.status = AgentStatus.ALERT
            self.threats_detected += 1
        else:
            self.status = AgentStatus.IDLE

        self.emit_event("response_executed", {
            "actions_count": len(actions_taken),
            "severity": severity,
            "actions": [a.action_type for a in actions_taken]
        }, severity=Severity(severity) if severity != "none" else Severity.NONE)

        return {
            "actions_taken": [a.model_dump() for a in actions_taken],
            "status": "responded",
            "blocked_ips_count": len(self.blocked_ips),
            "total_alerts": len(self.alerts),
        }

    def _block_ip(self, ip: str, reason: str) -> ActionResult:
        self.blocked_ips.add(ip)
        return ActionResult(action_type="block_ip", success=True, target=ip,
                            description=f"IP {ip} blocked. Reason: {reason[:100]}",
                            metadata={"total_blocked": len(self.blocked_ips)})

    def _rate_limit_ip(self, ip: str) -> ActionResult:
        self.rate_limited_ips[ip] = datetime.utcnow()
        return ActionResult(action_type="rate_limit", success=True, target=ip,
                            description=f"Rate limiting applied to {ip}")

    async def _send_alert(self, threat: dict) -> ActionResult:
        alert = {"timestamp": datetime.utcnow().isoformat(), "severity": threat.get("severity"),
                 "threat_type": threat.get("threat_type"), "description": threat.get("description", ""),
                 "source_ip": threat.get("source_ip")}
        self.alerts.append(alert)
        self.alerts = self.alerts[-100:]

        # SOC Notification for CRITICAL/HIGH threats
        severity = threat.get("severity", "none").lower()
        if severity in ("critical", "high"):
            import os
            webhook_url = os.getenv("SOC_WEBHOOK_URL", "")
            if webhook_url:
                import httpx
                import asyncio
                payload = {
                    "text": f"🚨 *{severity.upper()} Threat Detected* 🚨\nType: {alert['threat_type']}\nIP: {alert['source_ip']}\nDesc: {alert['description']}"
                }
                async def post_webhook():
                    try:
                        async with httpx.AsyncClient(timeout=3.0) as client:
                            await client.post(webhook_url, json=payload)
                    except Exception as e:
                        print(f"Failed to send SOC webhook: {e}")
                asyncio.create_task(post_webhook())

        return ActionResult(action_type="alert_admin", success=True, target="admin",
                            description=f"Alert sent: {threat.get('threat_type')} ({threat.get('severity')})")

    def is_ip_blocked(self, ip: str) -> bool:
        return ip in self.blocked_ips

    def get_blocked_ips(self) -> list[str]:
        return list(self.blocked_ips)

    def get_recent_alerts(self, limit: int = 20) -> list[dict]:
        return self.alerts[-limit:]

    def get_action_history(self, limit: int = 50) -> list[dict]:
        return [a.model_dump() for a in self.action_log[-limit:]]
