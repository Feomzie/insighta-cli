import requests
from insighta.storage import load_tokens

BASE_URL = "https://your-backend.com"


def get_headers():
    tokens = load_tokens()

    if not tokens:
        return {}

    return {
        "Authorization": f"Bearer {tokens['access_token']}"
    }


def request(method, endpoint, **kwargs):
    return requests.request(
        method,
        f"{BASE_URL}{endpoint}",
        headers=get_headers(),
        **kwargs
    )