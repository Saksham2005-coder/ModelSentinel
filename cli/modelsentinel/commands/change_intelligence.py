import typer
from ..client import client
from ..output import print_json, print_table, print_details, console
from .. import output
from rich.panel import Panel
from rich.text import Text

app = typer.Typer()

@app.callback(invoke_without_command=True)
def main(patch_id: str = typer.Argument(None)):
    """Inspect deterministic change impact, historical evidence, blast radius and risk for a patch."""
    if not patch_id:
        return
        
    data = client.get(f"/patches/{patch_id}/change-intelligence")
    if output.is_json:
        print_json(data)
        return

    text = Text()
    
    # Score & Level
    score = data.get("risk_score", 0)
    level = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    
    text.append("Score: ", style="bold")
    text.append(f"{score} / 100\n")
    text.append("Level: ", style="bold")
    text.append(f"{level}\n\n")

    # Counts
    changed_files = len(data.get("changed_files", []))
    changed_symbols = sum(len(f.get("symbols_changed", [])) for f in data.get("changed_files", []))
    affected_symbols = len(data.get("affected_dependencies", []))
    affected_models = len(data.get("affected_models", []))
    
    text.append(f"{'Changed files:'.ljust(22)} {changed_files}\n")
    text.append(f"{'Changed symbols:'.ljust(22)} {changed_symbols}\n")
    text.append(f"{'Affected symbols:'.ljust(22)} {affected_symbols}\n")
    text.append(f"{'Affected models:'.ljust(22)} {affected_models}\n\n")

    # ML Impact
    text.append("ML Impact\n", style="bold underline")
    text.append("-" * 32 + "\n")
    ml_impacts = data.get("ml_impact", [])
    if ml_impacts:
        for imp in ml_impacts:
            text.append(f"{imp.get('component', '').ljust(22)} {imp.get('impact', '')}\n")
    else:
        text.append("None\n")
    text.append("\n")

    # Historical Evidence
    text.append("Historical Evidence\n", style="bold underline")
    text.append("-" * 32 + "\n")
    evidence = data.get("historical_evidence", [])
    if evidence:
        for ev in evidence:
            text.append(f"{ev.get('type', '').replace('_', ' ').title().ljust(22)} {ev.get('evidence', '')}\n")
    else:
        text.append("None\n")
    text.append("\n")

    # Risk Factors
    text.append("Risk Factors\n", style="bold underline")
    text.append("-" * 32 + "\n")
    risk_factors = data.get("risk_factors", [])
    if risk_factors:
        for factor in risk_factors:
            text.append(f"{factor}\n")
    else:
        text.append("Base risk only\n")

    console.print(Panel(text, title="CHANGE RISK"))

@app.command()
def risk(patch_id: str):
    """Show just the change risk score and factors"""
    data = client.get(f"/patches/{patch_id}/change-intelligence")
    if output.is_json:
        print_json({"risk_score": data.get("risk_score"), "risk_factors": data.get("risk_factors")})
        return

    print_details(f"RISK FOR {patch_id}", {
        "Score": data.get("risk_score"),
        "Factors": "\n".join(data.get("risk_factors", []))
    })

@app.command()
def blast_radius(patch_id: str):
    """Show the blast radius details"""
    data = client.get(f"/patches/{patch_id}/change-intelligence")
    if output.is_json:
        print_json({
            "blast_radius": data.get("blast_radius"),
            "affected_dependencies": data.get("affected_dependencies")
        })
        return

    print_details(f"BLAST RADIUS FOR {patch_id}", {
        "Level": data.get("blast_radius"),
        "Dependencies": ", ".join(data.get("affected_dependencies", []))
    })
