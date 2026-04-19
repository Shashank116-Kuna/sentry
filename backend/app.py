"""
SENTRY - Main FastAPI Application
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="../frontend"), name="static")
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from datetime import datetime
from pathlib import Path

from database import init_database
from models import *
from security.rate_limiter import check_rate_limit
from security.validator import validate_message, validate_channel, sanitize_input
from api import reports, campaigns, alerts, events

# Initialize FastAPI app
app = FastAPI(
    title="SENTRY API",
    description="Social Engineering Threat Reporting & Yielding System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
BASE_DIR = Path(__file__).parent.parent
static_dir = BASE_DIR / "frontend"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_database()
    print("✓ SENTRY system initialized")

# Health check
@app.get("/")
async def root():
    return {
        "status": "online",
        "system": "SENTRY v1.0",
        "timestamp": datetime.utcnow().isoformat()
    }

# Include API routers
app.include_router(reports.router, prefix="/api", tags=["Reports"])
app.include_router(campaigns.router, prefix="/api", tags=["Campaigns"])
app.include_router(alerts.router, prefix="/api", tags=["Alerts"])
app.include_router(events.router, prefix="/api", tags=["Events"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
