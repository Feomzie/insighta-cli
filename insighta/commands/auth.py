import typer
from insighta.storage import save_tokens, clear_tokens, load_tokens

app = typer.Typer()

@app.command()
def login():
    typer.echo("Logging in via GitHub...")

    # Simulated backend response
    tokens = {
        "access_token": "access123",
        "refresh_token": "refresh123",
        "user": {"username": "john_doe"}
    }

    save_tokens(tokens)

    typer.echo("Logged in as @john_doe")


@app.command()
def logout():
    clear_tokens()
    typer.echo("Logged out")


@app.command()
def whoami():
    data = load_tokens()

    if not data:
        typer.echo("Not logged in")
        return

    typer.echo(f"Logged in as @{data['user']['username']}")