import datetime
import bs4
import requests
import urllib3  # <-- 1. Import urllib3 to suppress warnings
from monitors.base_scraper import BaseScraper
import re


class ScheduleOfClasses:
    def __init__(
        self,
        id,
        course_id,
        course_name,
        event_type,
        lecture_days,
        lecture_time_start,
        lecture_time_end,
        location,
        semester,
    ):
        self.id = id
        self.course_id = course_id
        self.course_name = course_name
        self.event_type = event_type
        self.lecture_days = lecture_days
        self.lecture_time_start = lecture_time_start
        self.lecture_time_end = lecture_time_end
        self.location = location
        self.semester = semester


class ScheduleOfClassesScraper(BaseScraper):
    def __init__(self, db):
        super().__init__(db, "Schedule of Classes", "SOC")

        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }

        # --- 4. NEW FIX: Disable SSL verification for this session ---
        self.session.verify = False
        # Suppress only the InsecureRequestWarning
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        # --- END NEW FIX ---

    def scrape(self):
        print("Running Schedule of Classes scraper...")
        resources = self._fetch_courses()
        for resource in resources:
            print(f"Added course: {resource.course_id} - {resource.course_name}")
        # Add the logic to store data in database

    def scrape_data_only(self):
        resources = self._fetch_courses()
        return resources

    def _fetch_courses(self):
        semester, semester_label = self.getCurrentSemester()
        if not semester:
            print("Error: Could not determine current semester. Stopping scrape.")
            return []  # Return an empty list if no semester is found

        print(f"Current semester identified as: {semester}")

        url = "https://enr-apps.as.cmu.edu/assets/SOC/" + semester + ".htm"

        try:
            # Use the initialized session and headers
            # The session will now use verify=False automatically
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()

            # Fix malformed HTML: Insert <TR> before orphaned <TD> tags
            # Pattern: After a row ending with </TR>, if the next tag is <TD>, insert <TR>

            fixed_html = response.text

            # Replace pattern: </TR>\n<TD with </TR>\n<TR><TD
            # This adds the missing <TR> tag after section headers
            fixed_html = re.sub(
                r"(</TR>)\s*(<TD)", r"\1\n<TR>\2", fixed_html, flags=re.IGNORECASE
            )

            print("Fixed malformed HTML by inserting missing <TR> tags")

            # Debug: save both versions
            # with open("debug_response_original.html", "w", encoding="utf-8") as f:
            #     f.write(response.text)
            # with open("debug_response_fixed.html", "w", encoding="utf-8") as f:
            #     f.write(fixed_html)
            # print("Saved original and fixed HTML files")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL: {url}")
            print(f"Exception: {e}")
            return []

        soup = bs4.BeautifulSoup(fixed_html, "html.parser")
        print("Successfully fetched and parsed the schedule of classes page.")

        all_tables = soup.find_all("table", {"border": "0"})

        # Now, filter these tables to find only the ones that are *course* tables
        tables = []
        for t in all_tables:
            header_rows = t.find_all("tr")
            # Check if table has at least 2 rows, and one of the first three rows contains <b>Course</b>
            if any(r.find("b", string="Course") for r in header_rows[:3]):
                tables.append(t)

        # --- END MODIFICATION ---

        if not tables:
            print("Scraper found no course tables on the page.")
        # --- END DEBUGGING ---

        resources = []
        for table_idx, table in enumerate(tables):
            rows = table.find_all("tr")

            last_course_id = None
            last_course_name = None

            # Process normal <tr> rows
            for row_idx, course in enumerate(rows):
                cols = course.find_all("td")
                last_course_id, last_course_name = self._process_row_columns(
                    cols, last_course_id, last_course_name, semester_label, resources
                )

        print(f"Scraper found {len(resources)} courses.")
        return resources

    def _process_row_columns(
        self, cols, last_course_id, last_course_name, semester_label, resources
    ):
        """Process a set of columns representing a course row"""
        if len(cols) < 7:
            return last_course_id, last_course_name

        raw_course_id = cols[0].text.strip()
        raw_course_name = cols[1].text.strip()
        lecture_section = cols[3].text.strip()

        # Track the base course name and last lecture section separately
        if not hasattr(self, "_last_base_course_name"):
            self._last_base_course_name = None
        if not hasattr(self, "_last_lecture_section"):
            self._last_lecture_section = None

        # Determine the course name to use for this row
        if raw_course_id:
            # New course row - this becomes the base
            last_course_id = raw_course_id
            last_course_name = raw_course_name
            self._last_base_course_name = raw_course_name
        elif raw_course_name:
            # Continuation row with subtitle - combine base + subtitle
            last_course_name = self._last_base_course_name + " " + raw_course_name
        # else: no course_id and no course_name means we keep last_course_name as-is

        # Update lecture section if present
        if lecture_section:
            self._last_lecture_section = lecture_section
        else:
            # Use the last known lecture section
            lecture_section = self._last_lecture_section

        if not last_course_id or not self.is_real_course_row(last_course_id):
            return last_course_id, last_course_name

        days = cols[4].text.strip()
        time_start = cols[5].text.strip()
        time_end = cols[6].text.strip()
        location = cols[7].text.strip() if len(cols) > 7 else "TBA"

        if days == "TBA" or not time_start:
            return last_course_id, last_course_name

        resource = ScheduleOfClasses(
            id=None,
            course_id=last_course_id,
            course_name=last_course_name,
            event_type=lecture_section,
            lecture_days=days,
            lecture_time_start=time_start,
            lecture_time_end=time_end,
            location=location,
            semester=semester_label,
        )
        resources.append(resource)

        return last_course_id, last_course_name

    def getCurrentSemester(self):
        current_date = datetime.datetime.now()

        ranges = [
            (
                datetime.datetime(2025, 12, 20),
                datetime.datetime(2026, 5, 1),
                "sched_layout_spring",
                "Spring",
            ),
            (
                datetime.datetime(2026, 5, 10),
                datetime.datetime(2026, 6, 18),
                "sched_layout_summer_1",
                "Summer1",
            ),
            (
                datetime.datetime(2026, 6, 20),
                datetime.datetime(2026, 7, 31),
                "sched_layout_summer_2",
                "Summer2",
            ),
            (
                datetime.datetime(2026, 8, 15),
                datetime.datetime(2026, 12, 12),
                "sched_layout_fall",
                "Fall",
            ),
        ]

        for start, end, soc_layout, semester_name in ranges:
            if start <= current_date <= end:
                year_suffix = end.year % 100  # based on END date
                semester_label = f"{semester_name}_{year_suffix}"
                return soc_layout, semester_label

        print("Warning: Current date does not fall within any defined semester ranges.")
        return None, None

    def is_real_course_row(self, course_id):
        return course_id.isdigit()
