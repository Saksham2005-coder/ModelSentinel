# Testing

ModelSentinel includes test suites for the backend, frontend, and CLI.

## Backend Tests

The backend uses `pytest` and `pytest-asyncio` for unit and integration testing.

```bash
cd backend
# Create and activate a virtual environment if not already done
pytest tests/
```

This suite validates:
- Core models and schemas
- API endpoint behaviors (Incidents, Patches, Monitoring, Deployments)
- Database migration sanity
- Simulated ML anomaly thresholds

## Frontend Tests

The frontend leverages ESLint for static analysis and TypeScript for type checking.

```bash
cd frontend
npm install

# Run static analysis
npm run lint

# Verify type safety and build
npm run build
```

## CLI Tests

The CLI uses `pytest` and `responses` to mock HTTP interactions with the backend API.

```bash
cd cli
pip install -e .[dev] # Or ensure pytest is installed
pytest tests/
```

This suite validates:
- Command parsing and argument validation
- Authentication and token storage
- Output formatting (Rich tables)
- Error handling on unexpected API responses
