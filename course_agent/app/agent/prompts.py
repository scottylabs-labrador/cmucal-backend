VERIFY_SITE_PROMPT = """
You are verifying whether a webpage is the official course website.

Course name: {course_name}
Page URL: {url}
Page snippet:
{text}

Answer ONLY yes or no.
"""

CRITIC_PROMPT = """
You are reviewing another agent's decision.

Course: {course_name}
Proposed website: {url}

Page content:
{text}

Question:
Is this clearly the official course website (not Piazza, Canvas, Reddit, or a generic page)?

Answer ONLY one word: accept or reject.
"""

