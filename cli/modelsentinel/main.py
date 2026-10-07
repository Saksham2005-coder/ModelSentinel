import typer
import sys
from typing import Optional

from .config import config
from .output import set_json_output, print_error
from .errors import CLIError

app = typer.Typer(
    name="modelsentinel",
    help="ModelSentinel Engineering CLI",
    add_completion=False,
)

# Import and register subcommands
from .commands import models, incidents, telemetry, repository, change_intelligence, patches, validation, deployments, reliability

app.add_typer(models.app, name="models", help="Model inspection and health commands")
app.add_typer(incidents.app, name="incidents", help="Incident investigation commands")
app.add_typer(telemetry.app, name="telemetry", help="Telemetry ingestion and list commands")
app.add_typer(repository.app, name="repository", help="Repository intelligence commands")
app.add_typer(change_intelligence.app, name="change-intelligence", help="Change impact and risk commands")
app.add_typer(patches.app, name="patches", help="Patch and validation commands")
app.add_typer(validation.app, name="validation", help="Validation show commands")
app.add_typer(deployments.app, name="deployments", help="Deployment state commands")
app.add_typer(reliability.app, name="reliability", help="Reliability analytics and memory commands")

__version__ = "0.1.0"

def version_callback(value: bool):
    if value:
        typer.echo(f"ModelSentinel Engineering CLI v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    api_url: Optional[str] = typer.Option(
        None, "--api-url", help="Override the ModelSentinel API URL"
    ),
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True, help="Show the version and exit."
    ),
):
    if api_url:
        config.API_URL = api_url

def run():
    # Globally intercept --json and --debug
    if "--json" in sys.argv:
        set_json_output(True)
        sys.argv.remove("--json")
    if "--debug" in sys.argv:
        config.DEBUG = True
        sys.argv.remove("--debug")

    try:
        app()
    except CLIError as e:
        if config.DEBUG:
            raise
        print_error(e.message)
        sys.exit(e.exit_code)
    except Exception as e:
        if config.DEBUG:
            raise
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run()
