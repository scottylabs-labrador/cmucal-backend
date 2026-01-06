# course-agent/app/services/search.py
import requests
import os

SERPER_URL = "https://google.serper.dev/search"


def search_course_site(course_name: str, max_results: int = 5) -> list[str]:
    payload = {"q": f"{course_name} Carnegie Mellon course website", "num": max_results}

    headers = {
        "X-API-KEY": os.environ["SERPER_API_KEY"],
        "Content-Type": "application/json",
    }

    res = requests.post(SERPER_URL, json=payload, headers=headers, timeout=10)

    res.raise_for_status()
    data = res.json()

    return [item["link"] for item in data.get("organic", []) if "link" in item]
