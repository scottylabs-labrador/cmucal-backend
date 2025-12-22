#!/usr/bin/env python3
"""
Script to process Handshake scraped data and upload to Supabase database.

Step 1: Extract event hosts from Excel files and add to organizations table.
"""

import os
import sys
import pandas as pd
import glob
from datetime import datetime
from pathlib import Path

# Add the parent directory to Python path to import app modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(project_root, ".env.development"))

from app.services.db import SessionLocal, engine
from app.models.models import Organization, Category
from sqlalchemy.exc import IntegrityError

def get_handshake_excel_files():
    """Get all handshake Excel files in the scraper directory."""
    scraper_dir = Path(__file__).parent
    excel_files = list(scraper_dir.glob("handshake_events_*.xlsx"))
    
    # Filter out temporary Excel files (starting with ~$)
    excel_files = [f for f in excel_files if not f.name.startswith("~$")]
    
    print(f"Found {len(excel_files)} handshake Excel files:")
    for file in excel_files:
        print(f"  - {file.name}")
    
    return excel_files

def extract_unique_event_hosts(excel_files):
    """Extract unique event hosts from all Excel files, prioritizing the newest."""
    all_hosts = set()
    
    # Sort files by modification time (newest first)
    excel_files_sorted = sorted(excel_files, key=lambda x: x.stat().st_mtime, reverse=True)
    
    print(f"\nProcessing {len(excel_files_sorted)} Excel files (newest first):")
    
    for i, excel_file in enumerate(excel_files_sorted):
        try:
            mod_time = datetime.fromtimestamp(excel_file.stat().st_mtime)
            print(f"\n{i+1}. Processing {excel_file.name} (modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')})...")
            df = pd.read_excel(excel_file)
            
            if 'Event Host' not in df.columns:
                print(f"  Warning: 'Event Host' column not found in {excel_file.name}")
                continue
            
            # Get unique hosts from this file, excluding NaN values
            hosts_in_file = df['Event Host'].dropna().unique()
            hosts_count = len(hosts_in_file)
            
            print(f"  Found {hosts_count} unique hosts in this file")
            if i == 0:  # Show details for the newest file
                print(f"  Sample hosts from newest file: {list(hosts_in_file[:5])}")
            
            # Add to overall set
            all_hosts.update(hosts_in_file)
            
        except Exception as e:
            print(f"  Error processing {excel_file.name}: {e}")
    
    # Convert to sorted list for consistent processing
    unique_hosts = sorted(list(all_hosts))
    
    print(f"\nTotal unique event hosts across all files: {len(unique_hosts)}")
    print("\nAll unique hosts:")
    for i, host in enumerate(unique_hosts, 1):
        print(f"  {i:2d}. {host}")
    
    return unique_hosts

def add_hosts_to_organizations_table(unique_hosts):
    """Add event hosts to the organizations table in Supabase."""
    
    if not unique_hosts:
        print("No hosts to add to database.")
        return []
    
    db = SessionLocal()
    added_orgs = []
    skipped_orgs = []
    
    try:
        print(f"\nStep 1: Adding {len(unique_hosts)} hosts to organizations table...")
        
        for host in unique_hosts:
            try:
                # Check if organization already exists
                existing_org = db.query(Organization).filter(Organization.name == host).first()
                
                if existing_org:
                    print(f"  ✓ Organization '{host}' already exists (ID: {existing_org.id})")
                    skipped_orgs.append({
                        'name': host,
                        'id': existing_org.id,
                        'created_at': existing_org.created_at
                    })
                    continue
                
                # Create new organization
                new_org = Organization(
                    name=host,
                    type="HANDSHAKE_HOST",  # Type to identify these as handshake event hosts
                    description=f"Organization created from Handshake event host: {host}"
                )
                
                db.add(new_org)
                db.flush()  # Get the ID without committing
                
                added_orgs.append({
                    'name': host,
                    'id': new_org.id,
                    'created_at': new_org.created_at
                })
                
                print(f"  ✓ Added organization '{host}' (ID: {new_org.id})")
                
            except IntegrityError as e:
                db.rollback()
                print(f"  ✗ Failed to add '{host}': {e}")
                continue
        
        # Commit all organization changes
        db.commit()
        
        print(f"\nStep 1 Summary:")
        print(f"  - Added: {len(added_orgs)} new organizations")
        print(f"  - Skipped: {len(skipped_orgs)} existing organizations")
        
        return added_orgs + skipped_orgs
        
    except Exception as e:
        db.rollback()
        print(f"Error adding organizations to database: {e}")
        return []
    
    finally:
        db.close()

