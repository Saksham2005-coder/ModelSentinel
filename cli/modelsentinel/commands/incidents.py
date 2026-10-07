import typer
from typing import Optional
from ..client import client
from ..output import print_json, print_table, print_details
from .. import output

app = typer.Typer()

@app.command()
def list(status: Optional[str] = None, severity: Optional[str] = None, limit: int = 100):
    """List incidents"""
    params = {}
    if status:
        params["status"] = status
    if severity:
        params["severity"] = severity
    # Add skip/limit if API supports it, backend probably uses skip/limit
    params["limit"] = limit
    
    data = client.get("/incidents", params=params)
    if output.is_json:
        print_json(data)
        return

    print_table(
        "Incidents",
        data,
        ["ID", "Severity", "Status", "Model ID", "Detected"],
        [lambda i: i.get("id"), lambda i: i.get("severity"), lambda i: i.get("status"), lambda i: i.get("model_id"), lambda i: i.get("detected_at")]
    )

@app.command()
def show(incident_id: str):
    """Show details for a specific incident"""
    data = client.get(f"/incidents/{incident_id}")
    if output.is_json:
        print_json(data)
        return

    print_details(f"INCIDENT {incident_id}", {
        "ID": data.get("id"),
        "Key": data.get("incident_key"),
        "Title": data.get("title"),
        "Severity": data.get("severity"),
        "Status": data.get("status"),
        "Model ID": data.get("model_id"),
        "Detected At": data.get("detected_at"),
    })

@app.command()
def investigate(incident_id: str):
    """Show investigation status for an incident"""
    data = client.get(f"/incidents/{incident_id}/investigations")
    if output.is_json:
        print_json(data)
        return

    if not data:
        print_details(f"INVESTIGATION FOR {incident_id}", {"Status": "No investigation found"})
        return
    
    inv = data[0] if isinstance(data, list) else data
    print_details(f"INVESTIGATION {inv.get('id')}", {
        "Status": inv.get("status"),
        "Root Cause (LLM)": inv.get("root_cause_summary") or "Pending",
        "Recommended Action": inv.get("recommended_action") or "Pending",
    })

@app.command()
def timeline(incident_id: str):
    """Show timeline for an incident"""
    data = client.get(f"/incidents/{incident_id}/timeline")
    if output.is_json:
        print_json(data)
        return

    print_table(
        f"Timeline for {incident_id}",
        data,
        ["Timestamp", "Event Type", "Description"],
        [lambda t: t.get("timestamp"), lambda t: t.get("event_type"), lambda t: t.get("description")]
    )
