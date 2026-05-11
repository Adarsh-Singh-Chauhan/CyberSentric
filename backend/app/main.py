"""
CyberSentric — FastAPI Application Entry Point
"""
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes.auth import router as auth_router
from app.routes.core import router as core_router
from app.orchestrator import orchestrator


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: begin monitor heartbeat
    task = asyncio.create_task(orchestrator.monitor.start_heartbeat(5.0))
    print(f"[CyberSentric] v{settings.APP_VERSION} started")
    print(f"[CyberSentric] Agents: Defender, Analyzer, Response, Monitor, RedTeam")
    yield
    # Shutdown
    orchestrator.monitor.stop_heartbeat()
    task.cancel()
    print("[CyberSentric] Shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Agent-Driven Cybersecurity Defense Platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(core_router)


import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

@app.get("/health")
async def health():
    return {"status": "healthy", "agents_active": 5,
            "pipeline_runs": orchestrator.pipeline_runs}

# Serve frontend static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")

if os.path.isdir(frontend_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dir, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = os.path.join(frontend_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dir, "index.html"))
else:
    @app.get("/")
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "operational - FRONTEND NOT BUILT",
            "message": "Run 'npm run build' in the frontend directory."
        }
