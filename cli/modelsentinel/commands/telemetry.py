import typer
import os
from ..client import client
from ..output import print_json, print_table, print_details, print_success, print_error, is_json

app = typer.Typer()

@app.command()
def list(model_id: str = None, limit: int = 100):
    """List telemetry ingests"""
    params = {"limit": limit}
    if model_id:
        params["model_id"] = model_id
    data = client.get("/telemetry", params=params)
    if output.is_json:
        print_json(data)
        return

    print_table(
        "Telemetry Ingests",
        data,
        ["ID", "Model ID", "Timestamp", "Status"],
        [lambda t: t.get("id"), lambda t: t.get("model_id"), lambda t: t.get("timestamp"), lambda t: t.get("status")]
    )

@app.command()
def show(telemetry_id: str):
    """Show details for a telemetry ingest"""
    data = client.get(f"/telemetry/{telemetry_id}")
    if output.is_json:
        print_json(data)
        return

    print_details(f"TELEMETRY {telemetry_id}", {
        "ID": data.get("id"),
        "Model ID": data.get("model_id"),
        "Timestamp": data.get("timestamp"),
        "Status": data.get("status"),
        "Rows": data.get("rows_processed"),
    })

@app.command()
def ingest(model_id: str, csv_file: str):
    """Ingest telemetry from a CSV file"""
    if not os.path.exists(csv_file):
        if output.is_json:
            print_json({"error": "File not found"})
        else:
            print_error(f"File '{csv_file}' not found.")
        raise typer.Exit(1)
        
    if not output.is_json:
        typer.echo("Uploading telemetry...")

    with open(csv_file, "rb") as f:
        files = {"file": (os.path.basename(csv_file), f, "text/csv")}
        data = client.post(f"/telemetry/ingest/{model_id}", files=files)
    
    if output.is_json:
        print_json(data)
        return

    print_success("Ingestion accepted")
    if data.get("monitoring_run_id"):
        print_success("Monitoring run created")
        print_success("Health evaluated")
        if data.get("incident_id"):
            print_error(f"Incident created: {data.get('incident_id')}")
        else:
            print_success("No new incident")
