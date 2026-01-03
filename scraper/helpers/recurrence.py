from datetime import datetime, time
from typing import Optional
from app.models import FrequencyType
from scraper.models import ScheduleOfClasses

from datetime import datetime, time
from typing import Optional
from app.models import FrequencyType

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


def build_rrule_from_parts(
    *,
    lecture_days: str,
    sem_start,
    sem_end,
) -> Optional[dict]:

    if not lecture_days:
        return None

    by_day = [SOC_DAY_MAP[d] for d in lecture_days]

    until_dt = datetime.combine(sem_end, time.max)

    # # ---- DTSTART ----
    # # ignore this part because we already have start_dt in the event
    # start_dt = datetime.combine(
    #     sem_start,
    #     parse_soc_time(soc.lecture_time_start),
    # )

    return {
        "frequency": FrequencyType.WEEKLY,
        "interval": 1,
        "by_day": by_day,
        # "start_datetime": start_dt,
        "until": until_dt,
        "count": None,
        "by_month": None,
        "by_month_day": None,
        "orig_until": until_dt,
    }