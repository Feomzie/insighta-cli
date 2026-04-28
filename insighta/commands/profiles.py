import typer
from insighta.api import request

app = typer.Typer()

@app.command()
def list(country: str = None, gender: str = None):
    res = request("GET", "/api/profiles", params={
        "country": country,
        "gender": gender
    })

    data = res.json()

    for p in data["data"]:
        typer.echo(f"{p['name']} - {p['country_name']}")


@app.command()
def search(query: str):
    res = request("GET", f"/api/profiles/search?q={query}")

    for p in res.json()["data"]:
        typer.echo(p["name"])


@app.command()
def get(id: str):
    res = request("GET", f"/api/profiles/{id}")
    typer.echo(res.json())


@app.command()
def create(name: str):
    res = request("POST", "/api/profiles", json={"name": name})
    typer.echo(res.json())

#CSV thingy
@app.command()
def export():
    res = request("GET", "/api/profiles/export?format=csv")

    with open("profiles.csv", "wb") as f:
        f.write(res.content)

    typer.echo("Export saved as profiles.csv")