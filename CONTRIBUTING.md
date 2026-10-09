# Contributing to ModelSentinel

Thank you for your interest in contributing to ModelSentinel! 

## Branching & Pull Requests

1. **Branch Naming**: Use descriptive branch names prefixed with the type of change (e.g., `feat/`, `fix/`, `docs/`, `chore/`).
2. **Pull Requests**: Ensure all PRs are linked to an active issue (if applicable) and clearly state the motivation and implementation details.
3. **Draft PRs**: Feel free to open a Draft PR early to get feedback on an implementation approach.

## Code Standards

- **Backend (Python)**: Follow PEP 8 standards. Use type hints (`-> List[str]`, `-> Dict`) throughout the FastAPI application.
- **Frontend (TypeScript)**: Ensure strict typing is maintained. Avoid `any` where a proper interface can be used. Use ESLint to check for compliance before committing (`npm run lint`).
- **Tests**: Include relevant unit or integration tests for any new behavior. Run `pytest` and confirm successful execution before pushing.

## Submitting a Bug Report

When filing a bug, please include:
1. Steps to reproduce the issue.
2. The expected outcome.
3. The actual outcome.
4. Any relevant logs or stack traces (ensure secrets are redacted).
