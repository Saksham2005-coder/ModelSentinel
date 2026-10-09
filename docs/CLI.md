# ModelSentinel CLI

The ModelSentinel CLI (`modelsentinel`) is a Python-based command-line tool designed for developers and CI/CD pipelines to interact with the ModelSentinel platform without using the web UI.

## Installation

To install the CLI in development mode:

```bash
cd cli
pip install -e .
```

## Authentication

Before running commands, you must authenticate against the backend API. The CLI stores the authentication token locally.

```bash
modelsentinel --api-url http://localhost:8000 auth login
```
You will be prompted for your username (e.g., `admin@modelsentinel.local`) and password.

## Command Reference

The `--api-url` flag is required for all commands unless the backend is running at the default `http://localhost:8000`.

### Models

List all active models registered in the platform:
```bash
modelsentinel --api-url http://localhost:8000 models list
```

### Incidents

List all active incidents:
```bash
modelsentinel --api-url http://localhost:8000 incidents list
```

View detailed information about a specific incident, including its investigation status:
```bash
modelsentinel --api-url http://localhost:8000 incidents view <INCIDENT_ID>
```

### Deployments

List recent deployments and their statuses:
```bash
modelsentinel --api-url http://localhost:8000 deployments list
```

## Error Handling

The CLI returns standard exit codes (0 for success, non-zero for failures) making it suitable for automation. API errors (e.g., 401 Unauthorized or 404 Not Found) are gracefully caught and displayed in the terminal.
