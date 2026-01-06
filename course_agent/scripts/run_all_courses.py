# course-agent/scripts/run_all_courses.py
from app.db.repositories import fetch_all_courses
from app.db.supabase_client import supabase
from app.agent.graph import build_course_agent

def main():
    courses = fetch_all_courses()

    # Create a new agent run record, should increment agent_version if needed
    agent_run = supabase.table("agent_runs").insert({
        "agent_version": "v1"
    }).execute().data[0]["id"]

    agent = build_course_agent()

    for course in courses:
        final_state = agent.invoke({
            "course_id": course["id"],
            "course_number": course["course_number"],
            "course_name": course["course_name"],
            "agent_run_id": agent_run,
            "candidate_urls": [],
            "current_url_index": 0,
            "verified_site_id": None,
            "calendar_url": None,
            "done": False
        })



if __name__ == "__main__":
    main()
