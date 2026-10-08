# ModelSentinel

**ModelSentinel** is an AI-powered ML reliability engineering platform. It is designed to take an ML incident through its complete lifecycle: from model failure to validated, human-approved code change. 

## Core Product Workflow

1. **Monitor & Detect:** Watch for ML anomalies or drift.
2. **Investigate & Find Root Cause:** Deep dive into failures.
3. **Identify Affected Code:** Trace issues back to the specific ML code or data pipelines.
4. **Propose Multi-File Fix:** AI-assisted suggestion of necessary code modifications.
5. **Human Review & Validation:** Engineers review the fix within a sandbox environment.
6. **Regression Test Generation:** Automatically create tests to prevent recurrence.
7. **Pull Request:** Ship the fix securely.

## Current Architecture

The architecture emphasizes maintainability, strong typing, and standard industry practices without unnecessary microservices.

- **Frontend:** A single-page application communicating with the REST API.
- **Backend:** A monolithic REST API providing the core services.
- **Database:** Relational storage for all entities, designed for future vector capabilities (pgvector).

## Technology Stack

- **Frontend:** React, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query.
- **Backend:** Python, FastAPI, Pydantic, SQLAlchemy, Alembic.
- **Infrastructure:** Docker, Docker Compose, PostgreSQL.

## Setup and Demo

The infrastructure has been finalized for easy demonstration.
For a complete guide to running the presentation demo, please refer to:
[DEMO.md](DEMO.md)

For detailed deployment instructions (Demo vs Production modes, PostgreSQL vs SQLite):
[DEPLOYMENT.md](DEPLOYMENT.md)

**Quick Start (Demo Mode):**
```bash
./demo start
./demo seed
```

## Repository Structure

```
ModelSentinel/
├── frontend/           # React frontend application
├── backend/            # FastAPI backend application
│   ├── app/            # Application code
│   └── tests/          # Backend test suite
├── docs/               # Project documentation
├── scripts/            # Helper and deployment scripts
├── docker-compose.yml  # Local development environment
└── README.md           # This file
```

## Development Commands

**Frontend (Local):**
```bash
cd frontend
npm install
npm run dev
npm run lint
```

**Backend (Local):**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Current Project Status

**Phase 0 / Foundation:** Complete. Basic project structure and Docker infrastructure established.

**Phase 1 / Premium Product UI Foundation:** Complete. Established central design-token support, Tailwind CSS integrations, and highly modular React components mimicking the amber/orange dark theme of the design reference.

**Phase 2 / Real ML Model Management Foundation:** Complete. Implemented model registry full-stack (SQLAlchemy models for Model, ModelVersion, ModelMetric, FastAPI endpoints, and React frontend API integrations with modals).

**Phase 3 / ML Monitoring & Deterministic Evaluation:** Complete.
- **Monitoring Architecture**: A synchronous, deterministic monitoring runner in the FastAPI backend that compares current window data to baseline data (CSV).
- **Supported Metrics**: Classification metrics (Accuracy, Precision, Recall, F1, ROC-AUC).
- **Drift Methods**: KS Statistic (Numerical features), PSI (Population Stability Index for Numerical, Categorical features, and Prediction drift).
- **Baseline/Current Concept**: Compares a reference `baseline` dataframe against a recent `current` dataframe to extract drift and performance degradation.
- **Data Quality**: Evaluates Missing Values, Duplicate Rows, and Invalid Data.
- **Segment Analysis**: Evaluates standard ML metrics over dynamically filtered segments (e.g. `url_count > 2`).
- **Monitoring Endpoints**: RESTful `POST /api/v1/models/{id}/monitoring/runs` orchestrates the run and GET variants retrieve the persisted metric, drift, quality, and segment tables.
- **Demo Dataset**: Seed script generates dummy CSVs `email-spam-classifier_baseline.csv` and `email-spam-classifier_current.csv` with synthetic performance degradation and feature drift for demonstration.
- **Thresholds**: Defined in `thresholds.py`. Signals are mapped to `healthy`, `warning`, or `critical`. (e.g., PSI > 0.25 is critical).