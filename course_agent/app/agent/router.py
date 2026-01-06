# course-agent/app/agent/router.py
from course_agent.app.agent.state import CourseAgentState

def route_after_verify(state: CourseAgentState):
    if state.get("proposed_site_id"):
        return "critic"
    if state.get("done"):
        return "end"
    return "verify_site"

def route_after_critic(state: CourseAgentState):
    if state.get("verified_site_id"):
        return "extract_calendar"
    if state.get("done"):
        return "end"
    return "verify_site"