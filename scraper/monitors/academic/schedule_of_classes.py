import datetime
import bs4
from monitors.base_scraper import BaseScraper
from scraper.models import ScheduleOfClasses

class ScheduleOfClassesScraper(BaseScraper):
    def __init__(self, db):
        super().__init__(db, "Schedule of Classes", "SOC")
    
    def scrape(self):
        print("Running Schedule of Classes scraper...")
        resources = self._fetch_courses()
        for resource in resources:
            print(f"Added course: {resource.course_id} - {resource.course_name}") 
        # Add the logic to store data in database

    def scrape_data_only(self):
        resources = self._fetch_courses()
        for resource in resources:
            print(f"Added course: {resource.course_id} - {resource.course_name}") 
        return resources

    def _fetch_courses(self):
        semester = self.getCurrentSemester()
        print(f"Current semester identified as: {semester}")

        url = "https://enr-apps.as.cmu.edu/assets/SOC/" + semester + ".htm"
        response = self.session.get(url, headers=self.headers)
        response.raise_for_status()
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        print("Successfully fetched and parsed the schedule of classes page.")

        tables = soup.find_all('table', class_='course')
        resources = []
        for table in tables:
            rows = table.find_all('tr')[3:]  # Skip header rows
            for course in rows:
                cols = course.find_all('td')
                if len(cols) < 7:
                    continue  # Skip rows that don't have enough columns
                course_id = cols[0].text.strip()
                course_name = cols[1].text.strip()
                section_schedule = cols[3].text.strip()
                days = cols[4].text.strip()
                time_start = cols[5].text.strip()
                time_end = cols[6].text.strip()
                location = cols[7].text.strip() if len(cols) > 7 else "TBA"

                resource = ScheduleOfClasses(
                    id=None,
                    course_id=course_id,
                    course_name=course_name,
                    lecture_days=days,
                    lecture_time=f"{time_start} - {time_end}",
                    recitation_days=None,
                    recitation_time=None,
                    location=location
                )
                resources.append(resource)
        return resources

    def getCurrentSemester(self):
        range_data = {
            (datetime.datetime(2025, 1, 12), datetime.datetime(2025, 5, 1)): "sched_layout_spring",
            (datetime.datetime(2025, 5, 12), datetime.datetime(2025, 6, 18)): "sched_layout_summer_1",
            (datetime.datetime(2025, 6, 23), datetime.datetime(2025, 7, 31)): "sched_layout_summer_2",
            (datetime.datetime(2025, 8, 25), datetime.datetime(2025, 12, 12)): "sched_layout_fall"
        }
        current_date = datetime.datetime.now()

        for date_range, semester in range_data.items():
            if date_range[0] <= current_date <= date_range[1]:
                return semester
        print("Warning: Current date does not fall within any defined semester ranges.")
