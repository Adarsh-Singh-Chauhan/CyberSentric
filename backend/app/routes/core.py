"""
CyberSentric Core API Routes
Threat analysis, dashboard data, agent status, red team simulation.
"""
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional
from app.orchestrator import orchestrator
from app.websocket_manager import ws_manager
from app.routes.auth import get_current_user, require_admin

router = APIRouter(prefix="/api", tags=["core"])


class AnalyzeRequest(BaseModel):
    input: str
    source_ip: Optional[str] = "127.0.0.1"
    user_id: Optional[str] = "anonymous"
    action: Optional[str] = "request"
    status: Optional[str] = "success"
    endpoint: Optional[str] = "/"


class SimulationRequest(BaseModel):
    simulation_type: str = "full"


@router.post("/analyze")
async def analyze_input(req: AnalyzeRequest, user: dict = Depends(get_current_user)):
    """Run input through the full agent pipeline."""
    result = await orchestrator.process_input(req.model_dump())
    await ws_manager.broadcast("threat_event", result)
    return result


@router.get("/dashboard")
async def get_dashboard(user: dict = Depends(get_current_user)):
    """Get aggregated dashboard data."""
    data = orchestrator.get_dashboard_data()
    data["connected_clients"] = ws_manager.count
    data["user_role"] = user.get("role", "user")
    return data


@router.get("/agents")
async def get_agents(user: dict = Depends(get_current_user)):
    """Get all agent statuses."""
    return {"agents": orchestrator.get_all_agent_status()}


@router.get("/agents/{agent_name}")
async def get_agent(agent_name: str, user: dict = Depends(get_current_user)):
    """Get specific agent status and recent events."""
    agents = {a.name.lower(): a for a in [orchestrator.defender, orchestrator.analyzer,
              orchestrator.response, orchestrator.monitor, orchestrator.redteam]}
    agent = agents.get(agent_name.lower())
    if not agent:
        return {"error": f"Agent '{agent_name}' not found"}
    status = agent.get_status()
    status["recent_events"] = [e.model_dump() for e in agent.events[-20:]]
    return status


@router.get("/threats")
async def get_threats(user: dict = Depends(get_current_user)):
    """Get recent threat data."""
    return {
        "recent_alerts": orchestrator.response.get_recent_alerts(),
        "blocked_ips": orchestrator.response.get_blocked_ips(),
        "action_history": orchestrator.response.get_action_history(),
        "total_threats": orchestrator.total_threats,
    }


@router.get("/stats")
async def get_stats(user: dict = Depends(get_current_user)):
    """Get threat statistics for charts."""
    agents = orchestrator.get_all_agent_status()
    total_processed = sum(a["processed_count"] for a in agents)
    total_threats = sum(a["threats_detected"] for a in agents)

    # Attack type distribution
    type_counts = {}
    for alert in orchestrator.response.get_recent_alerts(100):
        tt = alert.get("threat_type", "unknown")
        type_counts[tt] = type_counts.get(tt, 0) + 1
    attack_types = [{"name": k, "value": v} for k, v in type_counts.items()]

    # Severity distribution
    sev_counts = {}
    for alert in orchestrator.response.get_recent_alerts(100):
        s = alert.get("severity", "unknown")
        sev_counts[s] = sev_counts.get(s, 0) + 1

    return {
        "total_processed": total_processed,
        "total_threats": total_threats,
        "detection_rate": round(total_threats / max(total_processed, 1), 3),
        "attack_types": attack_types if attack_types else [
            {"name": "prompt_injection", "value": 0}, {"name": "xss", "value": 0},
            {"name": "sqli", "value": 0}, {"name": "brute_force", "value": 0}
        ],
        "severity_distribution": sev_counts,
        "blocked_ips_count": len(orchestrator.response.blocked_ips),
        "pipeline_runs": orchestrator.pipeline_runs,
    }


@router.post("/redteam/simulate")
async def run_simulation(req: SimulationRequest, user: dict = Depends(require_admin)):
    """Run a red team simulation (admin only)."""
    result = await orchestrator.run_red_team(req.simulation_type)
    await ws_manager.broadcast("simulation_complete", {
        "type": req.simulation_type,
        "detection_rate": result.get("overall_detection_rate", result.get("detection_rate", 0)),
        "tests_run": result.get("tests_run", 0),
    })
    return result


@router.get("/redteam/history")
async def get_redteam_history(user: dict = Depends(get_current_user)):
    """Get red team simulation history."""
    return {"history": orchestrator.redteam.get_simulation_history()}


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """WebSocket endpoint for real-time dashboard updates."""
    await ws_manager.connect(ws)
    # Subscribe monitor agent to broadcast events
    async def on_event(event_type: str, data: dict):
        await ws_manager.broadcast(event_type, data)
    orchestrator.monitor.subscribe(on_event)
    try:
        while True:
            data = await ws.receive_text()
            # Client can send commands via WebSocket
            if data == "ping":
                await ws.send_text('{"type":"pong"}')
            elif data == "status":
                import json
                await ws.send_text(json.dumps({"type": "status",
                    "data": orchestrator.get_all_agent_status()}, default=str))
    except WebSocketDisconnect:
        pass
    finally:
        orchestrator.monitor.unsubscribe(on_event)
        await ws_manager.disconnect(ws)
