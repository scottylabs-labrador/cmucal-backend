# course-agent/app/agent/nodes/extract_calendar.py
from app.services.html_fetcher import fetch_html
from app.services.iframe_scanner import find_google_calendar_iframe
from app.db.repositories import insert_calendar
from app.agent.state import CourseAgentState

def extract_calendar_node(state: CourseAgentState):
    html = state.get("verified_site_html")
    website_id = state.get("verified_site_id")

    if not html or not website_id:
        return {**state, "done": True}

    iframe_url = find_google_calendar_iframe(html)

    insert_calendar(website_id, iframe_url)

    return {
        **state,
        "calendar_url": iframe_url,
        "done": True
    }
