# RackLab-OSH

Meta-style Hardware Systems test harness demo API (minimal deployable version).

## Live Demo
After deploying on Render, open:
- `/docs` (Swagger UI)
- `/health`

Example:
`https://<your-service>.onrender.com/docs`

## Endpoints
- `GET /health`
- `POST /api/runs` (create a run)
- `GET /api/runs` (list runs)
- `GET /api/runs/{id}` (run detail)
- `POST /api/runs/{id}/simulate_complete` (demo helper)
- `GET /api/metrics` (basic metrics)

## Local Run
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
