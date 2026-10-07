import typer
from ..client import client
from ..output import print_json, print_table, print_details
from .. import output

app = typer.Typer()

@app.command()
def list():
    """List deployments"""
    data = client.get("/deployments")
    if output.is_json:
        print_json(data)
        return

    print_table(
        "Deployments",
        data,
        ["ID", "Status", "Model Version", "Environment", "Created At"],
        [lambda d: d.get("id"), lambda d: d.get("status"), lambda d: d.get("model_version_id"), lambda d: d.get("environment"), lambda d: d.get("created_at")]
    )

@app.command()
def show(deployment_id: str):
    """Show deployment details"""
    data = client.get(f"/deployments/{deployment_id}")
    if output.is_json:
        print_json(data)
        return

    print_details(f"DEPLOYMENT {deployment_id}", {
        "ID": data.get("id"),
        "Status": data.get("status"),
        "Model Version": data.get("model_version_id"),
        "Environment": data.get("environment"),
        "Health State": data.get("post_deployment_health", "Unknown"),
    })

@app.command()
def verify(deployment_id: str):
    """Check post-deployment verification state"""
    data = client.get(f"/deployments/{deployment_id}/verification")
    if output.is_json:
        print_json(data)
        return

    print_details(f"VERIFICATION FOR {deployment_id}", {
        "Status": data.get("status"),
        "Started": data.get("started_at"),
        "Completed": data.get("completed_at"),
        "Is Degraded": "Yes" if data.get("is_degraded") else "No",
        "Incident ID": data.get("incident_id") or "None"
    })
