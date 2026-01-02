from scraper.persistence.supabase_writer import get_supabase


def replace_recurrence_rules(db, rrules: list, event_id_by_key: dict):
    """ Delete all existing rules for the event and insert the new ones """

    if not rrules:
        return

    rows = []
    event_ids = set()

    for r in rrules:
        event_id = event_id_by_key[r["event_key"]]
        event_ids.add(event_id)

        row = dict(r)
        row["event_id"] = event_id
        row.pop("event_key")
        rows.append(row)

    db.table("recurrence_rules").delete().in_("event_id", list(event_ids)).execute()

    db.table("recurrence_rules").insert(rows).execute()
