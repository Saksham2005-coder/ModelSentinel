import typer
from ..client import client
from ..output import print_json, print_table, print_details, console
from .. import output

app = typer.Typer()

@app.command()
def list(model_id: str = None):
    """List SLO objectives for a model or all"""
    endpoint = "/slo/objectives"
    if model_id:
        endpoint += f"?model_id={model_id}"
    
    data = client.get(endpoint)
    if output.is_json:
        print_json(data)
        return

    if not data:
        console.print("No SLO objectives found.")
        return

    print_table(
        data,
        ["id", "name", "objective_type", "target_value", "evaluation_window", "enabled"],
        ["ID", "Name", "Type", "Target", "Window", "Enabled"]
    )
    
@app.command()
def evaluate(objective_id: str):
    """Evaluate an SLO objective"""
    data = client.post(f"/slo/objectives/{objective_id}/evaluate", data={})
    if output.is_json:
        print_json(data)
        return
        
    print_details(f"SLO EVALUATION ({objective_id})", {
        "ID": data.get("id"),
        "Status": data.get("status"),
        "Measured Value": data.get("measured_value"),
        "Target Value": data.get("target_value"),
        "Compliance Ratio": data.get("compliance_ratio"),
        "Burn Rate": data.get("burn_rate"),
        "Error Budget Remaining": data.get("error_budget_remaining")
    })