def create_main_categories_for_orgs(organizations):
    """Create 'Main' category for each newly added organization."""
    
    if not organizations:
        print("No organizations to create categories for.")
        return []
    
    db = SessionLocal()
    added_categories = []
    skipped_categories = []
    
    try:
        print(f"\nStep 2: Creating 'Main' categories for organizations...")
        
        for org in organizations:
            try:
                org_id = org['id']
                org_name = org['name']
                
                # Check if 'Main' category already exists for this org
                existing_category = db.query(Category).filter(
                    Category.org_id == org_id,
                    Category.name == "Main"
                ).first()
                
                if existing_category:
                    print(f"  ✓ 'Main' category already exists for '{org_name}' (ID: {existing_category.id})")
                    skipped_categories.append({
                        'name': "Main",
                        'id': existing_category.id,
                        'org_id': org_id,
                        'org_name': org_name,
                        'created_at': existing_category.created_at
                    })
                    continue
                
                # Create new 'Main' category
                new_category = Category(
                    name="Main",
                    org_id=org_id
                )
                
                db.add(new_category)
                db.flush()  # Get the ID without committing
                
                added_categories.append({
                    'name': "Main",
                    'id': new_category.id,
                    'org_id': org_id,
                    'org_name': org_name,
                    'created_at': new_category.created_at
                })
                
                print(f"  ✓ Added 'Main' category for '{org_name}' (Category ID: {new_category.id})")
                
            except IntegrityError as e:
                db.rollback()
                print(f"  ✗ Failed to add 'Main' category for '{org_name}': {e}")
                continue
        
        # Commit all category changes
        db.commit()
        
        print(f"\nStep 2 Summary:")
        print(f"  - Added: {len(added_categories)} new 'Main' categories")
        print(f"  - Skipped: {len(skipped_categories)} existing 'Main' categories")
        
        return added_categories + skipped_categories
        
    except Exception as e:
        db.rollback()
        print(f"Error adding categories to database: {e}")
        return []
    
    finally:
        db.close()

def run_fresh_scrape():
    """Run the handshake scraper to get the latest data."""
    print("\n" + "=" * 60)
    print("RUNNING FRESH HANDSHAKE SCRAPE")
    print("=" * 60)
    
    try:
        # Run the handshake exporter to get fresh data
        print("Running handshake scraper and exporter...")
        result = os.system("cd /Users/amandalu/Documents/projects/cmucal-backend/scraper && python exporters/handshake_export_to_excel.py")
        
        if result == 0:
            print("✓ Fresh handshake data scraped successfully")
            return True
        else:
            print("✗ Failed to scrape fresh handshake data")
            return False
            
    except Exception as e:
        print(f"✗ Error running handshake scraper: {e}")
        return False

def main():
    """Main function to process handshake data - Steps 1 & 2."""
    
    print("=" * 60)
    print("HANDSHAKE TO SUPABASE PROCESSOR - STEPS 1 & 2")
    print("1. Extracting event hosts and adding to organizations table")
    print("2. Creating 'Main' categories for each organization")
    print("=" * 60)
    
    # Check database connection
    try:
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✓ Database connection successful")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        print("Please check your SUPABASE_DB_URL environment variable.")
        return
    
    # Step 0: Run fresh scrape to get latest data
    if not run_fresh_scrape():
        print("Failed to get fresh data. Proceeding with existing files...")
    
    # Step 1: Get Excel files (should now include the fresh one)
    excel_files = get_handshake_excel_files()
    
    if not excel_files:
        print("No handshake Excel files found. Please run the scraper first.")
        return
    
    # Step 2: Extract unique hosts
    unique_hosts = extract_unique_event_hosts(excel_files)
    
    if not unique_hosts:
        print("No event hosts found in Excel files.")
        return
    
    # Step 3: Add organizations to database
    organizations = add_hosts_to_organizations_table(unique_hosts)
    
    if not organizations:
        print("\n✗ Step 1 failed - no organizations were processed.")
        return
    
    # Step 4: Create 'Main' categories for organizations
    categories = create_main_categories_for_orgs(organizations)
    
    if organizations and categories:
        print(f"\n✅ Steps 1 & 2 completed successfully!")
        print(f"  📊 {len(organizations)} organizations are now available in the database.")
        print(f"  📁 {len(categories)} 'Main' categories created for organizations.")
        
        # Save results to file for reference
        results_file = f"handshake_organizations_categories_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(results_file, 'w') as f:
            f.write("Handshake Event Host Organizations & Categories\n")
            f.write("=" * 50 + "\n\n")
            f.write("ORGANIZATIONS:\n")
            f.write("-" * 20 + "\n")
            for org in organizations:
                f.write(f"ID: {org['id']}, Name: {org['name']}, Created: {org['created_at']}\n")
            
            f.write("\nCATEGORIES:\n")
            f.write("-" * 20 + "\n")
            for cat in categories:
                f.write(f"ID: {cat['id']}, Name: {cat['name']}, Org: {cat['org_name']} (ID: {cat['org_id']}), Created: {cat['created_at']}\n")
        
        print(f"  📄 Results saved to: {results_file}")
    else:
        print("\n✗ Steps 1 & 2 failed - organizations or categories were not processed properly.")

if __name__ == "__main__":
    main()
