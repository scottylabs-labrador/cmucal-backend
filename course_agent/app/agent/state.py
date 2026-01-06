from typing import TypedDict, Optional, List

class CourseAgentState(TypedDict):
    course_id: str
    course_number: str
    course_name: str
    agent_run_id: str

    candidate_urls: List[str]
    current_url_index: int

    proposed_site_id: Optional[str]
    proposed_site_url: Optional[str]

    verified_site_id: Optional[str]
    calendar_url: Optional[str]

    critic_decision: Optional[str]  # "accept" | "reject"

    verifier_score: Optional[float]
    critic_score: Optional[float]
    heuristic_score: Optional[float]
    final_score: Optional[float]

    done: bool

