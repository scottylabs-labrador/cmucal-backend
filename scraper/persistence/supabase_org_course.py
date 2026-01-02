def upsert_orgs(db, orgs: dict) -> dict:
    """
    Upserts organizations and returns a mapping:
        {(course_num, semester): org_id}
    """
    data = list(orgs.values())

    # Upsert: insert or update on conflict
    db.table("organizations").upsert(data, on_conflict="name").execute()

    # Fetch IDs back
    names = [o["name"] for o in data]

    res = db.table("organizations").select("id,name").in_("name", names).execute()

    name_to_id = {row["name"]: row["id"] for row in res.data}

    # Rebuild mapping aligned with input keys
    org_id_by_key = {}

    for key, org in orgs.items():
        org_id_by_key[key] = name_to_id[org["name"]]

    return org_id_by_key


def upsert_courses(db, courses: dict, org_id_by_key: dict):
    """
    Upserts courses and appends semester if it already exists.
    """

    course_numbers = [c["course_number"] for c in courses.values()]

    # Fetch existing courses
    existing = (
        db.table("courses")
        .select("id, course_number, semesters")
        .in_("course_number", course_numbers)
        .execute()
        .data
    )

    existing_by_number = {row["course_number"]: row for row in existing}

    # Merge semesters
    rows_to_upsert = []

    for (course_num, semester), course in courses.items():
        org_id = org_id_by_key[(course_num, semester)]

        if course_num in existing_by_number:
            existing_semesters = existing_by_number[course_num]["semesters"] or []
            merged_semesters = sorted(set(existing_semesters + course["semesters"]))
        else:
            merged_semesters = course["semesters"]

        rows_to_upsert.append(
            {
                "course_number": course_num,
                "course_name": course["course_name"],
                "semesters": merged_semesters,
                "org_id": org_id,
            }
        )

    # Upsert merged result
    db.table("courses").upsert(rows_to_upsert, on_conflict="course_number").execute()
