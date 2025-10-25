# CMU Calendar Scraper

## Quick Start
1. `cd scraper`
2. Set up Handshake authentication (see below)
3. Run exporters:
   - `python exporters/handshake_export_to_excel.py`
   - `python exporters/tartanconnect_export_to_excel.py`
   - `python exporters/si_export_to_excel.py`
   - `python exporters/peer_tutoring_export_to_excel.py`

## Handshake Authentication Setup

The Handshake scraper requires authentication to access career events. Follow these steps:

### Step 1: Get Your Authentication Token
1. **Log into Handshake** at [app.joinhandshake.com](https://app.joinhandshake.com)
2. **Open browser developer tools** (Press F12 or right-click → Inspect)
3. **Go to Application tab** → Storage → Cookies → app.joinhandshake.com
4. **Find the 'hss-global' cookie** and copy its entire Value (it's a very long string starting with "eyJ...")

### Step 2: Set the Token (Choose One Method)

#### Method A: Using the Setup Script (Recommended)
```bash
python set_handshake_token.py
```
- Paste your token when prompted
- The script will show you how to make it permanent

#### Method B: Manual Setup
Add this line to your shell profile (`~/.zshrc` on Mac, `~/.bashrc` on Linux):
```bash
export HANDSHAKE_AUTH_TOKEN="your_very_long_token_here"
```

Then reload your shell:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

### Step 3: Verify Setup
Run the Handshake exporter to test:
```bash
python exporters/handshake_export_to_excel.py
```

If successful, you'll see events being scraped and exported to an Excel file.

## Load Data into Supabase

To upload scraped handshake data to the Supabase database:

```bash
cd scraper
python process_handshake_to_supabase.py
```

This script will:
1. Run fresh handshake scraping
2. Extract unique event hosts and add to `organizations` table
3. Process event data for database upload

**Requirements**: Ensure `SUPABASE_DB_URL` is set in your `.env.development` file.

### Troubleshooting
- **"HANDSHAKE_AUTH_TOKEN not set" error**: The environment variable isn't available. Try restarting your terminal or re-running the setup.
- **Authentication failed**: Your token may have expired. Get a fresh token from your browser and repeat the setup.
- **No events found**: Check that you're logged into the correct Handshake account and have access to CMU events.

# Old README

To use, first create a virtual environment: `python3 -m venv <myenvname>`

Then activate it:

On windows: `.\env\Scripts\activate.bat`
On mac: `source venv/bin/activate`

Then install needed packages: `pip3 install -r requirements.txt`

Then create a file `config.ini` that contains the link to the MONGO database in the format seen in `config.ini.example`.

Then launch the scraper: `python3 main.py`

--------

Updates for the future:
- fix peertutoring cause they switched from the login method to SSO one, breaking the whole scraper...
- improve the Handshake/TC mechanisms to automatically update login cookie information cause it is static at the moment
- might need to abstract "resource_source" out of each scraper file so it's not one to one (i.e. one scraper file like OfficeHoursScraper can query 5 different google calendars, and write to 5 different resource sources. this would
involve updating the update_database function slightly )
- more office hours
- write a backend in flask that connects with mongo and returns a list of events given filters (will also expand out reoccurring events for whole semester)