# RackLab-OSH
**Meta-style Hardware Systems Test Harness (API + Worker + Simulator + YAML Test Plans)**

> A production-style validation harness that models how hardware systems engineers run system-level thermal/power smoke tests, track run state, generate procedural logs, and communicate results across hardware, firmware, and software teams.

---

## Live Demo
Swagger UI: https://racklab-osh-1.onrender.com/docs  
Health: https://racklab-osh-1.onrender.com/health  

Note: Free-tier deployments may take ~20–30 seconds to wake up.

---

## Why This Project
Real server bring-up and hardware validation is not CRUD. It involves defining thermal and power test plans, executing repeatable system-level tests, keeping a procedural execution record, and debugging failures with clear signals. RackLab-OSH focuses on this systems validation layer commonly seen in data-center hardware teams.

---

## What This Tool Does
RackLab-OSH provides a minimal but realistic API for hardware test orchestration. It allows creating and tracking test runs, executing YAML-defined system tests via a background worker, simulating rack behavior (fan, load, temperature), producing step-wise PASS/FAIL results, and exposing fleet-style metrics for validation visibility.

---

## Hardware Test Execution
RackLab-OSH supports YAML-driven system-level hardware tests executed by a worker.
- Hardware simulator models thermal and power behavior
- Worker executes test plans step-by-step
- Each step produces a procedural execution log
- Pass/Fail decisions are evaluated against thermal thresholds

This mirrors how real data-center validation teams run rack-level smoke tests before production rollout.

---

## API Surface
GET /health – Liveness probe  
POST /api/runs – Create a new run  
GET /api/runs – List runs  
GET /api/runs/{run_id} – Run details  
POST /api/runs/{run_id}/execute – Execute YAML test plan (worker + simulator)  
GET /api/metrics – Aggregate metrics  

---

## 60-Second Demo
1. Open /docs
2. Call GET /health → {"status":"ok"}
3. Create a run using POST /api/runs with:
   {"name":"thermal_smoke","notes":"render demo"}
4. Copy the returned run_id
5. Call POST /api/runs/{run_id}/execute
6. Fetch results via GET /api/runs/{run_id}
7. Check system metrics via GET /api/metrics

---

## Test Plan Format
Example test plan (thermal_smoke.yaml):
- Set fan speed
- Apply load for a fixed duration
- Read temperature and evaluate against threshold

This follows the control → stress → measure → decide pattern used in hardware validation.

---

## System Design
Client (Swagger / scripts) calls a FastAPI service that orchestrates runs and exposes metrics.  
The execute endpoint triggers a worker that reads a YAML test plan and executes it step-by-step.  
The worker interacts with a hardware simulator that models fan control, power load, and temperature sensing.  
Each step returns procedural logs and PASS/FAIL outcomes.

---

## Repository Layout
app/ – FastAPI service  
worker/ – YAML test executor  
simulator/ – Thermal/power rack simulator  
testplans/ – YAML test plans  
requirements.txt – Python dependencies  

---

## Tech Stack
Python 3  
FastAPI  
Uvicorn  
PyYAML  
Render (deployment)

---

## Reliability Notes
Procedural step-wise execution logs  
Deterministic PASS/FAIL evaluation  
Clear API contracts via Swagger  

Future upgrades include SQLite persistence, async job queues, failure injection, and report export.

---

## Local Run 
pip install -r requirements.txt  
uvicorn app.main:app --host 0.0.0.0 --port 8000  
Open http://localhost:8000/docs

---

## Render Deploy Settings
Build Command: pip install -r requirements.txt  
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT  
