import typer
from ..client import client
from ..output import print_json, print_table, print_details
from .. import output

app = typer.Typer()

@app.command()
def list():
    """List all models"""
    data = client.get("/models")
    if output.is_json:
        print_json(data)
        return

    items = data
    if isinstance(data, dict):
        if "items" in data:
            items = data["items"]
        else:
            output.print_error("Unexpected response format from API: missing 'items' key")
            raise typer.Exit(1)
            
    if type(items) is not type([]):
        output.print_error("Unexpected response format from API: expected a list of models")
        raise typer.Exit(1)

    print_table(
        "Models",
        items,
        ["ID", "Name", "Task Type", "Status"],
        [lambda m: m.get("id"), lambda m: m.get("name"), lambda m: m.get("task_type"), lambda m: m.get("status")]
    )

@app.command()
def show(model_id: str):
    """Show details for a specific model"""
    data = client.get(f"/models/{model_id}")
    if output.is_json:
        print_json(data)
        return

    print_details(f"MODEL {model_id}", {
        "ID": data.get("id"),
        "Name": data.get("name"),
        "Task Type": data.get("task_type"),
        "Status": data.get("status"),
        "Environment": data.get("environment"),
    })

@app.command()
def health(model_id: str):
    """Show model health intelligence"""
    data = client.get(f"/models/{model_id}/intelligence")
    if output.is_json:
        print_json(data)
        return

    health_data = data.get("health", {})
    breakdown = health_data.get("breakdown", {})
    print_details(f"MODEL HEALTH {model_id}", {
        "Status": health_data.get("status"),
        "Score": f'{health_data.get("score")}/100',
        "Performance": breakdown.get("performance"),
        "Data Quality": breakdown.get("data_quality"),
        "Feature Drift": breakdown.get("feature_drift"),
        "Prediction Stability": breakdown.get("prediction_stability"),
        "Incident State": breakdown.get("incident_state"),
    })

@app.command()
def history(model_id: str):
    """Show model health history"""
    data = client.get(f"/models/{model_id}/intelligence")
    history_data = data.get("history", [])
    if output.is_json:
        print_json(history_data)
        return

    print_table(
        f"Health History for {model_id}",
        history_data,
        ["Timestamp", "Score", "Status"],
        [lambda h: h.get("timestamp"), lambda h: h.get("score"), lambda h: h.get("status")]
    )

@app.command()
def versions(model_id: str):
    """List versions for a model"""
    data = client.get(f"/models/{model_id}/versions")
    if output.is_json:
        print_json(data)
        return

    print_table(
        f"Versions for {model_id}",
        data,
        ["ID", "Name", "Status", "Created At"],
        [lambda v: v.get("id"), lambda v: v.get("name"), lambda v: v.get("status"), lambda v: v.get("created_at")]
    )

@app.command()
def compare(model_id: str, version_a: str, version_b: str):
    """Compare two versions of a model"""
    data = client.get(f"/models/{model_id}/compare?version_a={version_a}&version_b={version_b}")
    if output.is_json:
        print_json(data)
        return

    summary = data.get("summary", {})
    print_details(f"COMPARE {version_a} vs {version_b}", {
        "Performance Diff": summary.get("performance_diff"),
        "Drift Diff": summary.get("drift_diff"),
        "Verdict": summary.get("verdict"),
    })
