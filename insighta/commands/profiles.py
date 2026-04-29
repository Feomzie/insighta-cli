import typer
import os
import re
from rich.console import Console
from rich.table import Table
from insighta.api import request

app = typer.Typer()
console = Console()

def print_table(data_list):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=36)
    table.add_column("Name")
    table.add_column("Gender")
    table.add_column("Age", justify="right")
    table.add_column("Age Group")
    table.add_column("Country")
    
    for p in data_list:
        table.add_row(
            str(p.get("id", "")),
            str(p.get("name", "")),
            str(p.get("gender", "")),
            str(p.get("age", "")),
            str(p.get("age_group", "")),
            str(p.get("country_name", ""))
        )
    console.print(table)


@app.command("list")
def list_profiles(
    gender: str = typer.Option(None, "--gender", help="Filter by gender (male/female)"),
    country_id: str = typer.Option(None, "--country", help="Filter by country ID (e.g. US, NG)"),
    age_group: str = typer.Option(None, "--age-group", help="Filter by age group"),
    min_age: int = typer.Option(None, "--min-age", help="Minimum age limit"),
    max_age: int = typer.Option(None, "--max-age", help="Maximum age limit"),
    sort_by: str = typer.Option(None, "--sort-by", help="Field to sort by (age, created_at)"),
    order: str = typer.Option(None, "--order", help="Sort order (asc/desc)"),
    page: int = typer.Option(1, "--page", help="Page number"),
    limit: int = typer.Option(10, "--limit", help="Items per page"),
):
    params = {k: v for k, v in locals().items() if v is not None}

    with console.status("[cyan]Fetching profiles...[/cyan]"):
        res = request("GET", "/api/profiles", params=params)
        data = res.json()

    print_table(data.get("data", []))

    # Output Pagination info
    cur_page = data.get("page", page)
    total_pages = data.get("total_pages", 1)
    total_records = data.get("total", 0)
    console.print(f"[dim]Page {cur_page} of {total_pages} | Total records: {total_records}[/dim]")


@app.command("search")
def search(query: str):
    with console.status(f"[cyan]Executing natural language search for '{query}'...[/cyan]"):
        res = request("GET", "/api/profiles/search", params={"q": query})
        data = res.json()

    print_table(data.get("data", []))
    
    total_records = data.get("total", 0)
    console.print(f"[dim]Found {total_records} matches[/dim]")


@app.command("get")
def get_profile(id: str):
    with console.status("[cyan]Fetching profile details...[/cyan]"):
        res = request("GET", f"/api/profiles/{id}")
        data = res.json().get("data", {})
    
    table = Table(show_header=False, title="Profile Details")
    table.add_column("Field", style="bold magenta", justify="right")
    table.add_column("Value", style="cyan")
    
    for key, value in data.items():
        table.add_row(key.replace("_", " ").title(), str(value))
    
    console.print(table)


@app.command("create")
def create(name: str = typer.Option(..., "--name", help="Name of the person to generate a profile for")):
    with console.status(f"[cyan]Building profile for '{name}' via external APIs...[/cyan]"):
        res = request("POST", "/api/profiles", json={"name": name})
        data = res.json().get("data", {})

    console.print("[bold green]✔ Profile created and saved successfully![/bold green]")
    
    # Showcase standard print table function logic
    print_table([data])


@app.command("export")
def export(
    format: str = typer.Option("csv", "--format", help="Export format"),
    gender: str = typer.Option(None, "--gender"),
    country: str = typer.Option(None, "--country"),
    age_group: str = typer.Option(None, "--age-group"),
    min_age: int = typer.Option(None, "--min-age"),
    max_age: int = typer.Option(None, "--max-age"),
    sort_by: str = typer.Option(None, "--sort-by"),
    order: str = typer.Option(None, "--order"),
):
    params = {k: v for k, v in locals().items() if v is not None}

    with console.status("[cyan]Generating export file...[/cyan]"):
        res = request("GET", "/api/profiles/export", params=params)
    
    # Read backend dynamically generated filename
    content_disp = res.headers.get("Content-Disposition", "")
    match = re.search(r'filename="?([^"]+)"?', content_disp)
    filename = match.group(1) if match else "profiles_export.csv"
    
    filepath = os.path.join(os.getcwd(), filename)
    with open(filepath, "wb") as f:
        f.write(res.content)

    console.print(f"[bold green]✔ Export saved to {filepath}[/bold green]")