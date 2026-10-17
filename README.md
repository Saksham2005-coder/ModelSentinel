<div align="center">

# ModelSentinel

**An ML Reliability Control Plane**

*Monitor model health. Investigate failures. Validate fixes. Enforce reliability.*

[![Live Demo](https://img.shields.io/badge/Demo-Live%20Platform-f59e0b?style=for-the-badge&logo=railway&logoColor=white)](https://frontend-production-b9b9.up.railway.app)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Saksham2005-coder/ModelSentinel)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.103-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-18.2-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.3-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com)

---

### [🚀 Explore Live Demo (Hosted on Railway)](https://frontend-production-b9b9.up.railway.app)

> **Demo Access Credentials:**
> - **Email:** `admin@modelsentinel.local`
> - **Password:** `StrongDemoPassword123!`
>
> *(The live deployment hosts an active, pre-seeded production environment featuring model health monitoring, multi-stage investigations, regression suites, change-risk intelligence, and workflow runs.)*

---

</div>

## Table of Contents

- [What is ModelSentinel?](#what-is-modelsentinel)
- [The Problem It Solves](#the-problem-it-solves)
- [Key Features](#key-features)
- [Architecture Overview](#architecture-overview)
- [End-to-End Incident Lifecycle](#end-to-end-incident-lifecycle)
- [How It Works](#how-it-works)
- [Technology Stack](#technology-stack)
- [Repository Structure](#repository-structure)
- [Getting Started Locally](#getting-started-locally)
  - [Prerequisites](#prerequisites)
  - [Automated Demo Quick Start](#automated-demo-quick-start)
  - [Manual Development Setup](#manual-development-setup)
- [Configuration](#configuration)
- [CLI Reference](#cli-reference)
- [Testing & Quality Checks](#testing--quality-checks)
- [Production Deployment](#production-deployment)
- [Security & Responsible Use](#security--responsible-use)
- [Current Limitations & Operational Notes](#current-limitations--operational-notes)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License & Acknowledgments](#license--acknowledgments)

---

## What is ModelSentinel?

**ModelSentinel** is an open, unified **ML Reliability Control Plane** designed to bridge the gap between machine learning operations and software engineering.

In contemporary production systems, machine learning models rarely fail with catastrophic server crashes. Instead, they degrade **silently**—input feature distributions drift, upstream schema contracts break, categorical values go missing, or subtle code changes introduce edge-case exceptions. Traditional observability platforms stop at alerting engineers that an metric dropped (such as *"F1 score dropped by 18%"*). They leave engineers to manually correlate telemetry, search git histories, hypothesize root causes, hand-craft bug fixes, and guess whether a patch causes regressions elsewhere.

ModelSentinel unifies this entire incident lifecycle into a connected, systematic platform:
1. **Detects** telemetry anomalies, distribution drift (PSI, Kolmogorov-Smirnov), and data-quality violations.
2. **Escalates** alerts into deduplicated, prioritized incidents linked to model versions and data slices.
3. **Investigates** root causes by combining deterministic diagnostic tool calls with AI-driven hypothesis formation.
4. **Analyzes Code Impact** using AST-level repository indexing, symbol dependency parsing, and blast-radius scoring.
5. **Generates & Validates Patches** in isolated validation environments against historical regression test cases.
6. **Enforces Reliability Gates** in CI/CD deployment pipelines and indexes validated solutions into persistent **Incident Memory**.

---

## The Problem It Solves

```
Fragmented Traditional ML Workflow:
[ Telemetry Alert ] ──> (Manual Log Diving) ──> (Ad-Hoc Jupyter Debugging) ──> (Blind Git PR) ──> (Unverified Deployment)
                                                                                                        │
                                                                                        (Silent Secondary Regression)

ModelSentinel Unified Control Plane:
[ Telemetry Alert ] ──> [ Deterministic Evidence ] ──> [ AI Hypothesis Engine ] ──> [ AST Blast Radius ]
                                                                                             │
[ Incident Memory ] <── [ Post-Deploy Verify ] <── [ Deployment Gates ] <── [ Sandbox Validation ]
```

| Operational Challenge | Traditional Approach | ModelSentinel Solution |
| :--- | :--- | :--- |
| **Silent Performance Loss** | Disconnected dashboards; engineers notice drops days or weeks after deployment. | Automated daily/hourly window evaluation tracking drift (PSI, KS), slice metrics, and data quality checks against strict SLOs. |
| **Root Cause Investigation** | Manual, ad-hoc investigation across disparate logs, metrics, data dumps, and commit logs. | Automated evidence gathering via tool registry; structured AI hypotheses verified against actual metrics and distributions. |
| **Code vs. Data Disconnect** | Telemetry monitors have zero awareness of the repository code producing the features. | AST-aware code indexer correlates changed symbols, functions, and feature pipelines directly to telemetry drops. |
| **High Blast-Radius Fixes** | Engineers rush emergency fixes without knowing what downstream models depend on the code. | Deterministic change-risk calculation scores patches (0–100) and computes blast radius across files, models, and features. |
| **Repetitive Regressions** | Post-mortems live in static Google Docs; previously fixed bugs reappear in new model retraining runs. | Synthesizes resolved incidents into executable **Regression Test Suites** and searchable **Incident Memory** patterns. |

---

## Key Features

### 1. Model Registry & Multi-Task Monitoring
- Registers models across diverse frameworks (**HuggingFace**, **PyTorch**, **LightGBM**, **Scikit-Learn**, **XGBoost**).
- Tracks classification, regression, and ranking tasks with customizable primary metrics ($F_1$, ROC-AUC, RMSE, Accuracy).
- Calculates statistical data drift:
  - **Population Stability Index (PSI)** for categorical and numerical features.
  - **Two-sample Kolmogorov-Smirnov (KS) test** for continuous feature distributions.
- Monitors data quality rules (null rate, range boundaries, distinct count shifts) and slice/segment performance.

### 2. Incident Management & Alerting
- Escalates threshold breaches into structured, deduplicated incidents with severity ratings (`critical`, `high`, `medium`, `low`).
- Provides chronological event streams, affected segment tags, and timeline tracking.
- Interactive status workflows: **Acknowledge**, **Investigate**, **Resolve**, or **Suppress**.

### 3. Investigation Orchestrator & AI Provider Abstraction
- Executes deterministic evidence collection using an internal diagnostic tool registry:
  - `get_incident_context`, `get_monitoring_run`, `get_performance_metrics`
  - `get_feature_drift`, `get_prediction_drift`, `get_segment_analysis`, `get_data_quality`
- Pluggable `LLMProvider` abstraction (implemented with **Groq** using `llama-3.1-8b-instant`) generates structured, Pydantic-validated hypotheses and tests them against collected telemetry evidence.

### 4. Repository Indexing & Change Intelligence
- Clones and indexes code snapshots down to symbol level (functions, classes, imports, pipelines).
- Calculates deterministic **Change Risk Scores** (0–100) based on modified AST nodes, API contract preservation, and test coverage.
- Evaluates **Blast Radius** by identifying downstream dependent models, feature extractors, and historical failure correlations.

### 5. Automated Patch Proposals & Isolated Validation
- Proposes precise, multi-file code diffs addressing verified incident root causes.
- Runs an isolated `ValidationRunner` that applies diffs in a temporary sandbox, executes test checks, compares candidate metric improvements against baseline thresholds, and produces an actionable validation verdict (`PASSED`, `FAILED`, `INCONCLUSIVE`).

### 6. Regression Suites & Persistent Incident Memory
- Automatically synthesizes edge cases from resolved incidents into persistent regression test suites.
- Prevents re-emergence of past failures during subsequent model retraining or prompt engineering iterations.
- Searchable vector and text knowledge base of incident resolutions and historical effectiveness scores.

### 7. Deployment Promotion Gates & CI/CD Policies
- Verifies that model deployments satisfy defined governance policies (e.g., minimum validation accuracy, maximum acceptable feature drift, required human approvals).
- Tracks pull requests, checks verification statuses, and controls rollouts across staging and production.

### 8. Enterprise Developer CLI (`modelsentinel`)
- Standalone Python CLI built with Typer for terminal-centric developers and automated CI/CD pipelines.
- Supports authentication, model listing, incident inspection, telemetry upload, risk evaluations, and workflow runs.

---

## Architecture Overview

ModelSentinel is built as a cohesive, layered platform. The frontend communicates with a modular FastAPI service layer backed by relational persistence, an isolated validation runtime, and an AI provider abstraction.

```mermaid
flowchart TB
    subgraph Clients["Presentation & Interface Layer"]
        UI["React 18 + Vite Web Application\n(Tailwind CSS, Lucide, Recharts)"]
        CLI["ModelSentinel CLI\n(Python 3.10+, Typer, Rich Tables)"]
    end

    subgraph API["FastAPI API & Gateway Layer (/api/v1)"]
        Router["REST Router & Request Validation\n(Pydantic V2 Schemas)"]
        AuthMid["Security Middleware\n(OAuth2, JWT, RBAC Permissions)"]
    end

    subgraph Services["Core Application Services"]
        ModelSvc["Model & Telemetry Service\n(PSI & KS Drift Calculation)"]
        IncidentSvc["Incident & Alert Escalator\n(Deduplication & SLO Checking)"]
        InvestigateSvc["Investigation Orchestrator\n(Deterministic Tool Registry)"]
        RepoSvc["Repository & AST Parser\n(Symbol Extraction & Dependency Graph)"]
        ChangeRiskSvc["Change Risk & Blast Radius Engine\n(Deterministic Scoring 0-100)"]
        PatchSvc["Patch Proposal & Validator\n(Sandbox Diff Runner)"]
        RegressionSvc["Regression Test Suite Engine\n(Incident-to-Test Synthesis)"]
        WorkflowSvc["Workflow Orchestrator\n(Multi-step Recovery Pipelines)"]
    end

    subgraph AI["Intelligence Provider Layer"]
        LLMBase["LLMProvider Interface\n(Structured JSON & Tool Calling)"]
        GroqImpl["Groq Provider\n(llama-3.1-8b-instant)"]
    end

    subgraph Storage["Persistence & Storage Layer"]
        DB[("Database Engine\nPostgreSQL 15 (Prod) / SQLite (Demo)\nSQLAlchemy 2.0 ORM + Alembic")]
        RepoStore["Repository Snapshot Store\n(Local Disk / Volume Snapshot)"]
    end

    subgraph Ext["External Integrations (Live / Optional)"]
        GH["GitHub API & Webhooks\n(HMAC SHA-256 Verified)"]
        AlertSink["Notification Sinks\n(PagerDuty / Slack / Email)"]
    end

    UI <-->|HTTPS / JSON REST| Router
    CLI <-->|HTTPS / JSON REST| Router
    Router --> AuthMid
    AuthMid --> Services

    ModelSvc --> DB
    IncidentSvc --> DB
    InvestigateSvc --> DB
    InvestigateSvc --> LLMBase
    RepoSvc --> RepoStore
    RepoSvc --> DB
    ChangeRiskSvc --> RepoSvc
    PatchSvc --> RepoStore
    PatchSvc --> DB
    RegressionSvc --> DB
    WorkflowSvc --> DB

    LLMBase --> GroqImpl
    IncidentSvc -.-> AlertSink
    RepoSvc -.-> GH
```

---

## End-to-End Incident Lifecycle

The following diagram illustrates the complete, deterministic lifecycle supported by ModelSentinel—from real-time telemetry anomaly detection to human-approved production promotion:

```mermaid
flowchart TD
    A["1. Telemetry Ingestion\n(Batch / Live Prediction CSVs)"] --> B{"2. Signal Evaluation\n(PSI > 0.25, KS p < 0.01,\nAccuracy < Threshold)"}
    
    B -->|Within SLOs| A
    B -->|SLO Breach / Degradation| C["3. Incident Escalation\n(Deduplication & Severity Tagging)"]
    
    C --> D["4. Evidence Collection\n(Diagnostic Tool Registry Queries Telemetry, Drift & Slices)"]
    
    D --> E["5. AI Hypothesis Formulation\n(Groq LLM Generates & Verifies Root Cause Hypotheses)"]
    
    E --> F["6. Repository & AST Code Impact\n(Parser correlates affected symbols, functions, and pipelines)"]
    
    F --> G["7. Blast Radius & Change Risk Assessment\n(Calculates 0-100 Risk Score & Identifies Dependent Models)"]
    
    G --> H["8. Automated Multi-File Patch Generation\n(Proposes structured diff to remedy root cause)"]
    
    H --> I["9. Sandbox Validation Run\n(Applies patch in isolated environment & tests against edge cases)"]
    
    I --> J{"10. Validation Verdict"}
    J -->|Failed / Regressed| H
    J -->|Passed| K["11. Human-in-the-Loop Review\n(Engineer approves proposed code change & PR)"]
    
    K --> L["12. Deployment Gate & CI Promotion\n(Verifies SLO error budget & policy compliance)"]
    
    L --> M["13. Post-Deployment Verification\n(Live canary monitoring of updated model)"]
    
    M --> N["14. Incident Memory Indexing\n(Synthesizes regression test & stores resolution vector)"]

    style A fill:#1e293b,stroke:#475569,stroke-width:1px,color:#f8fafc
    style C fill:#451a03,stroke:#b45309,stroke-width:1px,color:#fef3c7
    style E fill:#1e1b4b,stroke:#4338ca,stroke-width:1px,color:#e0e7ff
    style G fill:#2e1065,stroke:#7e22ce,stroke-width:1px,color:#f3e8ff
    style I fill:#064e3b,stroke:#047857,stroke-width:1px,color:#ecfdf5
    style K fill:#78350f,stroke:#d97706,stroke-width:2px,color:#fffbeb
    style L fill:#064e3b,stroke:#059669,stroke-width:1px,color:#ecfdf5
    style N fill:#1e293b,stroke:#3b82f6,stroke-width:1px,color:#eff6ff
```

---

## How It Works

ModelSentinel organizes reliability engineering into five distinct, sequential phases:

### Phase 1: Signal Observation & Anomaly Ingestion
When models execute inference in production, prediction logs and ground-truth labels are ingested via REST or batch upload. The monitoring engine computes sliding-window statistics across data distributions, drift metrics, and target evaluations. If metric thresholds breach defined Service Level Objectives (SLOs), alerts trigger and automatically escalate into a single, deduplicated incident record.

### Phase 2: Evidence Gathering & Diagnostic Hypothesis Formation
When an engineer triggers or inspects an incident investigation:
1. The **Investigation Orchestrator** pulls deterministic diagnostics via registered tools (querying exact feature drift percentiles, slice failure rates, and categorical null counts).
2. The **AI Provider** evaluates this factual context, forming structured hypotheses (e.g., *"Unhandled Unicode emoji inputs cause tokenization pipeline truncation"*).
3. The model tests each hypothesis against telemetry data, marking hypotheses as **Confirmed**, **Refuted**, or **Inconclusive**.

### Phase 3: Codebase AST Indexing & Change Risk Analysis
ModelSentinel inspects the snapshot of the code repository linked to the model version:
1. The **AST Parser** extracts symbol trees, function definitions, docstrings, and import hierarchies.
2. The **Relevance Engine** matches incident error signatures and affected features against repository files.
3. The **Change Risk Engine** deterministically scores proposed modifications based on contract alterations, module isolation, and downstream model dependencies.

### Phase 4: Patch Proposal & Sandbox Validation
1. An automated, multi-file code diff is synthesized to address the confirmed root cause.
2. A temporary sandbox environment (`ValidationEnvironment`) is instantiated.
3. The patch is applied and executed against synthetic edge cases and historical regression vectors.
4. If validation succeeds without performance regression, the patch is presented with full evidence to the engineering team for human-in-the-loop review.

### Phase 5: CI Promotion & Memory Retention
1. Upon engineer approval, the fix is linked to a Pull Request or deployment gate.
2. The gate validates policy constraints and promotes the model version.
3. The resolution strategy is synthesized into a permanent **Regression Test Case** and indexed into **Incident Memory**, ensuring the organization never repeats the same failure pattern.

---

## Technology Stack

| Domain | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend Framework** | [React 18.2](https://react.dev) | Modern component architecture, hooks, and responsive UX |
| **Language (Web)** | [TypeScript 5.0](https://www.typescriptlang.org) | End-to-end static typing across all UI interfaces |
| **Styling & Design System** | [Tailwind CSS 3.3](https://tailwindcss.com) | Custom dark/amber enterprise UI, glassmorphism, responsive grid |
| **UI Primitives & Icons** | [Radix UI](https://www.radix-ui.com) & [Lucide React](https://lucide.dev) | Accessible primitives, accessible dialogs, and enterprise iconography |
| **Data Visualization** | [Recharts 3.10](https://recharts.org) | Time-series telemetry graphs, drift distributions, SLO burn rates |
| **Build Tooling** | [Vite 4.4](https://vitejs.dev) | Lightning-fast HMR and optimized production bundling |
| **Backend Framework** | [FastAPI 0.103](https://fastapi.tiangolo.com) | High-performance asynchronous REST endpoints with OpenAPI autodocs |
| **Language (Core)** | [Python 3.10+](https://python.org) | Core engineering platform, scientific analysis, and CLI |
| **Data Validation** | [Pydantic V2 (2.4.2)](https://docs.pydantic.dev) | Strict schema validation, settings management, and structured AI outputs |
| **Database & ORM** | [SQLAlchemy 2.0](https://www.sqlalchemy.org) & [Alembic](https://alembic.sqlalchemy.org) | Database abstraction layer with declarative models and versioned migrations |
| **Database Engines** | [PostgreSQL 15](https://www.postgresql.org) & [SQLite](https://www.sqlite.org) | PostgreSQL for multi-user production; SQLite for zero-config local demo |
| **ML & Statistics** | [Scikit-Learn](https://scikit-learn.org), [SciPy](https://scipy.org), [Pandas](https://pandas.pydata.org) | Statistical drift calculations (PSI, Kolmogorov-Smirnov), slice analytics |
| **AI / LLM Provider** | [Groq SDK](https://groq.com) (`llama-3.1-8b-instant`) | Structured hypothesis formation, reasoning, and automated patch synthesis |
| **CLI Framework** | [Typer](https://typer.tiangolo.com) & [Rich](https://rich.readthedocs.io) | Terminal developer interface, colored output, formatting, and tables |
| **Containerization** | [Docker](https://www.docker.com) & [Docker Compose](https://docs.docker.com/compose/) | Isolated multi-container environments for local development and demo |
| **Cloud Hosting** | [Railway](https://railway.app) | Production PaaS hosting for backend API, frontend SPA, and PostgreSQL |

---

## Repository Structure

```
ModelSentinel/
├── backend/                        # FastAPI Core Platform & ML Reliability Engine
│   ├── app/
│   │   ├── ai/                     # LLMProvider abstraction & Groq implementation
│   │   ├── api/v1/endpoints/       # REST route handlers (models, incidents, patches, etc.)
│   │   ├── core/                   # Security, JWT tokens, configuration settings
│   │   ├── db/                     # SQLAlchemy session & base declarations
│   │   ├── incidents/              # Incident escalation, deduplication, triage
│   │   ├── investigation/          # Orchestrator, diagnostic tool registry, schemas
│   │   ├── models/                 # 23 SQLAlchemy declarative database models
│   │   ├── monitoring/             # PSI/KS statistical calculations & metric runner
│   │   ├── patch/                  # Multi-file patch generator, risk, and validator
│   │   ├── repository/             # AST indexer, symbol parser, change intelligence
│   │   ├── schemas/                # Pydantic request and response contracts
│   │   ├── services/               # Reliability analytics, SLO engine, Git service
│   │   ├── validation/             # Isolated sandbox environment and runner
│   │   └── workflows/              # Incident recovery workflow orchestrator
│   ├── data/                       # Cloned repository snapshots & storage volumes
│   ├── tests/                      # 31 Pytest test modules
│   ├── Dockerfile                  # Production container definition
│   └── requirements.txt            # Python dependencies
│
├── frontend/                       # React 18 + TypeScript Web Application
│   ├── public/                     # Static assets, branding, favicons
│   ├── src/
│   │   ├── components/             # Reusable UI elements, badges, charts, graphs
│   │   ├── contexts/               # Global state (Authentication, Toast notifications)
│   │   ├── layouts/                # AppLayout, navigation sidebar, header
│   │   ├── pages/                  # 30+ dedicated application pages (Monitoring, Incidents, etc.)
│   │   ├── services/api/           # Type-safe API client & demo fallback data
│   │   ├── App.tsx                 # Client-side router configuration
│   │   └── index.css               # Design tokens, amber palette, glassmorphism utilities
│   ├── package.json                # Frontend dependencies & npm scripts
│   └── vite.config.ts              # Vite build and proxy settings
│
├── cli/                            # ModelSentinel Developer CLI Package
│   ├── modelsentinel/
│   │   ├── commands/               # Typer subcommands (models, incidents, slo, prs, etc.)
│   │   ├── client.py               # Authenticated API client
│   │   ├── config.py               # CLI local configuration & token storage
│   │   └── main.py                 # CLI entry point
│   ├── tests/                      # CLI unit tests
│   └── pyproject.toml              # CLI packaging and dependencies
│
├── docs/                           # Technical Documentation
│   ├── ARCHITECTURE.md             # System architecture & component breakdown
│   ├── CLI.md                      # CLI usage, command syntax, and flags
│   ├── CONFIGURATION.md            # Complete environment variable specification
│   ├── DEMO.md                     # Deterministic hero presentation flow
│   ├── DEPLOYMENT.md               # Production deployment runbook
│   ├── SECURITY.md                 # Security policies, secrets, and auth standards
│   └── TESTING.md                  # Test suites, coverage, and execution instructions
│
├── scripts/                        # Automation & Administrative Tooling
│   ├── create_admin.py             # Administrator account creation utility
│   ├── demo.py                     # Demo orchestration runner (start, seed, reset)
│   └── seed_demo_environment.py    # Database seeder with complete hero flow
│
├── demo.cmd                        # Windows one-click demo launcher
├── demo                            # Unix/macOS one-click demo launcher
├── docker-compose.yml              # Base Docker Compose configuration (PostgreSQL)
└── docker-compose.demo.yml         # Self-contained SQLite local demo Compose override
```

---

## Getting Started Locally

ModelSentinel provides two ways to run locally:
1. **Automated Demo Mode:** A zero-config containerized SQLite environment with pre-seeded models, incidents, and telemetry.
2. **Manual Development Mode:** Running the FastAPI backend and Vite frontend as independent services.

### Prerequisites

Ensure you have installed:
- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)
- [Python 3.10+](https://python.org) (for local backend development or CLI usage)
- [Node.js 18+](https://nodejs.org) and `npm` (for local frontend development)

---

### Automated Demo Quick Start

The fastest way to experience ModelSentinel is using the built-in demo orchestration script:

#### On Windows:
```cmd
# 1. Start the containers
.\demo.cmd start

# 2. Seed the database with demo data (hero incident, models, telemetry)
.\demo.cmd seed

# 3. Check status
.\demo.cmd status
```

#### On Linux / macOS:
```bash
# 1. Make demo executable & start containers
chmod +x ./demo
./demo start

# 2. Seed the database with demo data
./demo seed

# 3. Check status
./demo status
```

#### Access Points:
- **Frontend Web UI:** [http://localhost:5173](http://localhost:5173)
- **Backend API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Endpoint:** [http://localhost:8000/health](http://localhost:8000/health)
- **Default Admin Credentials:**
  - **Email:** `admin@modelsentinel.local`
  - **Password:** `StrongDemoPassword123!`

To reset or stop the demo environment:
```bash
# Reset database back to clean state
./demo reset

# Stop containers
./demo stop
```

---

### Manual Development Setup

If you prefer to run services natively on your host machine without Docker:

#### 1. Backend Setup

```bash
cd backend

# Create and activate a Python virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp ../.env.example .env

# Run database migrations
alembic upgrade head

# Bootstrap the initial administrator user
python ../scripts/create_admin.py --demo

# Start the FastAPI development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Frontend Setup

In a separate terminal:

```bash
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```

The frontend will start at `http://localhost:5173` with automatic hot-module reloading and proxy API requests to `http://localhost:8000`.

---

## Configuration

ModelSentinel reads configuration via environment variables. For local development, copy `.env.example` to `.env`.

### Environment Variable Reference

| Variable Name | Default Value | Sensitivity | Description |
| :--- | :--- | :---: | :--- |
| `PROJECT_NAME` | `ModelSentinel API` | Public | Name displayed in OpenAPI documentation |
| `API_V1_STR` | `/api/v1` | Public | Base prefix for all API version 1 endpoints |
| `SECRET_KEY` | *(Generated string)* | **Secret** | Cryptographic key used to sign OAuth2 JWT tokens (Must be $\ge$ 32 bytes in production) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` (24h) | Public | Duration before JWT session expiration |
| `DATABASE_URL` | `sqlite:///./modelsentinel.db` | Public / Secret | Connection URI (`postgresql://user:pass@host:5432/db` for production) |
| `POSTGRES_SERVER` | `db` | Public | Hostname for PostgreSQL service |
| `POSTGRES_USER` | `modelsentinel` | Public | PostgreSQL username |
| `POSTGRES_PASSWORD` | `modelsentinel_password` | **Secret** | PostgreSQL password |
| `POSTGRES_DB` | `modelsentinel` | Public | PostgreSQL database name |
| `POSTGRES_PORT` | `5432` | Public | PostgreSQL listening port |
| `BACKEND_CORS_ORIGINS` | `["http://localhost:5173"]` | Public | JSON list of authorized browser CORS origins |
| `FRONTEND_URL` | `http://localhost:5173` | Public | Public origin of the frontend web application |
| `LLM_PROVIDER` | `groq` | Public | Pluggable LLM provider choice (`groq`) |
| `GROQ_API_KEY` | *(Empty / Optional)* | **Secret** | Groq Cloud API key for live AI investigations |
| `GROQ_MODEL` | `llama-3.1-8b-instant` | Public | LLM model identifier used for structured inference |
| `MODELSENTINEL_GITHUB_TOKEN` | *(Empty / Optional)* | **Secret** | Personal Access Token for live GitHub repository and PR interactions |
| `MODELSENTINEL_GITHUB_WEBHOOK_SECRET` | *(Empty / Optional)* | **Secret** | Secret used to verify incoming GitHub webhook HMAC-SHA256 signatures |

---

## CLI Reference

ModelSentinel includes a production-ready command line interface (`modelsentinel`) built with Typer for terminal workflows and pipeline automation.

### Installation

```bash
cd cli
pip install -e .
```

### Global Options

All CLI commands accept the following global flags:
- `--api-url <URL>`: Override the target backend URL (defaults to `http://localhost:8000`).
- `--json`: Output raw JSON responses instead of formatted tables (ideal for piping to `jq` or CI scripts).
- `--debug`: Enable verbose stack traces on errors.
- `--version`: Display CLI version.

### Command Catalog

```bash
# Authentication & Identity
modelsentinel auth login                 # Authenticate and store JWT session
modelsentinel auth me                    # Print current authenticated user info
modelsentinel auth logout                # Clear local authentication credentials

# Model Operations
modelsentinel models list                # List registered models, framework, and status
modelsentinel models view <MODEL_ID>     # View detailed model metadata and primary metric

# Incident Management
modelsentinel incidents list             # List active incidents filtered by severity
modelsentinel incidents view <INC_ID>    # Detailed incident report, signals, and timeline
modelsentinel incidents acknowledge <ID> # Mark incident as acknowledged

# Telemetry
modelsentinel telemetry list             # List recent telemetry batch uploads
modelsentinel telemetry upload <PATH>    # Ingest a new model telemetry CSV file

# Change Intelligence & Risk
modelsentinel change-intelligence view <PATCH_ID> # Inspect AST diff symbols & blast radius
modelsentinel change-intelligence evaluate        # Trigger deterministic change-risk evaluation

# Patch & Validation
modelsentinel patches list <INV_ID>      # List proposed patches for an investigation
modelsentinel patches view <PATCH_ID>    # Show full unified diff of a patch proposal
modelsentinel validation view <VAL_ID>   # Check validation run verdict and metric changes

# Service Level Objectives & Alerts
modelsentinel slo list                   # List reliability objectives and compliance
modelsentinel slo evaluate <SLO_ID>      # Manually trigger SLO evaluation
modelsentinel alerts list                # List active alert rules and trigger states

# Workflows & Automation
modelsentinel workflows list             # List orchestration workflows
modelsentinel workflows view <WF_ID>     # Inspect multi-step workflow execution graph
modelsentinel workflows start <WF_ID>    # Trigger recovery workflow execution
```

---

## Testing & Quality Checks

ModelSentinel maintains dedicated test suites across the backend, CLI, and frontend:

### Backend Test Suite
The backend test suite contains **31 comprehensive test modules** verifying API routes, anomaly thresholds, migration sanity, AST parsing, and validation execution.

```bash
cd backend
pytest tests/ -v
```

### CLI Test Suite
Validates argument parsing, output formatting, token storage, and mock API communications.

```bash
cd cli
pytest tests/ -v
```

### Frontend Code Quality & Build Verification
Validates TypeScript static types, ESLint rules, and production bundle compilation.

```bash
cd frontend
# Run static lint analysis
npm run lint

# Verify TypeScript compilation and production build
npm run build
```

---

## Production Deployment

### Live Cloud Deployment (Railway)
ModelSentinel is deployed in a multi-service production topology on [Railway](https://railway.app):
- **Frontend SPA:** [https://frontend-production-b9b9.up.railway.app](https://frontend-production-b9b9.up.railway.app)
  - Hosted as a static SPA with dynamic runtime backend detection.
  - Intercepts non-API traffic and gracefully prevents HTML-JSON parsing anomalies.
- **Backend API:** [https://backend-production-cca4.up.railway.app/api/v1](https://backend-production-cca4.up.railway.app/api/v1)
  - Containerized FastAPI service running via Uvicorn.
  - Automatically executes database migrations on startup.
- **PostgreSQL Database:** Managed PostgreSQL 15 instance storing all models, incidents, telemetry, and index data.

### Self-Hosted Docker Compose (PostgreSQL)

For private cloud or on-premise production deployments:

1. Configure production environment variables in `.env`:
   ```env
   POSTGRES_SERVER=db
   POSTGRES_USER=sentinel_admin
   POSTGRES_PASSWORD=your_secure_db_password
   POSTGRES_DB=modelsentinel_production
   SECRET_KEY=your_cryptographically_secure_random_key_here
   FRONTEND_URL=https://modelsentinel.yourcompany.com
   BACKEND_CORS_ORIGINS=["https://modelsentinel.yourcompany.com"]
   GROQ_API_KEY=gsk_your_groq_api_key
   ```

2. Launch via Docker Compose:
   ```bash
   docker compose up -d --build
   ```

3. Bootstrap the initial production administrator:
   ```bash
   docker compose exec backend python /app_data/scripts/create_admin.py
   ```

4. Place an SSL-terminating reverse proxy (such as Nginx, Traefik, or AWS ALB) in front of the application to enforce HTTPS.

---

## Security & Responsible Use

- **Human-in-the-Loop Safeguards:** ModelSentinel is explicitly designed as an **engineering copilot**, not an unconstrained autonomous agent. Patch proposals, validation runs, and deployment gate evaluations **require human engineer review and sign-off** before code can be merged or models promoted.
- **Deterministic vs. Probabilistic Separation:** Critical reliability decisions (such as metric thresholds, drift statistical tests, and blast radius calculations) are computed **deterministically** via Python code and AST parsers. Probabilistic LLM outputs are confined to diagnostic hypothesis generation and patch diff drafts.
- **Secret Hygiene:** Database passwords, JWT signing keys, AI provider credentials, and GitHub tokens must never be committed to source control. Use environment variable injection or a dedicated secrets manager.
- **Webhook Integrity:** All incoming GitHub webhooks are validated using HMAC-SHA256 signatures (`X-Hub-Signature-256`) and idempotency keys to guard against replay attacks.
- **Role-Based Access Control (RBAC):** Backend endpoints enforce granular role permissions (`ADMIN`, `ENGINEER`, `VIEWER`), preventing unauthorized modifications to model registries or deployment gates.

---

## Current Limitations & Operational Notes

To ensure technical credibility, the following known limitations and operational characteristics are documented:

1. **AI Provider Key Prerequisite:** Live AI hypothesis generation and real-time patch synthesis require a valid `GROQ_API_KEY`. If no key is configured, the platform safely falls back to pre-seeded historical investigations without crashing.
2. **GitHub Live vs. Seeded Operations:** The platform contains fully implemented GitHub REST and Webhook handlers. However, active GitHub interactions (such as creating remote pull requests or syncing branches) require a valid `MODELSENTINEL_GITHUB_TOKEN`. In local demo and test environments, git operations utilize local directory snapshots.
3. **Database Concurrency:** The local demo configuration defaults to SQLite for immediate, zero-dependency evaluation. SQLite does not support high-concurrency writes; all team or multi-user deployments must configure PostgreSQL.
4. **Validation Isolation Scope:** The built-in `ValidationRunner` applies diffs to a isolated snapshot on the local filesystem. In high-security multi-tenant production clusters, validation execution should be wrapped inside isolated ephemeral Docker containers or Kubernetes Jobs.

---

## Roadmap

- [ ] **Streaming Telemetry Connectors:** Native Kafka, Kinesis, and OpenTelemetry collectors for real-time inference span streaming.
- [ ] **Multi-Provider AI Fallback:** Expanding the `LLMProvider` interface to support Anthropic Claude, OpenAI, and local Ollama / vLLM instances.
- [ ] **Automated Canary Shadowing:** Shadow-traffic routing to compare candidate patched models against live production traffic before gate promotion.
- [ ] **Expanded ML Task Support:** Pre-configured evaluators for Large Language Model (LLM) hallucinations, RAG retrieval relevance, and embedding drift.
- [ ] **Native Slack & Microsoft Teams Bot:** Interactive incident alerts with direct Slack-based acknowledge and investigation trigger buttons.

---

## Contributing

We welcome contributions to ModelSentinel! To get started:

1. **Fork the Repository:** Fork [Saksham2005-coder/ModelSentinel](https://github.com/Saksham2005-coder/ModelSentinel) to your GitHub account.
2. **Create a Feature Branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Set Up Local Environment:** Follow the [Manual Development Setup](#manual-development-setup) instructions above.
4. **Run Tests:** Ensure all tests pass before submitting changes:
   ```bash
   cd backend && pytest tests/
   cd ../cli && pytest tests/
   cd ../frontend && npm run lint && npm run build
   ```
5. **Submit a Pull Request:** Open a detailed Pull Request on GitHub describing your changes, motivation, and test coverage.

---

## License & Acknowledgments

### License
*(A formal open-source license decision is currently pending. Please do not redistribute or utilize in proprietary commercial production environments without explicit authorization from the author.)*

### Acknowledgments
ModelSentinel is built upon the incredible open-source ecosystem, including:
- [FastAPI](https://fastapi.tiangolo.com) by Sebastián Ramírez (@tiangolo)
- [SQLAlchemy](https://www.sqlalchemy.org) by Mike Bayer
- [Tailwind CSS](https://tailwindcss.com) by Tailwind Labs
- [Lucide Icons](https://lucide.dev) by the Lucide Community
- [Recharts](https://recharts.org) by the Recharts Community
- [Typer](https://typer.tiangolo.com) for Python CLI developer experience

---

<div align="center">

**ModelSentinel** — Developed by [Saksham Gupta](https://github.com/Saksham2005-coder)  
*For questions, feedback, or enterprise collaboration, open an issue on [GitHub](https://github.com/Saksham2005-coder/ModelSentinel/issues).*

</div>