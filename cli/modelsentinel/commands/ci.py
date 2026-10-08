import typer
from typing import Optional
from ..client import client
import modelsentinel.output as out

app = typer.Typer(help="CI commands")

@app.command("status")
def ci_status(check_id: str = typer.Argument(...)):
    """Show details of a specific CI check."""
    data = client.get(f"/ci/status/{check_id}")
    if out.is_json:
        out.print_json(data)
    else:
        out.print_details("CI Check", data)

@app.command("runs")
def ci_runs(repository_id: str = typer.Argument(...)):
    """List CI checks for a specific repository."""
    data = client.get(f"/ci/runs/{repository_id}")
    if out.is_json:
        out.print_json(data)
    else:
        out.print_table("CI Checks", data, ["ID", "Name", "Status", "Conclusion"], [lambda x: x.get("id"), lambda x: x.get("name"), lambda x: x.get("status"), lambda x: x.get("conclusion")])
