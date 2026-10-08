import typer
from ..client import client
from ..output import print_json, print_table, print_details, console
from .. import output

app = typer.Typer()

@app.command()
def list(model_id: str = None):
    """List Alerts for a model or all"""
    endpoint = "/alerts"
    if model_id:
        endpoint += f"?model_id={model_id}"
    
    data = client.get(endpoint)
    if output.is_json:
        print_json(data)
        return

    if not data:
        console.print("No Alerts found.")
        return

    print_table(
        data,
        ["id", "severity", "status", "summary", "triggered_at"],
        ["ID", "Severity", "Status", "Summary", "Triggered At"]
    )
    
@app.command()
def acknowledge(alert_id: str):
    """Acknowledge an alert"""
    data = client.post(f"/alerts/{alert_id}/acknowledge", data={})
    if output.is_json:
        print_json(data)
        return
        
    console.print(f"[green]Alert {alert_id} acknowledged successfully.[/green]")
