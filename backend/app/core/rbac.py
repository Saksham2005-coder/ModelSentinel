from app.models.user import Role

ROLE_PERMISSIONS = {
    Role.ADMIN: [
        "models.read", "models.manage",
        "incidents.read", "incidents.investigate",
        "repositories.read", "repositories.manage",
        "patches.read", "patches.propose", "patches.approve", "patches.reject",
        "validation.read", "validation.run",
        "workflows.read", "workflows.start", "workflows.approve", "workflows.reject",
        "deployments.read", "deployments.approve", "deployments.execute",
        "integrations.read", "integrations.manage",
        "analytics.read",
        "audit.read",
        "users.read", "users.manage"
    ],
    Role.ML_ENGINEER: [
        "models.read",
        "incidents.read", "incidents.investigate",
        "repositories.read",
        "patches.read", "patches.propose",
        "validation.read", "validation.run",
        "workflows.read", "workflows.start",
        "deployments.read",
        "integrations.read",
        "analytics.read"
    ],
    Role.REVIEWER: [
        "models.read",
        "incidents.read",
        "repositories.read",
        "patches.read", "patches.approve", "patches.reject",
        "validation.read",
        "workflows.read", "workflows.approve", "workflows.reject",
        "deployments.read", "deployments.approve",
        "analytics.read"
    ],
    Role.VIEWER: [
        "models.read",
        "incidents.read",
        "repositories.read",
        "patches.read",
        "validation.read",
        "workflows.read",
        "deployments.read",
        "integrations.read",
        "analytics.read"
    ],
    Role.INTEGRATION: [
        "models.read",
        "incidents.read", "incidents.investigate",
        "repositories.read",
        "patches.read", "patches.propose",
        "validation.read", "validation.run",
        "workflows.read", "workflows.start",
        "deployments.read", "deployments.execute",
        "analytics.read"
    ]
}

def has_permission(role: Role, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, [])
