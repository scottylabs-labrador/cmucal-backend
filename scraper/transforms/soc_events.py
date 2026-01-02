import datetime
from typing import List, Tuple

from scraper.helpers.recurrence import build_rrule_from_soc, parse_soc_time
from scraper.helpers.event import make_event_key


def build_events_and_rrules(
    soc_rows,
    org_id_by_key: dict,
    category_id_by_org: dict,
) -> Tuple[List[dict], List[dict]]:
    events = []
    rrules = []

    for soc in soc_rows:
        key = (soc.course_num, soc.semester)
        org_id = org_id_by_key[key]
        category_id = category_id_by_org[org_id]

        start_time = parse_soc_time(soc.lecture_time_start)
        end_time = parse_soc_time(soc.lecture_time_end)

        start_dt = datetime.datetime.combine(soc.sem_start, start_time)
        end_dt = datetime.datetime.combine(soc.sem_start, end_time)

        event_key = make_event_key(soc)

        event = {
            "event_key": event_key,        # temporary identity
            "title": f"{soc.course_num} {soc.lecture_section}",
            "start_datetime": start_dt,
            "end_datetime": end_dt,
            "is_all_day": False,
            "location": soc.location,
            "org_id": org_id,
            "category_id": category_id,
            "description": f"{soc.course_num} {soc.lecture_section}",
            "event_type": "ACADEMIC",
            "source_url": "https://enr-apps.as.cmu.edu/open/SOC/SOCServlet/completeSchedule",
        }

        events.append(event)

        rrule = build_rrule_from_soc(soc)
        if rrule:
            rrule["event_key"] = event_key
            rrules.append(rrule)

    return events, rrules
