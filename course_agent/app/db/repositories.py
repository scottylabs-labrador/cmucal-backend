# course-agent/app/db/repositories.py
from .supabase_client import supabase
from typing import Optional, Dict

def fetch_all_courses():
    return supabase.table("courses").select("id, course_number, course_name").execute().data


def insert_course_website(course_id, agent_run_id, url, score, debug=None):
    return supabase.table("course_websites").insert({
        "course_id": course_id,
        "agent_run_id": agent_run_id,
        "url": url,
        "relevance_score": score,
        "source": "search",
        "agent_debug": debug
    }).execute().data[0]["id"]


def verify_course_website(website_id, notes, final_score):
    supabase.table("course_websites").update({
        "is_verified": True,
        "verification_notes": notes,
        "relevance_score": final_score
    }).eq("id", website_id).execute()



def insert_calendar(website_id, iframe_url: Optional[str]):
    supabase.table("course_calendars").insert({
        "course_website_id": website_id,
        "calendar_type": "google" if iframe_url else None,
        "iframe_url": iframe_url,
        "detected": bool(iframe_url),
        "detection_method": "iframe_scan"
    }).execute()
