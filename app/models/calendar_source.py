from app.models.models import CalendarSource
from typing import Optional

def create_calendar_source(
    db_session,
    *,
    url: str,
    org_id: int,
    category_id: int,
    active: bool = True,
    notes: Optional[str] = None,
    default_event_type: Optional[str] = None,
    created_by_user_id: Optional[int] = None,
    **kwargs,
):
    calendar_source = CalendarSource(
        url=url,
        org_id=org_id,
        category_id=category_id,
        active=active,
        notes=notes,
        default_event_type=default_event_type,
        created_by_user_id=created_by_user_id,
        **kwargs,
    )

    db_session.add(calendar_source)
    db_session.flush()
    return calendar_source