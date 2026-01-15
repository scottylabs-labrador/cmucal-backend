# course_agent/app/services/search.py
import requests
import os

SERPER_URL = "https://google.serper.dev/search"

_search_fn = None

# Returns a cached search function that queries Google (via Serper API) for a CMU course website and 
# returns a list of URLs.

def get_search_course_site():
    global _search_fn
    if _search_fn is None:
        def _search(course_name: str, max_results: int = 5) -> list[str]:
            # Create Google-style query 
            payload = {
                "q": f"{course_name} Carnegie Mellon course website",
                "num": max_results,
            }

            headers = {
                "X-API-KEY": os.environ["SERPER_API_KEY"],
                "Content-Type": "application/json",
            }

            # Send HTTP request
            res = requests.post(
                SERPER_URL,
                json=payload,
                headers=headers,
                timeout=10,
            )
            res.raise_for_status()
            data = res.json()

            # Return array of links
            return [item["link"] for item in data.get("organic", []) if "link" in item]

        _search_fn = _search

    return _search_fn
