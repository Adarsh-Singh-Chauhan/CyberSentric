"""
CyberSentric Orchestrator
Coordinates all agents in a pipeline: Defender → Analyzer → Response → Monitor
"""
from datetime import datetime
from app.agents.defender import DefenderAgent
from app.agents.analyzer import AnalyzerAgent
from app.agents.response import ResponseAgent
from app.agents.monitor import MonitorAgent
from app.agents.redteam import RedTeamAgent


class Orchestrator:
    def __init__(self):
        self.defender = DefenderAgent()
        self.analyzer = AnalyzerAgent()
        self.response = ResponseAgent()
        self.monitor = MonitorAgent()
        self.redteam = RedTeamAgent()
        self.pipeline_runs = 0
        self.total_threats = 0

    async def process_input(self, data: dict) -> dict:
        """Run the full agent pipeline on input data."""
        self.pipeline_runs += 1
        start = datetime.utcnow()

        # Check if IP is already blocked
        ip = data.get("source_ip", "")
        if ip and self.response.is_ip_blocked(ip):
            blocked_result = {
                "threat_detected": True, "threat_type": "blocked_ip",
                "severity": "critical", "description": f"IP {ip} is blocked",
                "actions_taken": [{"action_type": "request_denied", "success": True,
                                   "target": ip, "description": "Blocked IP attempted access"}],
                "pipeline_stage": "pre_check", "blocked": True,
            }
            await self.monitor.process({"event_type": "blocked_ip_access", "source": "orchestrator",
                                         "severity": "high", "message": f"Blocked IP {ip} attempted access"})
            return blocked_result

        # Stage 1: Defender
        defender_result = await self.defender.process(data)
        defender_dict = defender_result.model_dump()

        # Stage 2: Analyzer
        analyzer_data = {**data, "defender_result": defender_dict}
        analyzer_result = await self.analyzer.process(analyzer_data)
        analyzer_dict = analyzer_result.model_dump()

        # Merge: take the higher severity
        sev_map = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
        if sev_map.get(analyzer_dict["severity"], 0) >= sev_map.get(defender_dict["severity"], 0):
            final_threat = analyzer_dict
        else:
            final_threat = defender_dict

        # Stage 3: Response
        response_result = await self.response.process({"threat_result": final_threat})

        # Stage 4: Monitor
        await self.monitor.log_threat(final_threat, response_result)

        elapsed = (datetime.utcnow() - start).total_seconds()
        if final_threat.get("threat_detected"):
            self.total_threats += 1

        return {
            "threat_detected": final_threat.get("threat_detected", False),
            "threat_type": final_threat.get("threat_type", "none"),
            "severity": final_threat.get("severity", "none"),
            "confidence": final_threat.get("confidence", 0),
            "description": final_threat.get("description", ""),
            "sanitized_input": defender_dict.get("sanitized_input"),
            "actions_taken": response_result.get("actions_taken", []),
            "defender_analysis": defender_dict.get("metadata", {}),
            "analyzer_analysis": analyzer_dict.get("metadata", {}),
            "pipeline_time_ms": round(elapsed * 1000, 2),
            "pipeline_run": self.pipeline_runs,
        }

    async def run_red_team(self, simulation_type: str = "full") -> dict:
        return await self.redteam.process({"simulation_type": simulation_type, "orchestrator": self})

    def get_all_agent_status(self) -> list[dict]:
        return [a.get_status() for a in [self.defender, self.analyzer, self.response, self.monitor, self.redteam]]

    def get_dashboard_data(self) -> dict:
        return {
            "pipeline_runs": self.pipeline_runs, "total_threats": self.total_threats,
            "blocked_ips": self.response.get_blocked_ips(),
            "blocked_ips_count": len(self.response.blocked_ips),
            "recent_alerts": self.response.get_recent_alerts(),
            "agents": self.get_all_agent_status(),
            "system_metrics": self.monitor.get_system_metrics(),
            "action_history": self.response.get_action_history(),
            "red_team_history": self.redteam.get_simulation_history(),
        }


# Global orchestrator instance
orchestrator = Orchestrator()
