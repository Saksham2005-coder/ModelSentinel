import typer
from ..client import client
from ..output import print_json, print_table, print_details, print_error, print_success
from .. import output

app = typer.Typer()

@app.command()
def list(investigation_id: str):
    """List patches for an investigation"""
    data = client.get(f"/investigations/{investigation_id}/patches")
    if output.is_json:
        print_json(data)
        return

    print_table(
        f"Patches for Investigation {investigation_id}",
        data,
        ["ID", "Status", "Summary", "Created At"],
        [lambda p: p.get("id"), lambda p: p.get("status"), lambda p: p.get("summary"), lambda p: p.get("created_at")]
    )

@app.command()
def show(patch_id: str):
    """Show patch details"""
    data = client.get(f"/patches/{patch_id}")
    if output.is_json:
        print_json(data)
        return

    print_details(f"PATCH {patch_id}", {
        "ID": data.get("id"),
        "Status": data.get("status"),
        "Investigation": data.get("investigation_id"),
        "Summary": data.get("summary"),
        "Rationale": data.get("rationale"),
    })

@app.command()
def diff(patch_id: str):
    """Show patch diff"""
    data = client.get(f"/patches/{patch_id}")
    files = data.get("file_changes", [])
    
    if output.is_json:
        print_json(files)
        return

    for fc in files:
        import rich
        from rich.syntax import Syntax
        typer.echo(f"\n--- a/{fc.get('file_path')}")
        typer.echo(f"+++ b/{fc.get('file_path')}")
        diff_text = fc.get("diff_text", "")
        rich.print(Syntax(diff_text, "diff", theme="monokai"))

@app.command()
def validate(patch_id: str):
    """Trigger validation for a patch (DOES NOT APPROVE)"""
    # Validation triggers tests. Does not approve the patch.
    if not output.is_json:
        typer.echo(f"Triggering validation for patch {patch_id}...")
    
    # Check if there is an endpoint for manual validation trigger
    # In ModelSentinel, this might be POST /validation/runs?patch_id={patch_id}
    # For now, hit the endpoint or display a sensible message.
    try:
        data = client.post(f"/validation/runs", json={"patch_proposal_id": patch_id, "environment": "test"})
        if output.is_json:
            print_json(data)
            return
        print_success(f"Validation run started: {data.get('id')}")
    except Exception as e:
        if output.is_json:
            print_json({"error": str(e)})
        else:
            print_error(str(e))
        raise typer.Exit(1)
