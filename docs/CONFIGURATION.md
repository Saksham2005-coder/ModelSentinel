# Configuration

ModelSentinel uses environment variables for configuration. A template is provided in `.env.example`.

## Environment Variables

### Database Configuration
- `POSTGRES_SERVER` (Default: `db`) - The hostname of the PostgreSQL server.
- `POSTGRES_USER` (Default: `modelsentinel`) - Database username.
- `POSTGRES_PASSWORD` - Database password. **(Secret)**
- `POSTGRES_DB` (Default: `modelsentinel`) - Database name.

> **Note**: In the local demo (`docker-compose.demo.yml`), the database defaults to a local SQLite file (`modelsentinel.db`), bypassing these PostgreSQL settings.

### Backend Configuration
- `PROJECT_NAME` (Default: `ModelSentinel API`) - The API project name.
- `API_V1_STR` (Default: `/api/v1`) - The base path for API v1.
- `BACKEND_CORS_ORIGINS` (Default: `["http://localhost:5173", "http://localhost"]`) - Allowed CORS origins for the frontend.

### Authentication
- `SECRET_KEY` - A cryptographic secret used to sign JWTs. **(Secret - Required for production)**

### Frontend
- `FRONTEND_URL` (Default: `http://localhost:5173`) - The URL where the frontend is hosted.

### LLM Provider (AI Investigations)
- `LLM_PROVIDER` (Default: `groq`) - The AI provider to use.
- `GROQ_API_KEY` - API key for Groq. **(Secret)**
- `GROQ_MODEL` (Default: `llama-3.1-8b-instant`) - The specific LLM model to use.

### GitHub Integration
- `GITHUB_TOKEN` - Token for opening/commenting on Pull Requests. **(Secret)**
- `GITHUB_WEBHOOK_SECRET` - Secret for verifying incoming webhooks from GitHub. **(Secret)**
