import time
import uuid
from fastapi import FastAPI, HTTPException
from worker.worker import execute_testplan

app = FastAPI(
    title="RackLab-OSH API",
    version="1.1.0",
    description="Meta-style Hardware Systems test harness demo API",
)

# In-memory run store (demo)
RUNS = {}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/runs")
def create_run(payload: dict):
    run_id = str(uuid.uuid4())
    RUNS[run_id] = {
        "id": run_id,
        "name": payload.get("name", "rack-test"),
        "status": "queued",
        "created_at": int(time.time()),
    }
    return RUNS[run_id]

@app.get("/api/runs")
def list_runs():
    return {"runs": list(RUNS.values())}

@app.get("/api/runs/{run_id}")
def get_run(run_id: str):
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

@app.post("/api/runs/{run_id}/execute")
def execute_run(run_id: str):
    run = RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    results = execute_testplan("testplans/thermal_smoke.yaml")
    run["status"] = "completed"
    run["results"] = results
    return run

@app.get("/api/metrics")
def metrics():
    total = len(RUNS)
    completed = sum(1 for r in RUNS.values() if r["status"] == "completed")
    return {
        "total_runs": total,
        "completed_runs": completed,
        "pending_runs": total - completed,
    }
