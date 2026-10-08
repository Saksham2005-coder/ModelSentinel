import typer
from typing import Optional
from ..client import client
from ..output import print_json, print_table, print_details, console
from .. import output

app = typer.Typer()

@app.command("overview")
def overview(
    days: Optional[int] = typer.Option(30, "--days", "-d", help="Time range in days"),
    model_id: Optional[str] = typer.Option(None, "--model-id", "-m", help="Filter by model ID")
):
    """View advanced engineering reliability overview."""
    endpoint = f"/analytics/engineering-overview?time_range_days={days}"
    if model_id:
        endpoint += f"&model_id={model_id}"
        
    data = client.get(endpoint)
    if output.is_json:
        print_json(data)
        return
        
    console.print(f"[bold]Engineering Overview[/bold]")
    console.print(f"Reliability Score: {data.get('reliability_score')}")
    console.print(f"Total Incidents: {data.get('total_incidents')}")
    console.print(f"Models at Risk: {data.get('models_at_risk')}")
    console.print(f"Active SLO Pressure: {data.get('active_slo_pressure')}")

@app.command("trends")
def trends(
    days: Optional[int] = typer.Option(30, "--days", "-d", help="Time range in days"),
    model_id: Optional[str] = typer.Option(None, "--model-id", "-m", help="Filter by model ID")
):
    """View reliability trends over time."""
    endpoint = f"/analytics/reliability-trends?time_range_days={days}"
    if model_id:
        endpoint += f"&model_id={model_id}"
        
    data = client.get(endpoint)
    if output.is_json:
        print_json(data)
        return
        
    console.print(f"[bold]Reliability Trends (Direction: {data.get('direction')})[/bold]")
    trends = data.get("trends", [])
    if trends:
        print_table(
            trends,
            ["timestamp", "incidents", "reliability_score"],
            ["Timestamp", "Incidents", "Score"]
        )
    else:
        console.print("Insufficient data.")

@app.command("models")
def models_comparison(
    days: Optional[int] = typer.Option(30, "--days", "-d", help="Time range in days")
):
    """Compare reliability across models."""
    endpoint = f"/analytics/models/comparison?time_range_days={days}"
    
    data = client.get(endpoint)
    if output.is_json:
        print_json(data)
        return
        
    console.print("[bold]Cross-Model Reliability Comparison[/bold]")
    if data:
        print_table(
            data,
            ["model_name", "reliability_score", "status", "incidents", "slo_breaches"],
            ["Model", "Score", "Status", "Incidents", "SLO Breaches"]
        )
    else:
        console.print("No models found.")

@app.command("effectiveness")
def effectiveness(
    days: Optional[int] = typer.Option(30, "--days", "-d", help="Time range in days"),
    model_id: Optional[str] = typer.Option(None, "--model-id", "-m", help="Filter by model ID")
):
    """View engineering fix effectiveness."""
    endpoint = f"/analytics/engineering-effectiveness?time_range_days={days}"
    if model_id:
        endpoint += f"&model_id={model_id}"
        
    data = client.get(endpoint)
    if output.is_json:
        print_json(data)
        return
        
    console.print("[bold]Engineering Effectiveness[/bold]")
    console.print(f"Validation Success Rate: {data.get('patch_validation_success_rate')}%")
    console.print(f"Deployment Health Rate: {data.get('deployment_health_success_rate')}%")

@app.command("hotspots")
def hotspots(
    days: Optional[int] = typer.Option(30, "--days", "-d", help="Time range in days")
):
    """View engineering hotspots and risk areas."""
    endpoint = f"/analytics/hotspots?time_range_days={days}"
    
    data = client.get(endpoint)
    if output.is_json:
        print_json(data)
        return
        
    console.print("[bold]Engineering Hotspots[/bold]")
    if data:
        print_table(
            data,
            ["component", "hotspot_score", "category", "incident_pressure"],
            ["Component", "Score", "Category", "Incident Pressure"]
        )
    else:
        console.print("No hotspots found.")

@app.command("drivers")
def drivers(
    days: Optional[int] = typer.Option(30, "--days", "-d", help="Time range in days"),
    model_id: Optional[str] = typer.Option(None, "--model-id", "-m", help="Filter by model ID")
):
    """View factors driving poor reliability."""
    endpoint = f"/analytics/reliability-drivers?time_range_days={days}"
    if model_id:
        endpoint += f"&model_id={model_id}"
        
    data = client.get(endpoint)
    if output.is_json:
        print_json(data)
        return
        
    console.print("[bold]Reliability Drivers[/bold]")
    if data:
        print_table(
            data,
            ["driver", "evidence_count", "affected_models", "confidence"],
            ["Driver", "Evidence Count", "Affected Models", "Confidence"]
        )
    else:
        console.print("No drivers found.")

@app.command("root-causes")
def root_causes(
    days: Optional[int] = typer.Option(30, "--days", "-d", help="Time range in days"),
    model_id: Optional[str] = typer.Option(None, "--model-id", "-m", help="Filter by model ID")
):
    """View root cause intelligence and recurrence."""
    endpoint = f"/analytics/root-causes/intelligence?time_range_days={days}"
    if model_id:
        endpoint += f"&model_id={model_id}"
        
    data = client.get(endpoint)
    if output.is_json:
        print_json(data)
        return
        
    console.print("[bold]Root Cause Intelligence[/bold]")
    if data:
        print_table(
            data,
            ["root_cause", "frequency", "successful_fix_rate", "severity"],
            ["Root Cause", "Frequency", "Successful Fix Rate", "Severity"]
        )
    else:
        console.print("No root causes found.")

@app.command("slo")
def slo_intelligence(
    days: Optional[int] = typer.Option(30, "--days", "-d", help="Time range in days"),
    model_id: Optional[str] = typer.Option(None, "--model-id", "-m", help="Filter by model ID")
):
    """View advanced SLO intelligence."""
    endpoint = f"/analytics/slo-intelligence?time_range_days={days}"
    if model_id:
        endpoint += f"&model_id={model_id}"
        
    data = client.get(endpoint)
    if output.is_json:
        print_json(data)
        return
        
    console.print("[bold]SLO Intelligence[/bold]")
    console.print(f"Total Objectives: {data.get('total_objectives')}")
    console.print(f"SLO Compliance Rate: {data.get('slo_compliance_rate')}%")
    console.print(f"Average Remaining Budget: {data.get('average_remaining_budget')}%")
    console.print(f"Active Alerts: {data.get('active_alerts')}")
