from scraper.monitors.academic import ScheduleOfClassesScraper
from scraper.persistence.supabase_categories import ensure_lecture_category
from scraper.transforms.soc_org_course import build_orgs_and_courses
from scraper.persistence.supabase_writer import get_supabase
from scraper.persistence.supabase_org_course import upsert_orgs, upsert_courses

from scraper.transforms.soc_events import build_events_and_rrules
from scraper.persistence.supabase_events import insert_events
from scraper.persistence.supabase_recurrence import replace_recurrence_rules

from app.env import load_env
ENV = load_env()

def export_soc():
    """ Scrape the Schedule of Classes and export to Supabase 
        - Note that nothing rolls back automatically.
        - The system is designed to heal itself on rerun, and does not rely on rollback
    """
    db = get_supabase()
    scraper = ScheduleOfClassesScraper(db, semester_label="Spring_26")
    resources = scraper.scrape_data_only()

    # orgs + courses
    orgs, courses = build_orgs_and_courses(resources)
    org_id_by_key = upsert_orgs(db, orgs)
    # for (course_num, semester), org_id in org_id_by_key.items():
    #     print(course_num, semester, org_id)
    upsert_courses(db, courses, org_id_by_key)
    print(f"✅ {len(orgs)} orgs and {len(courses)} courses")

    # categories
    category_id_by_org = ensure_lecture_category(db, org_id_by_key)
    print(f"✅ {len(category_id_by_org)} categories")

    # events + recurrence rules
    events, rrules = build_events_and_rrules(resources, org_id_by_key, category_id_by_org)
    event_id_by_key = insert_events(db, events)
    replace_recurrence_rules(db, rrules, event_id_by_key)
    print(f"✅ {len(events)} events and {len(rrules)} recurrence rules")


if __name__ == "__main__":
    export_soc()