import typer
from typing import Optional
from ..client import client
from ..output import print_json, print_table, print_details, is_json
from .. import output
from ..errors import APIError

app = typer.Typer()

@app.command("list")
def list_workflows():
    """List all workflows"""
    data = client.get("/workflows/")
    if output.is_json:
        print_json(data)
        return
        
    print_table(
        "Workflows",
        data,
        ["ID", "Name", "Type", "Status", "Started"],
        [
            lambda w: w["id"],
            lambda w: w["name"],
            lambda w: w["workflow_type"],
            lambda w: w["status"],
            lambda w: w.get("started_at") or "Not started"
        ]
    )

@app.command("show")
def show_workflow(workflow_id: str):
    """Show details of a workflow"""
    data = client.get(f"/workflows/{workflow_id}")
    if output.is_json:
        print_json(data)
        return
        
    print_details(f"WORKFLOW {data['id']}", {
        "Name": data["name"],
        "Type": data["workflow_type"],
        "Status": data["status"],
        "Target Entity": f"{data.get('entity_type')} {data.get('entity_id')}",
        "Started": data.get("started_at"),
        "Completed": data.get("completed_at"),
    })
    
    if data.get("steps"):
        print_table(
            "Workflow Steps",
            data["steps"],
            ["Order", "Name", "Status", "Started", "Error"],
            [
                lambda s: str(s["order"]),
                lambda s: s["name"],
                lambda s: s["status"],
                lambda s: s.get("started_at") or "-",
                lambda s: s.get("error_message") or "-"
            ]
        )

@app.command("start")
def start_workflow(workflow_type: str, entity_id: str, name: str = typer.Option("CLI Triggered", "--name")):
    """Start a new workflow"""
    # Infer entity type from workflow_type for now
    entity_type = "incident" if workflow_type == "INCIDENT_RECOVERY" else "unknown"
    created = client.post(f"/workflows/?name={name}&workflow_type={workflow_type}&entity_type={entity_type}&entity_id={entity_id}")
    
    started = client.post(f"/workflows/{created['id']}/start")
    
    if output.is_json:
        print_json(started)
        return
        
    typer.echo(f"Workflow created\nID: {started['id']}\nStatus: {started['status']}")
    
    if started["status"] == "WAITING_APPROVAL":
        waiting_step = next((s for s in started["steps"] if s["status"] == "WAITING"), None)
        if waiting_step:
            typer.echo(f"Current step: {waiting_step['step_type']}")

@app.command("resume")
def resume_workflow(workflow_id: str):
    """Resume a workflow"""
    data = client.post(f"/workflows/{workflow_id}/resume")
    if output.is_json:
        print_json(data)
        return
    typer.echo(f"Workflow {workflow_id} resumed. Status is now {data['status']}.")

@app.command("cancel")
def cancel_workflow(workflow_id: str):
    """Cancel a workflow"""
    data = client.post(f"/workflows/{workflow_id}/cancel")
    if output.is_json:
        print_json(data)
        return
    typer.echo(f"Workflow {workflow_id} cancelled.")

@app.command("approve")
def approve_workflow(workflow_id: str, comments: str = typer.Option("Approved via CLI", "--comments", "-c")):
    """Approve a paused workflow"""
    data = client.post(f"/workflows/{workflow_id}/approve", json={"comments": comments})
    if output.is_json:
        print_json(data)
        return
    typer.echo(f"Workflow {workflow_id} approved. Status is now {data['status']}.")

@app.command("reject")
def reject_workflow(workflow_id: str, comments: str = typer.Option("Rejected via CLI", "--comments", "-c")):
    """Reject a paused workflow"""
    data = client.post(f"/workflows/{workflow_id}/reject", json={"comments": comments})
    if output.is_json:
        print_json(data)
        return
    typer.echo(f"Workflow {workflow_id} rejected. Status is now {data['status']}.")

@app.command("steps")
def workflow_steps(workflow_id: str):
    """List workflow steps"""
    data = client.get(f"/workflows/{workflow_id}")
    if output.is_json:
        print_json(data.get("steps", []))
        return
        
    print_table(
        "Workflow Steps",
        data.get("steps", []),
        ["Order", "Name", "Status", "Automatic", "Approval Required"],
        [
            lambda s: str(s["order"]),
            lambda s: s["name"],
            lambda s: s["status"],
            lambda s: str(s.get("is_automatic")),
            lambda s: str(s.get("requires_approval"))
        ]
    )

@app.command("events")
def workflow_events(workflow_id: str):
    """List workflow reliability events (mocked)"""
    typer.echo("Fetching workflow events...")
