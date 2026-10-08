import typer
from typing import Optional
from ..client import client
import modelsentinel.output as out

app = typer.Typer(help="Pull Request commands")

@app.command("list")
def list_prs():
    """List all pull requests."""
    data = client.get("/pull-requests")
    if out.is_json:
        out.print_json(data)
    else:
        out.print_table("Pull Requests", data, ["ID", "Title", "Status", "Branch Name"], [lambda x: x.get("id"), lambda x: x.get("title", ""), lambda x: x.get("status"), lambda x: x.get("branch_name")])

@app.command("show")
def show_pr(pr_id: str = typer.Argument(...)):
    """Show details of a specific pull request."""
    data = client.get(f"/pull-requests/{pr_id}")
    if out.is_json:
        out.print_json(data)
    else:
        out.print_details("Pull Request", data)

@app.command("checks")
def list_checks(pr_id: str = typer.Argument(...)):
    """List CI checks for a specific pull request."""
    data = client.get(f"/pull-requests/{pr_id}/checks")
    if out.is_json:
        out.print_json(data)
    else:
        out.print_table("CI Checks", data, ["ID", "Name", "Status", "Conclusion"], [lambda x: x.get("id"), lambda x: x.get("name"), lambda x: x.get("status"), lambda x: x.get("conclusion")])
