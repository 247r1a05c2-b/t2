# TraceGaurd — Multi-Agent AI Incident Commander

TraceGaurd is a hackathon-ready incident operations platform for software engineers and SRE teams. It ingests client signals, correlates operational evidence, retrieves runbook knowledge with RAG, produces an evidence-backed root-cause hypothesis, exposes the diagnostic path, classifies remediation with a default-deny guardrail, and requires explicit human approval before a production-style action can execute.

## Core flow

Client signals → Ingestion → Noise filtering → Correlation → RAG → Root Cause → Diagnostic Steps → Guardrail → Human Approval → Controlled Executor → Audit Trail.

## Included

- Software engineer login with signed sessions
- Client monitoring and heartbeats
- Multi-agent investigation trace
- RAG runbook retrieval
- Root-cause confidence percentage
- Diagnostic steps and evidence
- Default-deny remediation guardrails
- Human approval gate
- Simulated allow-listed remediation executor
- Persistent SQLite locally / PostgreSQL when `DATABASE_URL` is provided
- Responsive React dashboard
- Vercel FastAPI entrypoint
- Local Docker support

## Run locally

Backend:

```bash
cd backend
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Demo login: `engineer@tracegaurd.ai` / `TraceGaurd@123`

## PostgreSQL / Vercel

Set `DATABASE_URL` to a PostgreSQL connection string for persistent deployment. Keep `TRACEGAURD_SECRET`, `DEMO_ENGINEER_EMAIL`, and `DEMO_ENGINEER_PASSWORD` in deployment environment variables. The backend can be deployed as a Vercel Python function from `backend/vercel.json`.

## Tests

```bash
cd backend
pytest -q
```
