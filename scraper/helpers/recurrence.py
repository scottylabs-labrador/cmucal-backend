from datetime import datetime, time
from typing import Optional
from app.models import FrequencyType
from scraper.models import ScheduleOfClasses

SOC_DAY_MAP = {
    "M": "MO",
    "T": "TU",
    "W": "WE",
    "R": "TH",
    "F": "FR",
    "S": "SA",
    "U": "SU",
}


def parse_soc_time(t: str) -> time:
    return datetime.strptime(t, "%I:%M%p").time()


def build_rrule_from_soc(
    soc: "ScheduleOfClasses",
) -> Optional[dict]:
    """
    Build a RecurrenceRule row from a ScheduleOfClasses object.
    """

    if not soc.lecture_days:
        return None

    # ---- BYDAY ----
    try:
        by_day = [SOC_DAY_MAP[d] for d in soc.lecture_days]
    except KeyError:
        raise ValueError(f"Invalid lecture_days: {soc.lecture_days}")

    # ---- DTSTART ----
    start_dt = datetime.combine(
        soc.sem_start,
        parse_soc_time(soc.lecture_time_start),
    )

    # ---- UNTIL (inclusive) ----
    until_dt = datetime.combine(
        soc.sem_end,
        time.max,
    )

    return {
        "frequency": FrequencyType.WEEKLY,
        "interval": 1,
        "start_datetime": start_dt,
        "until": until_dt,
        "by_day": by_day,
        "count": None,
        "by_month": None,
        "by_month_day": None,
        "orig_until": until_dt,
    }
