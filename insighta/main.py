import typer
from insighta.commands import auth, profiles

app = typer.Typer()

app.add_typer(auth.app, name="auth")
app.add_typer(profiles.app, name="profiles")

if __name__ == "__main__":
    app()