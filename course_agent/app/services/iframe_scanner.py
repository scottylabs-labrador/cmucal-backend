# course_agent/app/services/iframe_scanner.py
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urljoin
from course_agent.app.services.html_fetcher import fetch_html


def derive_ical_link(iframe_url: str) -> str | None:
    parsed = urlparse(iframe_url)
    params = parse_qs(parsed.query)

    src = params.get("src")
    if not src:
        return None

    calendar_id = src[0]

    return (
        "https://calendar.google.com/calendar/ical/"
        f"{calendar_id}/public/basic.ics"
    )


def normalize_href(href: str, base_url: str) -> str | None:
    if not href:
        return None

    href = href.strip()

    # ignore junk
    if href.startswith(("#", "javascript:", "mailto:")):
        return None

    return urljoin(base_url, href)

def is_valid_page(url: str) -> bool:
    path = urlparse(url).path.lower()
    if any(path.endswith(ext) for ext in [".pdf", ".zip", ".jpg", ".png"]):
        return False

    return path.endswith("/") or path.endswith(".html") or path.endswith(".htm")

def extract_html_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(" ", strip=True)

        url = normalize_href(href, base_url)
        # if url == "https://csapp.cs.cmu.edu/":
        #     continue 

        if not url:
            continue

        if not is_valid_page(url):
            continue

        links.append(url)

    return list(dict.fromkeys(links))  # dedupe

def find_google_calendar_iframe_url(html: str, base_url: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")

    # Find iframe on original page first
    for iframe in soup.find_all("iframe"):
        src = iframe.get("src", "")
        if "calendar.google.com" in src:
            return src

    # If cannot find iframe in original page, navigate to sidebar/navigation 
    nav_links = extract_html_links(html, base_url)

    # Find iframe in each nav link 
    for nav in nav_links:
        htmlNav = fetch_html(nav)
        soupNav = BeautifulSoup(htmlNav, "html.parser")

        for iframe in soupNav.find_all("iframe"):
            src = iframe.get("src", "")
            if "calendar.google.com" in src:
                return src

    return None
