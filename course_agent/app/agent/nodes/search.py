# course-agent/app/agent/nodes/search.py
from course_agent.app.services.search import get_search_course_site
from course_agent.app.agent.state import CourseAgentState


def search_node(state: CourseAgentState):
    # Return a search function  
    search = get_search_course_site()
    # Array of 3 links for the course
    urls = search(
        f"{state['course_number']} {state['course_name']}",
        max_results=3,
    )
    # If no urls found
    if not urls:
        return {
            **state,
            "candidate_urls": [],
            "done": True,
            "terminal_status": "no_site_found"
        }
    # If urls found
    return {
        **state,
        "candidate_urls": urls,
        "current_url_index": 0,
    }
