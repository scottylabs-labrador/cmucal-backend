from course_agent.app.services.iframe_scanner import find_google_calendar_iframe, derive_ical_link
from course_agent.app.services.html_fetcher import fetch_html

def test_finds_google_calendar_iframe():
    html = """
    <html>
      <body>
        <iframe src="https://calendar.google.com/calendar/embed?src=test@cmu.edu"></iframe>
      </body>
    </html>
    """

    result = find_google_calendar_iframe(html)

    assert result == "https://calendar.google.com/calendar/embed?src=test@cmu.edu"


def test_returns_none_when_no_iframe():
    html = "<html><body>No iframe here</body></html>"

    assert find_google_calendar_iframe(html) is None

def test_ignores_non_google_iframe():
    html = """
    <html>
      <body>
        <iframe src="https://youtube.com/embed/xyz"></iframe>
      </body>
    </html>
    """

    assert find_google_calendar_iframe(html) is None

def test_returns_first_google_calendar_iframe():
    html = """
    <html>
      <body>
        <iframe src="https://example.com"></iframe>
        <iframe src="https://calendar.google.com/calendar/embed?src=abc@cmu.edu"></iframe>
        <iframe src="https://calendar.google.com/calendar/embed?src=def@cmu.edu"></iframe>
      </body>
    </html>
    """

    result = find_google_calendar_iframe(html)

    assert result == "https://calendar.google.com/calendar/embed?src=abc@cmu.edu"


def test_derives_ical_link_from_iframe_url():
    iframe_url = (
        "https://calendar.google.com/calendar/embed"
        "?src=test@cmu.edu&ctz=America/New_York"
    )

    result = derive_ical_link(iframe_url)

    assert result == (
        "https://calendar.google.com/calendar/ical/"
        "test@cmu.edu/public/basic.ics"
    )

def test_returns_none_if_src_missing():
    iframe_url = "https://calendar.google.com/calendar/embed?ctz=UTC"

    assert derive_ical_link(iframe_url) is None

def test_full_calendar_extraction_flow():
    html = """
    <html>
      <body>
        <iframe src="https://calendar.google.com/calendar/embed?src=test@cmu.edu"></iframe>
      </body>
    </html>
    """

    iframe = find_google_calendar_iframe(html)
    ical = derive_ical_link(iframe)

    assert iframe is not None
    assert ical.endswith("/test@cmu.edu/public/basic.ics")


# Real data
def test_finds_iframe_122():
    url = "https://www.cs.cmu.edu/~15122/"
    html = fetch_html(url)
    result = find_google_calendar_iframe(html)
    assert result == "https://calendar.google.com/calendar/b/1/embed?showTitle=0&showTabs=0&showCalendars=0&mode=WEEK&height=450&wkst=1&bgcolor=%23FFFFFF&src=andrew.cmu.edu_oclvc5roik51hr1ak1i29iavd8%40group.calendar.google.com&color=%23182C57&ctz=America%2FNew_York"
    
def test_finds_iframe_210():
    url = "https://www.cs.cmu.edu/~15210/"
    html = fetch_html(url)
    result = find_google_calendar_iframe(html)
    assert result == "https://calendar.google.com/calendar/embed?height=500&wkst=1&ctz=America%2FNew_York&showPrint=0&mode=WEEK&src=c_bee38b13d3ebd2821f0ce848555eef524b9622fb4ac8562bbcbc63afdbc2dbeb%40group.calendar.google.com&color=%237cb342"

def test_finds_iframe_313():
    url = "https://cmu-313.github.io/"
    html = fetch_html(url)
    result = find_google_calendar_iframe(html)
    assert result == "https://calendar.google.com/calendar/embed?src=c_6ff178194982fe3e4cba4c28641acbb98c8c493febf2d427b07c4259d3c49a1f%40group.calendar.google.com&ctz=America%2FNew_York&mode=WEEK"

def test_finds_no_iframe_401():
    url = "https://www.coursicle.com/cmu/courses/STA/36401/"
    html = fetch_html(url)
    result = find_google_calendar_iframe(html)
    assert result is None
