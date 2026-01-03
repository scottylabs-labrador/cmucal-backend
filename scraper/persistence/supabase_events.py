from scraper.persistence.supabase_writer import chunked, get_supabase
from scraper.helpers.event import make_event_key


def insert_events(db, events: list) -> dict:
    """
    Inserts events if they do not already exist.
    Returns mapping: event_key -> event_id
    """

    # fetch existing events for involved orgs
    org_ids = list({e["org_id"] for e in events})

    existing = []
    for batch in chunked(org_ids, 200):
        res = (
            db.table("events")
            .select("id, title, start_datetime, end_datetime, org_id")
            .in_("org_id", batch)
            .execute()
            .data
        )
        existing.extend(res)

    existing_by_key = {}
    for row in existing:
        # reconstructs a minimal object to satisfy make_event_key
        fake_soc = type(
            "SOC",
            (),
            {
                "course_num": row["title"].split()[0],
                "lecture_section": row["title"].split()[1],
                "semester": None,
                "lecture_time_start": row["start_datetime"].strftime("%I:%M%p"),
                "lecture_time_end": row["end_datetime"].strftime("%I:%M%p"),
            },
        )
        existing_by_key[make_event_key(fake_soc)] = row["id"]

    # insert missing
    rows_to_insert = []
    event_id_by_key = {}

    for e in events:
        key = e["event_key"]

        if key in existing_by_key:
            event_id_by_key[key] = existing_by_key[key]
        else:
            row = dict(e)
            row.pop("event_key")
            rows_to_insert.append(row)

    if rows_to_insert:
        db.table("events").insert(rows_to_insert).execute()

    # refetch inserted ids
    inserted = []
    for batch in chunked(org_ids, 200):
        res = (
            db.table("events")
            .select("id, title, start_datetime, end_datetime, org_id")
            .in_("org_id", batch)
            .execute()
            .data
        )
        inserted.extend(res)

    for row in inserted:
        fake_soc = type(
            "SOC",
            (),
            {
                "course_num": row["title"].split()[0],
                "lecture_section": row["title"].split()[1],
                "semester": None,
                "lecture_time_start": row["start_datetime"].strftime("%I:%M%p"),
                "lecture_time_end": row["end_datetime"].strftime("%I:%M%p"),
            },
        )
        event_id_by_key[make_event_key(fake_soc)] = row["id"]

    return event_id_by_key
