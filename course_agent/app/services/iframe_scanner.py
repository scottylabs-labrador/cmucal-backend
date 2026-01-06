from bs4 import BeautifulSoup

def find_google_calendar_iframe(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")

    for iframe in soup.find_all("iframe"):
        src = iframe.get("src", "")
        if "calendar.google.com" in src:
            return src

    return None
