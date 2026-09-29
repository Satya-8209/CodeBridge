"""
FastAPI backend — serves all three interfaces:
  POST /alert     → fire a new alert, get AI suggestion
  POST /resolve   → mark incident resolved, store in Hindsight memory
  GET  /health    → health check
  GET  /ui        → serves the web UI (static HTML)
"""
import uuid
import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool

from backend.schemas import AlertIn, ResolveIn, AgentResponse
from backend.agent import handle_alert
from backend import hindsight_client as memory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Incident Memory Agent",
    description="DevOps on-call assistant powered by Hindsight persistent memory",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the Web UI at /ui
app.mount("/ui", StaticFiles(directory="web_ui", html=True), name="ui")


@app.post("/alert", response_model=AgentResponse, summary="Fire a new alert")
async def new_alert(alert: AlertIn):
    """
    Accepts a new production alert.
    - Recalls similar past incidents from Hindsight memory
    - Asks xAI Grok for root cause analysis
    - Returns structured suggestion + matched memory snippets
    """
    alert_id = str(uuid.uuid4())[:8].upper()
    logger.info("New alert [%s]: %s on %s", alert_id, alert.title, alert.service)

    result = await run_in_threadpool(
        handle_alert,
        alert.title,
        alert.service,
        alert.error_log,
        alert_id,
    )
    return result


@app.post("/resolve", summary="Resolve an incident and store in memory")
async def resolve_incident(data: ResolveIn):
    """
    Called after an incident is resolved.
    Stores the incident's root cause and fix in Hindsight memory
    so future alerts can benefit from this knowledge.
    """
    content = (
        f"Service: {data.service}\n"
        f"Incident: {data.title}\n"
        f"Root Cause: {data.root_cause}\n"
        f"Fix Applied: {data.fix_applied}\n"
        f"Time to Resolve: {data.time_to_resolve_minutes} minutes"
    )
    await run_in_threadpool(
        memory.retain,
        content,
        {
            "alert_id": data.alert_id,
            "service": data.service,
            "root_cause": data.root_cause,
        },
    )
    logger.info("Stored resolved incident [%s] in memory", data.alert_id)
    return {
        "status": "stored",
        "alert_id": data.alert_id,
        "bank": "devops-incident-memory",
        "message": "Incident stored in Hindsight memory. Future similar alerts will benefit.",
    }


@app.get("/health", summary="Health check")
async def health():
    return {"status": "ok", "service": "incident-memory-agent"}
