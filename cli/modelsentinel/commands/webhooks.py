import typer
from typing import Optional
from ..client import client
import modelsentinel.output as out

app = typer.Typer(help="Webhook commands")

@app.command("list")
def list_webhooks():
    """List recent webhook events."""
    data = client.get("/integrations/webhooks")
    if out.is_json:
        out.print_json(data)
    else:
        out.print_table("Webhook Events", data, ["ID", "Provider", "Event Type", "Processing Status", "Delivery ID"], [lambda x: x.get("id"), lambda x: x.get("provider"), lambda x: x.get("event_type"), lambda x: x.get("processing_status"), lambda x: x.get("delivery_id")])
