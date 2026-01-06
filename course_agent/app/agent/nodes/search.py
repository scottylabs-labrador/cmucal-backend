# course-agent/app/agent/nodes/search.py
from app.services.search import search_course_site
from app.agent.state import CourseAgentState

def search_node(state: CourseAgentState):
    urls = search_course_site(state["course_name"])
    return {
        **state,
        "candidate_urls": urls,
        "current_url_index": 0
    }