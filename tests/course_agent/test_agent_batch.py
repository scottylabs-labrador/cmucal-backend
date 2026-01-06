from course_agent.app.agent.graph import build_course_agent

def test_agent_runs_multiple_courses(
    mocker,
    course_batch_factory,
):
    from course_agent.app.agent.graph import build_course_agent

    courses = course_batch_factory(3)
    agent = build_course_agent()

    mocker.patch(
        'course_agent.app.services.search.get_search_course_site',
        return_value=lambda *_args, **_kwargs: ['https://www.cs.cmu.edu/~213']
    )


    mocker.patch(
        'course_agent.app.services.html_fetcher.fetch_html',
        return_value='<html>syllabus</html>'
    )

    mock_llm = mocker.Mock()
    mock_llm.invoke.side_effect = (
        [type('R', (), {'content': 'yes'}),
         type('R', (), {'content': 'accept'})] * 3
    )

    mocker.patch(
        'course_agent.app.services.llm.get_llm',
        return_value=mock_llm
    )

    mocker.patch(
        'course_agent.app.db.repositories.upsert_course_website',
        return_value='site-x'
    )

    for course in courses:
        state = agent.invoke({
            **course,
            'candidate_urls': [],
            'current_url_index': 0,
            'verified_site_id': None,
            'iframe_url': None,
            'ical_link': None,
            'terminal_status': None,
            'done': False,
            'event_type': 'ACADEMIC',
        })

        assert state['verified_site_id'] == 'site-x'
