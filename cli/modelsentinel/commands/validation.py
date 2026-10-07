import typer
from ..client import client
from ..output import print_json, print_details, print_table
from .. import output
from ..errors import APIError

app = typer.Typer()

@app.command()
def show(validation_id: str):
    """Show validation results"""
    data = client.get(f"/validation/runs/{validation_id}")
    if output.is_json:
        print_json(data)
        return

    print_details(f"VALIDATION {validation_id}", {
        "Status": data.get("status"),
        "Environment": data.get("environment"),
        "Started": data.get("started_at"),
        "Completed": data.get("completed_at"),
    })
    
    if data.get("results"):
        print_table(
            "Test Results",
            data.get("results", []),
            ["Test Name", "Status"],
            [lambda r: r.get("test_name"), lambda r: r.get("status")]
        )
    
    if data.get("status") == "failed":
        # Ensure we return a non-zero exit code if automation checks validation status
        raise typer.Exit(6)
