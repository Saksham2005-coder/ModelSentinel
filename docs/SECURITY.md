# Security & Operations

## Authentication & Authorization

ModelSentinel currently uses an RBAC system integrated with standard OAuth2 / JWT authentication. 
- Ensure that the `SECRET_KEY` in your `.env` is sufficiently long (at least 32 bytes) and securely generated.
- By default, the `admin@modelsentinel.local` user is created with a static password via the bootstrap script. **This must be changed immediately upon deployment.**

## Secret Management

- **Do not commit `.env` files.**
- Ensure Docker images do not inadvertently copy `.env` files. The `.dockerignore` covers this, but manual verification is recommended.
- Database passwords and AI provider keys (e.g. `GROQ_API_KEY`) should be injected via securely managed secrets managers (e.g. AWS Secrets Manager, Hashicorp Vault) in production environments.

## Local vs. Production Execution

- The local demo environment (`docker-compose.demo.yml`) utilizes **SQLite**, avoiding complex configuration. It is strictly meant for evaluation.
- Production environments must run **PostgreSQL**.
- Local demonstration endpoints operate over plain HTTP. Production implementations MUST configure TLS (HTTPS) via a reverse proxy (Nginx, Traefik, AWS ALB) to secure traffic and JWT transmission.
