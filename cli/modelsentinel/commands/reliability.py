import typer
from ..client import client
from ..output import print_json, print_table, print_details, console
from .. import output
from rich.panel import Panel

app = typer.Typer()

@app.command()
def timeline(model_id: str):
    """Show reliability timeline for a model"""
    data = client.get(f"/reliability/timeline/{model_id}")
    if output.is_json:
        print_json(data)
        return

    events = data.get("events", [])
    if not events:
        console.print("No events found in timeline.")
        return
        
    console.print(f"[bold]MODEL RELIABILITY TIMELINE ({model_id})[/bold]")
    console.print("================================")
    for ev in events:
        # timestamp format is likely ISO, keep it simple or format it
        timestamp = ev.get("timestamp", "").split("T")[1][:5] if "T" in ev.get("timestamp", "") else ev.get("timestamp")
        desc = ev.get("title") or ev.get("event_type")
        console.print(f"{timestamp.ljust(6)} {desc}")

@app.command()
def analytics(model_id: str):
    """Show reliability analytics"""
    data = client.get(f"/reliability/analytics/{model_id}")
    if output.is_json:
        print_json(data)
        return

    print_details(f"RELIABILITY ANALYTICS {model_id}", {
        "MTTF (Mean Time To Failure)": data.get("mttf_hours"),
        "MTTR (Mean Time To Resolution)": data.get("mttr_hours"),
        "Incident Count": data.get("incident_count"),
        "Availability": f"{data.get('availability_percentage', 0):.2f}%",
    })

@app.command()
def memory(incident_id: str):
    """Show incident resolution memory"""
    data = client.get(f"/memory/resolution/{incident_id}")
    if output.is_json:
        print_json(data)
        return

    print_details(f"RESOLUTION MEMORY FOR {incident_id}", {
        "ID": data.get("id"),
        "Summary": data.get("summary"),
        "Context": data.get("context"),
        "Resolution": data.get("resolution_details"),
    })
