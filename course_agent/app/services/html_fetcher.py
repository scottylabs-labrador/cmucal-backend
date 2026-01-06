import requests

def fetch_html(url: str) -> str:
    return requests.get(url, timeout=10).text
