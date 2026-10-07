import typer
from ..client import client
from ..output import print_json, print_table, print_details
from .. import output

app = typer.Typer()

@app.command()
def list():
    """List repositories"""
    data = client.get("/repositories")
    if output.is_json:
        print_json(data)
        return

    print_table(
        "Repositories",
        data,
        ["ID", "Name", "Url"],
        [lambda r: r.get("id"), lambda r: r.get("name"), lambda r: r.get("url")]
    )

@app.command()
def show(repository_id: str):
    """Show details for a repository"""
    data = client.get(f"/repositories/{repository_id}")
    if output.is_json:
        print_json(data)
        return

    print_details(f"REPOSITORY {repository_id}", {
        "ID": data.get("id"),
        "Name": data.get("name"),
        "URL": data.get("url"),
    })

@app.command()
def files(repository_id: str, snapshot_id: str = None):
    """List files in a repository snapshot"""
    params = {}
    if snapshot_id:
        params["snapshot_id"] = snapshot_id
    data = client.get(f"/repositories/{repository_id}/files", params=params)
    
    if output.is_json:
        print_json(data)
        return

    print_table(
        f"Files in Repository {repository_id}",
        data,
        ["ID", "Path", "Language"],
        [lambda f: f.get("id"), lambda f: f.get("path"), lambda f: f.get("language")]
    )

@app.command()
def dependencies(repository_id: str, symbol: str):
    """List dependencies for a given symbol"""
    # Requires backend endpoint /repositories/{id}/dependencies?symbol={symbol}
    # For Phase 19, dependencies might be returned as part of a file or change intel.
    # Let's hit a hypothetical or existing endpoint. If it doesn't exist, it will 404 gracefully.
    data = client.get(f"/repositories/{repository_id}/dependencies", params={"symbol": symbol})
    if output.is_json:
        print_json(data)
        return

    print_table(
        f"Dependencies for '{symbol}'",
        data,
        ["Source Symbol", "Target Symbol", "File"],
        [lambda d: d.get("source_symbol_name"), lambda d: d.get("target_symbol_name"), lambda d: d.get("file_path")]
    )
