import json
import sys
from rich.console import Console

# Global output state
is_json = False
console = Console()
err_console = Console(stderr=True)

def set_json_output(json_flag: bool):
    global is_json
    is_json = json_flag

def print_json(data: dict):
    # Standard library json.dumps, no rich formatting to avoid breaking machine readability
    print(json.dumps(data, indent=2))

def print_table(title, items, columns, value_extractors):
    from rich.table import Table
    table = Table(title=title)
    for col in columns:
        table.add_column(col)
    for item in items:
        row = [str(extractor(item)) for extractor in value_extractors]
        table.add_row(*row)
    console.print(table)

def print_details(title, data: dict):
    from rich.panel import Panel
    from rich.text import Text
    text = Text()
    for k, v in data.items():
        text.append(f"{k.ljust(20)}: ", style="bold")
        text.append(f"{v}\n")
    console.print(Panel(text, title=title))

def print_error(message: str, debug_info: str = None):
    err_console.print(f"[red]Error:[/red] {message}")
    if debug_info and config.DEBUG:
        err_console.print(f"\n[dim]{debug_info}[/dim]")

def print_success(message: str):
    if not is_json:
        console.print(f"[green]*[/green] {message}")

from .config import config
