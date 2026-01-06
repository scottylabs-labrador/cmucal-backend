# course-agent/app/agent/nodes/verify_site.py
from course_agent.app.services.html_fetcher import fetch_html
from course_agent.app.services.llm import get_llm
from course_agent.app.agent.prompts import VERIFY_SITE_PROMPT
from course_agent.app.db.repositories import upsert_course_website
from course_agent.app.agent.state import CourseAgentState
from course_agent.app.agent.scores import heuristic_score, VERIFIER_SCORES


def verify_site_node(state: CourseAgentState):
    idx = state["current_url_index"]
    urls = state["candidate_urls"]

    if idx >= len(urls):
        return {
            **state,
            "done": True,
            "terminal_status": "no_site_found"
        }

    url = urls[idx]
    html = fetch_html(url)
    snippet = html[:1500]

    formatted_course_name = f"{state['course_number'][0:2]}-{state['course_number'][2:4]} {state['course_name']}"
    llm = get_llm()
    response = (
        llm.invoke(
            VERIFY_SITE_PROMPT.format(
                course_name=formatted_course_name, url=url, text=snippet
            )
        )
        .content.strip()
        .lower()
    )

    website_id = upsert_course_website(
        course_id=state["course_id"],
        agent_run_id=state["agent_run_id"],
        url=url,
        score=0.9 if response == "yes" else 0.2,
        debug={"verifier_response": response},
    )
    
    if response != "yes":
        return {
            **state,
            "current_url_index": idx + 1
        }

    verifier_score = VERIFIER_SCORES.get(response, 0.1)
    heur_score = heuristic_score(url, html)

    return {
        **state,
        "proposed_site_id": website_id,
        "proposed_site_url": url,
        "proposed_site_html": html,
        "verifier_score": verifier_score,
        "heuristic_score": heur_score
    }

