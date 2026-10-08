import typer
from typing import Optional
from ..client import client
import modelsentinel.output as out

app = typer.Typer(help="Integration commands")

@app.command("list")
def list_integrations():
    """List all integrations."""
    data = client.get("/integrations")
    if out.is_json:
        out.print_json(data)
    else:
        out.print_table("Integrations", data, ["ID", "Provider", "Name", "Status"], [lambda i: i["id"], lambda i: i["provider"], lambda i: i["name"], lambda i: i["status"]])

@app.command("show")
def show_integration(integration_id: str = typer.Argument(...)):
    """Show details of a specific integration."""
    data = client.get(f"/integrations/{integration_id}")
    if out.is_json:
        out.print_json(data)
    else:
        out.print_details("Integration Details", data)

@app.command("github-status")
def github_status():
    """Check GitHub integration status."""
    data = client.get("/integrations/github/status")
    if out.is_json:
        out.print_json(data)
    else:
        out.print_details("Integration Details", data)
