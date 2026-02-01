from __future__ import annotations

import os
import time
import uuid
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

# ----------------------------
# Config
# ----------------------------
API_KEY = os.getenv("RACKLAB_API_KEY", "").strip()  # optional; if empty, auth is disabled

app = FastAPI(
    title="RackLab-OSH API",
    version="1.0.0",
    description="Meta-style Hardware Systems test harness demo API (minimal working).",
)

# ----------------------------
# Simple in-memory store (demo)
# NOTE: For production, replace with Postgres/SQLite.
# ----------------------------
RUNS: dict[str, dict] = {}

# ----------------------------
# Middleware: request id + basic structured logging
# ----------------------------
@app.middleware("http")
async def add_request_id_and_log(request: Request, call_next):
    rid = request.headers.get("x-request-id") or str(uuid.uuid4())
    start = time.time()
    try:
        response = await call_next(request)
    except Exception as e:
        dur_ms = int((time.time() - start) * 1000)
        print(f'{{"level":"ERROR","rid":"{rid}","path":"{request.url.path}","ms":{dur_ms},"err":"{type(e).__name__}"}}')
        raise
    dur_ms = int((time.time() - start) * 1000)
    response.headers["x-request-id"] = rid
    print(f'{{"level":"INFO","rid":"{rid}","path":"{request.url.path}","status":{response.status_code},"ms":{dur_ms}}}')
    return response


# ----------------------------
# Auth dependency (optional)
# ----------------------------
def require_api_key(x_api_key: Optional[str]) -> None:
    if not API_KEY:
        return  # auth disabled
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


# ----------------------------
# Health + demo endpoints
# ----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/runs")
async def create_run(
    request: Request,
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
):
    """
    Minimal run creation endpoint.
    Accepts JSON body like:
    {
      "name": "thermal_smoke",
      "notes": "optional"
    }
    """
    require_api_key(x_api_key)

    body = await request.json()
    name = str(body.get("name", "")).strip() or "racklab-run"
    notes = str(body.get("notes", "")).strip()

    # idempotency: return existing run if key matches
    if idempotency_key:
        for rid, r in RUNS.items():
            if r.get("idempotency_key") == idempotency_key:
                return {"id": rid, "status": r["status"], "name": r["name"], "idempotency_key": idempotency_key}

    run_id = str(uuid.uuid4())
    RUNS[run_id] = {
        "id": run_id,
        "name": name,
        "notes": notes,
        "status": "queued",
        "created_at": int(time.time()),
        "idempotency_key": idempotency_key,
    }
    return {"id": run_id, "status": "queued", "name": name}


@app.get("/api/runs")
def list_runs(x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")):
    require_api_key(x_api_key)
    return {"runs": list(RUNS.values())}


@app.get("/api/runs/{run_id}")
def get_run(run_id: str, x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")):
    require_api_key(x_api_key)
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.post("/api/runs/{run_id}/simulate_complete")
def simulate_complete(run_id: str, x_api_key: Optional[str] = Header(default=None, alias="X-API-Key")):
    """
    Demo helper: marks a run as completed (passed) to show end-to-end flow in Swagger.
    """
    require_api_key(x_api_key)
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    run["status"] = "passed"
    run["ended_at"] = int(time.time())
    return run


@app.get("/api/metrics")
def metrics():
    """
    Minimal metrics endpoint (demo).
    """
    total = len(RUNS)
    failed = sum(1 for r in RUNS.values() if r.get("status") == "failed")
    passed = sum(1 for r in RUNS.values() if r.get("status") == "passed")
    queued = sum(1 for r in RUNS.values() if r.get("status") == "queued")
    running = sum(1 for r in RUNS.values() if r.get("status") == "running")

    err_rate = (failed / total) if total else 0.0
    return {
        "runs_total": total,
        "runs_passed": passed,
        "runs_failed": failed,
        "runs_queued": queued,
        "runs_running": running,
        "error_rate": round(err_rate, 4),
        "notes": {
            "p50_ms": 0,
            "p95_ms": 0,
            "message": "This is a minimal deployable demo. Upgrade to DB + worker + simulator next.",
        },
    }


# ----------------------------
# Friendly JSON errors
# ----------------------------
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})
