# ModelSentinel

**ModelSentinel** is an AI-powered ML reliability engineering platform. It is designed to take an ML incident through its complete lifecycle: from model failure detection to a validated, human-approved code change.

## Problem Statement

When a machine learning model degrades in production, engineering teams face a fragmented workflow: detecting the anomaly, investigating the root cause across data/code, reproducing the issue, developing a patch, and securely deploying it. ModelSentinel unifies this process.

## Key Capabilities

- **Real-time Monitoring & Alerts**: Detects data drift (PSI, KS Statistic) and performance degradation.
- **Incident Management**: Automatically escalates alerts into actionable incidents.
- **AI Investigations**: Deep-dives into failures by analyzing telemetry, data quality, and causal graphs.
- **Automated Patch Proposals**: Generates multi-file code fixes based on investigation findings.
- **Validation & Regression Analysis**: Safely tests patches against historical regression suites.
- **Deployment Gates**: Controls deployment promotion based on ML health checks and CI/CD policies.
- **Reliability Analytics**: Tracks organizational SLOs, MTTR, and engineering intelligence.
- **Python CLI**: Interact with models, incidents, and deployments directly from the terminal.

## Technology Stack

- **Frontend**: React, TypeScript, Vite, Tailwind CSS, React Router
- **Backend**: Python, FastAPI, Pydantic, SQLAlchemy, Alembic
- **Database**: PostgreSQL (Production) / SQLite (Local Demo)
- **Infrastructure**: Docker, Docker Compose

## Repository Structure

```
ModelSentinel/
├── backend/            # FastAPI REST API, database models, and ML intelligence services
├── cli/                # Python CLI tool for developers
├── docs/               # Architecture, Deployment, and Configuration documentation
├── frontend/           # React SPA frontend application
├── scripts/            # Helper scripts (admin creation, demo seeding)
├── demo.cmd / demo     # Entry points for running the local demo
├── docker-compose.yml  # Base Docker configuration
└── docker-compose.demo.yml # Local SQLite-based demo overrides
```

## System Requirements

- **Docker** and **Docker Compose**
- **Node.js** (v18+) and npm (for frontend development)
- **Python 3.10+** (for backend/CLI development)

## Quick Start (Local Demo)

The repository includes a self-contained SQLite demo environment with pre-seeded data showcasing the complete hero workflow (Spam Classifier failure).

1. **Start the environment:**
   ```bash
   ./demo start
   ```
2. **Seed the database:**
   ```bash
   ./demo seed
   ```
3. **Access the application:**
   - Frontend: [http://localhost:5173](http://localhost:5173)
   - Backend API: [http://localhost:8000/api/v1](http://localhost:8000/api/v1)
   - Login with: `admin@modelsentinel.local` / `StrongDemoPassword123!`

For more details, see [docs/DEMO.md](docs/DEMO.md).

## Development Setup

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## CLI Usage

The Python CLI (`modelsentinel`) interacts with the backend.

```bash
cd cli
pip install -e .

# Authenticate
modelsentinel --api-url http://localhost:8000 auth login

# List active models
modelsentinel --api-url http://localhost:8000 models list

# View incident details
modelsentinel --api-url http://localhost:8000 incidents view <INCIDENT_ID>
```
For more commands, see [docs/CLI.md](docs/CLI.md).

## Testing

Run the test suites to verify functionality:

**Backend:**
```bash
cd backend
pytest tests/
```

**Frontend:**
```bash
cd frontend
npm run lint
npm run build
```

**CLI:**
```bash
cd cli
pytest tests/
```

## Security Considerations

- **Secrets**: Never commit `.env` files or API keys. Use `.env.example` as a template.
- **Admin Accounts**: The bootstrap script uses a temporary hardcoded password for the demo environment. Rotate this immediately in production.
- **Environment**: The local demo uses SQLite without strict transport security. Production deployments MUST use PostgreSQL and HTTPS.

## Limitations and Work-in-Progress

- **AI Investigation**: Fully implemented with the Groq provider via structured output generation and tool-calling. It is not simulated at runtime. A valid LLM API key must be configured, otherwise active investigations will gracefully fail with an error. (Note: The demo environment is pre-seeded with historical completed investigations for visualization).
- **GitHub Integrations**: Fully implemented. Webhook listeners (with HMAC signature verification and idempotency logic) and REST API PR interactions are strictly live and credential-dependent. They are not mocked. Active Git interactions require a valid GitHub Token and configured Webhook Secret.


## License

*(A license decision is currently pending. Please do not use in production without explicit authorization.)*