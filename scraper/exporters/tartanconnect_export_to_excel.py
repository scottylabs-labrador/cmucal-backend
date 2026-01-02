import os
import sys
import pandas as pd
from datetime import datetime

from scraper.monitors.academic import SIScraper, DropInScraper, OfficeHoursScraper, PeerTutoringScraper
from scraper.monitors.career_club import TartanConnectScraper

# No MongoDB dependency needed for export-only mode

def scrape_and_export():
    # Initialize scrapers WITHOUT database connection - just pass None
    academic_scrapers = [
        SIScraper(None),
        DropInScraper(None),
        OfficeHoursScraper(None),
        PeerTutoringScraper(None)
    ]

    career_club_scrapers = [
        TartanConnectScraper(None)  # Only TartanConnect scraper
    ]
    
    all_events = []
    
    # Run each scraper to get data directly (without database operations)
    for scraper in academic_scrapers + career_club_scrapers:
        try:
            print(f"Running {str(scraper)} scraper...")
            # Get scraped data directly instead of calling scrape() which updates database
            resources = scraper.scrape_data_only()
            
            # Convert resources to event data for Excel
            for resource in resources:
                for event in resource.events:
                    if hasattr(resource, 'course_id'):  # Academic event
                        event_data = {
                            'Resource Type': resource.resource_type,
                            'Source': resource.resource_source,
                            'Course ID': getattr(resource, 'course_id', ''),
                            'Course Name': getattr(resource, 'course_name', ''),
                            'Professor': getattr(resource, 'professor', ''),
                            'Instructor': getattr(resource, 'instructor', ''),
                            'Start Time': event.start_datetime.replace(tzinfo=None) if hasattr(event.start_datetime, 'replace') else event.start_datetime,
                            'End Time': event.end_datetime.replace(tzinfo=None) if hasattr(event.end_datetime, 'replace') else event.end_datetime,
                            'Location': event.location,
                            'Recurrence': str(event.recurrence) if event.recurrence else ''
                        }
                    else:  # Career/club event
                        event_data = {
                            'Resource Type': resource.resource_type,
                            'Source': resource.resource_source,
                            'Event Name': getattr(resource, 'event_name', ''),
                            'Event Host': getattr(resource, 'event_host', ''),
                            'Categories': ', '.join(getattr(resource, 'categories', [])),
                            'Start Time': event.start_datetime.replace(tzinfo=None) if hasattr(event.start_datetime, 'replace') else event.start_datetime,
                            'End Time': event.end_datetime.replace(tzinfo=None) if hasattr(event.end_datetime, 'replace') else event.end_datetime,
                            'Location': event.location,
                            'Recurrence': str(event.recurrence) if event.recurrence else ''
                        }
                    all_events.append(event_data)
                    print(f"Added event: {event_data}")
                    
        except Exception as e:
            print(f"Error running {str(scraper)} scraper: {str(e)}")
    
    # Convert to DataFrame and save to Excel
    if all_events:
        df = pd.DataFrame(all_events)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), f'tartanconnect_events_{timestamp}.xlsx')
        df.to_excel(output_file, index=False)
        print(f"\nEvents exported to {output_file}")
        print(f"Total events exported: {len(all_events)}")
    else:
        print("No events were found to export")

if __name__ == "__main__":
    scrape_and_export() 