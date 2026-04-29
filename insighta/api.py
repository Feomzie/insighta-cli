import requests
import sys
from rich.console import Console
from insighta.storage import load_tokens, save_tokens, clear_tokens

from insighta.config import BASE_URL

console = Console()

def get_headers(endpoint: str):
    tokens = load_tokens()
    headers = {}
    
    # Apply versioning only to profile APIs
    if "/api/profiles" in endpoint:
        headers["X-API-Version"] = "1"

    if tokens and "access_token" in tokens:
        headers["Authorization"] = f"Bearer {tokens['access_token']}"
        
    return headers

def refresh_access_token() -> bool:
    tokens = load_tokens()
    if not tokens or "refresh_token" not in tokens:
        return False
    
    try:
        res = requests.post(
            f"{BASE_URL}/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]}
        )
        if res.status_code == 200:
            new_data = res.json()
            tokens["access_token"] = new_data["access_token"]
            tokens["refresh_token"] = new_data["refresh_token"]
            save_tokens(tokens)
            return True
    except requests.RequestException:
        pass
    
    return False

def request(method: str, endpoint: str, **kwargs):
    url = f"{BASE_URL}{endpoint}"
    
    try:
        res = requests.request(method, url, headers=get_headers(endpoint), **kwargs)
        
        # Handle Token Expiry & Auto-Refresh
        if res.status_code == 401:
            if refresh_access_token():
                # Retry the original request
                res = requests.request(method, url, headers=get_headers(endpoint), **kwargs)
            else:
                clear_tokens()
                console.print("[bold red]Session expired or invalid. Please run `insighta login` again.[/bold red]")
                sys.exit(1)

        # Handle Rate Limiting
        if res.status_code == 429:
            console.print("[bold red]Rate limit exceeded (429 Too Many Requests). Please try again later.[/bold red]")
            sys.exit(1)

        # Handle General API Errors
        if res.status_code >= 400:
            try:
                err_msg = res.json().get("message", res.text)
            except ValueError:
                err_msg = res.text
            console.print(f"[bold red]API Error ({res.status_code}): {err_msg}[/bold red]")
            sys.exit(1)
            
        return res

    except requests.RequestException as e:
        console.print(f"[bold red]Network error: Failed to connect to server ({e})[/bold red]")
        sys.exit(1)