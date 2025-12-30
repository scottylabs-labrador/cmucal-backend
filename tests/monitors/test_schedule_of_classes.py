# tests/monitors/test_schedule_of_classes.py
import pathlib
from scraper.monitors.academic.schedule_of_classes import ScheduleOfClassesScraper

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def parse_fixture(name: str):
    scraper = ScheduleOfClassesScraper(db=None)
    html = load_fixture(name)
    fixed_html = scraper._fix_malformed_html(html)
    return scraper._parse_html(fixed_html)


def test_architecture_includes_48026():
    resources = parse_fixture("soc_architecture.html")
    course_ids = {r.course_id for r in resources}

    assert "48026" in course_ids
    assert "48105" in course_ids


def test_architecture_has_multiple_events_for_48105():
    resources = parse_fixture("soc_architecture.html")

    events_48105 = [r for r in resources if r.course_id == "48105"]

    # Lec + recitations
    assert len(events_48105) == 6
    assert {e.event_type for e in events_48105} == {"Lec", "A", "B", "C", "D", "E"}

def test_stagecraft_multiple_events():
    resources = parse_fixture("soc_stage.html")

    events = [r for r in resources if r.course_id == "54152"]
    # count D3 events in events.event_type
    d3_events = [e for e in events if e.event_type == "D3"]
    assert len(d3_events) == 3
    assert all(e.course_name == "Stagecraft: Rigging (3 units)" for e in d3_events)

def test_no_tba_or_empty_times():
    resources = parse_fixture("soc_architecture.html")

    for r in resources:
        assert r.lecture_days != "TBA"
        assert r.lecture_time_start
        assert r.lecture_time_end


def test_all_course_ids_are_numeric():
    resources = parse_fixture("soc_architecture.html")

    for r in resources:
        assert r.course_id.isdigit()


def test_semester_is_attached():
    resources = parse_fixture("soc_architecture.html")

    for r in resources:
        assert r.semester is not None
        assert "_" in r.semester  # e.g. Fall_26
