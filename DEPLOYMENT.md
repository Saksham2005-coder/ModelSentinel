# ModelSentinel Deployment Guide

This document outlines how to deploy ModelSentinel for production and demo environments.

## Architecture
- **Frontend**: React application built with Vite and served via Nginx (Docker).
- **Backend**: FastAPI Python backend running via Uvicorn (Docker).
- **Database**: 
  - **Demo Environment**: SQLite (local file volume mapped into Docker container).
  - **Production Environment**: PostgreSQL (standalone or via Docker).
- **Optional Integrations**: GitHub, PagerDuty, Email Provider.

## Environment Variables
See `.env.example` for a complete list.
Crucial variables include:
- `DATABASE_URL`: Set to SQLite for demo or PostgreSQL connection string for production.
- `SECRET_KEY`: Mandatory secure random string for JWT authentication.
- `FRONTEND_URL`: URL where the frontend is hosted (for CORS and emails).
- `LLM_PROVIDER`, `GROQ_API_KEY`: Required for intelligence features.

## Setup Steps

### 1. Database Configuration
**For Demo (SQLite)**:
Use `docker-compose.demo.yml` which is pre-configured to use SQLite.

**For Production (PostgreSQL)**:
Update `.env` with `POSTGRES_SERVER`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` and use `docker-compose.yml`.

### 2. Startup
**Production Startup**:
```bash
docker compose up -d --build
```
This will automatically run Alembic migrations (`alembic upgrade head`) and start the backend/frontend.

### 3. Bootstrap Administrator
You must create an initial administrator account. Do not hardcode passwords in scripts.
```bash
python scripts/create_admin.py
```
Or, if running entirely via Docker:
```bash
docker compose exec backend python scripts/create_admin.py
```

## CORS Configuration
Ensure `BACKEND_CORS_ORIGINS` is configured correctly in `.env`.
Example:
`BACKEND_CORS_ORIGINS=["https://yourdomain.com", "https://app.yourdomain.com"]`
Do not use `["*"]` in production.

## Health and Readiness
- **Health Check**: `GET /health` (Indicates if the API is responding).
- **Readiness Check**: `GET /ready` (Indicates if the database and required dependencies are reachable).

## Known Deployment Limitations
- The initial admin must be bootstrapped via CLI.
- SQLite is limited in concurrency; use PostgreSQL for real multi-user production environments.
- GitHub integration requires a valid token and exposed webhook endpoint.
