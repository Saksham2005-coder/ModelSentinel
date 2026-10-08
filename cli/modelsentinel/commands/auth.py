import typer
import json
import os
from pathlib import Path
from ..client import client
from ..output import print_error, print_success, print_json

app = typer.Typer()

@app.command()
def login(email: str = typer.Option(..., "--email", help="User email"), password: str = typer.Option(..., "--password", help="User password")):
    try:
        data = {"username": email, "password": password}
        response = client.session.post(f"{client.base_url.rstrip('/')}/auth/login", data=data)
        if response.status_code != 200:
            print_error(f"Login failed: {response.text}")
            raise typer.Exit(1)
        
        token_data = response.json()
        config_dir = Path.home() / ".modelsentinel"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "auth.json"
        
        with open(config_file, "w") as f:
            json.dump(token_data, f)
        
        from ..output import is_json
        if is_json:
            print_json({"status": "logged_in", "email": email})
        else:
            print_success(f"Successfully logged in as {email}")
    except Exception as e:
        print_error(f"Error during login: {str(e)}")
        raise typer.Exit(1)

@app.command()
def logout():
    try:
        client.post("/auth/logout")
    except Exception:
        pass # Ignore server errors during logout
        
    config_file = Path.home() / ".modelsentinel" / "auth.json"
    if config_file.exists():
        config_file.unlink()
        
    from ..output import is_json
    if is_json:
        print_json({"status": "logged_out"})
    else:
        print_success("Successfully logged out")

@app.command()
def whoami():
    try:
        user = client.get("/auth/me")
        from ..output import is_json
        if is_json:
            print_json(user)
        else:
            print_success(f"Authenticated as: {user.get('email')} (Role: {user.get('role')})")
    except Exception as e:
        print_error(f"Not logged in or error: {str(e)}")
        raise typer.Exit(1)
