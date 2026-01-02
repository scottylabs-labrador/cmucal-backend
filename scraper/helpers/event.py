import hashlib

def make_event_key(soc):
    raw = f"{soc.course_num}|{soc.lecture_section}|{soc.semester}|{soc.lecture_time_start}|{soc.lecture_time_end}"
    return hashlib.sha256(raw.encode()).hexdigest()
