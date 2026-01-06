import pytest


@pytest.fixture
def course_factory():
    def create_course(
        *,
        id="1",
        org,
        course_number="15213",
        course_name="Intro to Computer Systems",
    ):
        return {
            "id": id,
            "org_id": org.id,
            "course_number": course_number,
            "course_name": course_name,
        }

    return create_course
