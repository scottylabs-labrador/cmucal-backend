def test_agent_accepts_site_and_calendar(
    mocker,
    ca_base_state,
):
    from course_agent.app.agent.graph import build_course_agent

    agent = build_course_agent()

    # search
    mocker.patch(
        'course_agent.app.services.search.get_search_course_site',
        return_value=lambda *_args, **_kwargs: ['https://www.cs.cmu.edu/~213']
    )

    # html fetch
    mocker.patch(
        'course_agent.app.services.html_fetcher.fetch_html',
        return_value="""
            <html>
              <iframe src="https://calendar.google.com/calendar/embed?src=test@cmu.edu"></iframe>
              syllabus lectures
            </html>
        """
    )

    # LLM
    mock_llm = mocker.Mock()
    mock_llm.invoke.side_effect = [
        type('R', (), {'content': 'yes'}),     # verifier
        type('R', (), {'content': 'accept'}),  # critic
    ]
    mocker.patch(
        'course_agent.app.services.llm.get_llm',
        return_value=mock_llm
    )

    # DB writes
    mocker.patch(
        'course_agent.app.db.repositories.upsert_course_website',
        return_value='site-1'
    )
    mocker.patch(
        'course_agent.app.db.repositories.verify_course_website'
    )
    mocker.patch(
        'course_agent.app.db.repositories.upsert_calendar_source'
    )

    state = agent.invoke(ca_base_state)

    assert state['terminal_status'] == 'success'
    assert state['verified_site_id'] == 'site-1'
    assert state['ical_link'].endswith('.ics')

def test_agent_rejects_first_site_and_continues(
    mocker,
    ca_base_state,
):
    from course_agent.app.agent.nodes.verify_site import verify_site_node
    from course_agent.app.agent.nodes.critic import critic_node

    state = {
        **ca_base_state,
        'candidate_urls': ['https://www.reddit.com/r/cmu/comments/p0t1q7/15112_or_15122/', 'https://www.coursicle.com/cmu/courses/CS/15112/'],
    }

    mocker.patch(
        'course_agent.app.services.html_fetcher.fetch_html',
        return_value='<html>random page</html>'
    )

    mock_llm = mocker.Mock()
    mock_llm.invoke.side_effect = [
        type('R', (), {'content': 'yes'}),
        type('R', (), {'content': 'reject'}),
    ]
    mocker.patch(
        'course_agent.app.services.llm.get_llm',
        return_value=mock_llm
    )

    mocker.patch(
        'course_agent.app.db.repositories.upsert_course_website',
        return_value='site-x'
    )

    state = verify_site_node(state)
    state = critic_node(state)

    assert state['current_url_index'] == 1
    assert state['proposed_site_id'] is None
    assert state['done'] is False

def test_no_site_found_when_search_empty(
    mocker,
    ca_base_state,
):
    from course_agent.app.agent.graph import build_course_agent

    agent = build_course_agent()

    mocker.patch(
        'course_agent.app.services.search.get_search_course_site',
        return_value=lambda *_args, **_kwargs: []
    )

    state = agent.invoke(ca_base_state)

    assert state['terminal_status'] == 'no_site_found'
    assert state['done'] is True

def test_site_without_calendar(
    mocker,
    ca_base_state,
):
    from course_agent.app.agent.graph import build_course_agent

    agent = build_course_agent()

    mocker.patch(
        'course_agent.app.services.search.get_search_course_site',
        return_value=lambda *_args, **_kwargs: ['https://www.cs.cmu.edu/~213']
    )


    mocker.patch(
        'course_agent.app.services.html_fetcher.fetch_html',
        return_value='<html>syllabus but no iframe</html>'
    )

    mock_llm = mocker.Mock()
    mock_llm.invoke.side_effect = [
        type('R', (), {'content': 'yes'}),
        type('R', (), {'content': 'accept'}),
    ]
    mocker.patch(
        'course_agent.app.services.llm.get_llm',
        return_value=mock_llm
    )

    mocker.patch(
        'course_agent.app.db.repositories.upsert_course_website',
        return_value='site-1'
    )

    state = agent.invoke(ca_base_state)

    assert state['terminal_status'] == 'no_calendar'
