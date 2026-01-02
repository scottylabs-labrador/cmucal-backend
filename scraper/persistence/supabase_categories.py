def ensure_lecture_category(db, org_id_by_key: dict) -> dict:
    """
    Ensure each org has a 'Lecture and Recitations' category.

    Returns:
        {org_id: category_id}
    """

    CATEGORY_NAME = "Lecture and Recitations"

    org_ids = set(org_id_by_key.values())

    # Fetch existing categories
    existing = (
        db.table("categories")
        .select("id, org_id, name")
        .in_("org_id", list(org_ids))
        .execute()
        .data
    )

    category_by_org = {
        row["org_id"]: row["id"]
        for row in existing
        if row["name"] == CATEGORY_NAME
    }

    # Create missing categories
    rows_to_insert = []

    for org_id in org_ids:
        if org_id not in category_by_org:
            rows_to_insert.append({
                "org_id": org_id,
                "name": CATEGORY_NAME,
            })

    if rows_to_insert:
        db.table("categories").insert(rows_to_insert).execute()

    # Re-fetch to get IDs
    all_categories = (
        db.table("categories")
        .select("id, org_id, name")
        .in_("org_id", list(org_ids))
        .execute()
        .data
    )

    return {
        row["org_id"]: row["id"]
        for row in all_categories
        if row["name"] == CATEGORY_NAME
    }
