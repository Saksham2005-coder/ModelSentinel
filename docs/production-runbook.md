# ModelSentinel Production Runbook

This document describes the operational procedures for managing ModelSentinel in a production environment.

## 1. Startup

The application consists of a Postgres database, a FastAPI backend, and a Vite-built React frontend.

**Backend Start:**
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Frontend Start:**
```bash
cd frontend
npm run build
# Serve the static files from /dist using Nginx or a static file server
```

## 2. Migration

Run database migrations before starting the backend application:
```bash
cd backend
alembic upgrade head
```

## 3. Health Check

Verify liveness by checking the health endpoint:
```bash
curl http://localhost:8000/health
```
This returns `{"status": "ok"}` if the process is alive.

## 4. Readiness Check

Verify the API is fully ready to accept traffic and can reach the database:
```bash
curl http://localhost:8000/ready
```
This validates the connection to the PostgreSQL database and checks the LLM provider status.

## 5. Admin Bootstrap

If it's a new environment or the admin account needs recreation, run the local bootstrap script:
```bash
python scripts/create_admin.py
```
This script securely prompts for a password and will create or update the local admin account with `email_verified=True`. It never documents or outputs the password.

## 6. Login

Users can log in via the web UI. Authentication requires a verified email address. The backend uses JWT with short expiration and a token blacklist for secure logout functionality.

## 7. PostgreSQL Backup

Perform regular logical backups:
```bash
pg_dump -U modelsentinel -h <db_host> modelsentinel > modelsentinel_backup.sql
```

Ensure you backup the following volumes/data directories explicitly, as they contain critical persistent storage:
- `/data/telemetry` (CSV files)
- `/data/repositories` (Git snapshot cache)
- `/data/artifacts`

## 8. Restore

To restore from a backup:
```bash
psql -U modelsentinel -h <db_host> -d modelsentinel < modelsentinel_backup.sql
```
Data directories must be synced back from their respective file backups. 
*Note: Full restoration testing should be verified against an isolated environment.*

## 9. Logs

The backend outputs structured logging containing `request_id`, status, and traceback errors (only logged server-side, never exposed to users).
Collect these logs via a log aggregator (e.g., Fluentd, Datadog) for centralized querying.

## 10. Common Failures

**Database Interruptions:** API requests will fail fast, returning `500` or `503`. The connection pool will automatically attempt reconnection.
**File System Limits:** Large telemetry uploads are restricted to 50MB. Verify disk capacity for `/data`.

## 11. GitHub Integration Failure

If GitHub webhooks fail, the system relies on idempotency checks using the `X-GitHub-Delivery` ID. Retry delivery in the GitHub UI, and the integration endpoint will reject processed deliveries and accept unprocessed ones.

## 12. Email Failure

If `EMAIL_PROVIDER=console` is set in production, emails will only be logged locally. Ensure proper SMTP credentials are provided for registration verification. Unverified accounts cannot log in.

## 13. Telemetry Failure

Telemetry payload failures (e.g. malformed CSV, size limit exceeded) return a safe `400` or `413` HTTP response.
If deterministic monitoring rules cause failures, the system will record the validation error on the telemetry payload itself rather than crashing.

## 14. Workflow Failure

Interrupted workflows remain in a `RUNNING` or `WAITING_APPROVAL` state. They can be safely resumed or canceled through the CLI or UI. Step states are transactionally isolated, meaning no duplicate side-effects.

## 15. SLO / Alert Failure

SLO alerts are bound by strict cooldown policies to prevent alert spamming. Breaches only open a single incident per cooldown window. Manual acknowledgment halts auto-escalation temporarily.

## 16. Emergency Shutdown

To shut down:
```bash
# Terminate the backend process gracefully
kill -SIGTERM <backend_pid>
```
The application will wait briefly for in-flight requests and cleanly dispose of active DB connections.

## 17. Recovery Procedure

1. Verify DB is available.
2. Ensure migrations are up to date (`alembic upgrade head`).
3. Restore missing storage directories.
4. Start the application backend.
5. Check `/ready`.
6. Use `python scripts/create_admin.py` if credentials are lost.
