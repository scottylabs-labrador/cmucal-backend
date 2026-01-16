from course_agent.app.services.iframe_scanner import find_google_calendar_iframe_url, derive_ical_link
from course_agent.app.services.html_fetcher import fetch_html

# Real data
# Test case: Find iframe on landing page
def test_finds_iframe_122():
    url = "https://www.cs.cmu.edu/~15122/"
    html = fetch_html(url)
    result = find_google_calendar_iframe_url(html, url)
    assert result == "https://calendar.google.com/calendar/b/1/embed?showTitle=0&showTabs=0&showCalendars=0&mode=WEEK&height=450&wkst=1&bgcolor=%23FFFFFF&src=andrew.cmu.edu_oclvc5roik51hr1ak1i29iavd8%40group.calendar.google.com&color=%23182C57&ctz=America%2FNew_York"
    
# Test case: Find iframe on landing page
def test_finds_iframe_210():
    url = "https://www.cs.cmu.edu/~15210/"
    html = fetch_html(url)
    result = find_google_calendar_iframe_url(html, url)
    assert result == "https://calendar.google.com/calendar/embed?height=500&wkst=1&ctz=America%2FNew_York&showPrint=0&mode=WEEK&src=c_bee38b13d3ebd2821f0ce848555eef524b9622fb4ac8562bbcbc63afdbc2dbeb%40group.calendar.google.com&color=%237cb342"

# Test case: Find iframe on landing page
def test_finds_iframe_313():
    url = "https://cmu-313.github.io/"
    html = fetch_html(url)
    result = find_google_calendar_iframe_url(html, url)
    assert result == "https://calendar.google.com/calendar/embed?src=c_6ff178194982fe3e4cba4c28641acbb98c8c493febf2d427b07c4259d3c49a1f%40group.calendar.google.com&ctz=America%2FNew_York&mode=WEEK"

# Test case: No iframe on landing page. No extra url to navigate.
def test_finds_no_iframe_401():
    url = "https://www.coursicle.com/cmu/courses/STA/36401/"
    html = fetch_html(url)
    result = find_google_calendar_iframe_url(html, url)
    assert result is None

# Test case: No iframe on landing page. Find iframe on other pages.
def test_finds_iframe_in_nav_150():
    url = "https://www.cs.cmu.edu/~15150/"
    html = fetch_html(url)
    result = find_google_calendar_iframe_url(html, url)
    assert result == "https://calendar.google.com/calendar/embed?src=c_5b3c3c4849862c434c1b26f56a6f108ac2cb759ecd1f6048bef6217eb5ef4eb8%40group.calendar.google.com&ctz=America%2FNew_York"

# Test case: No iframe on landing page. No iframe on other pages as well
def test_finds_no_iframe_259():
    url = "https://www.cs.cmu.edu/~harchol/PnC/class.html"
    html = fetch_html(url)
    result = find_google_calendar_iframe_url(html, url)
    assert result is None

# Test case: No iframe on landing page. No iframe on other pages as well
# Problem with ssl error
# def test_finds_iframe_in_nav_213():
#     url = "https://www.cs.cmu.edu/~213/"
#     html = fetch_html(url)
#     result = find_google_calendar_iframe_url(html, url)
#     assert result is None

