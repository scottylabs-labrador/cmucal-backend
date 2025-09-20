# Directions to run the backend

## 0. Git Ignore
Make a `.gitignore` file in the root directory and include the following code:
```
client_secret.json
.env
venv/
**/__pycache__/
*.pyc
```

## 1. Virtual Environment
(ignore this step if already have venv) If there isn't a venv folder, run `python3 -m venv venv` in terminal to create an venv.


- Next, run the following command to activate venv
    - macOS: `source venv/bin/activate`
    - windows: `venv\Scripts\activate`

- Once activated, you can install dependencies by `pip install -r requirements.txt`, and save them by running `pip freeze > requirements.txt`
- If you encounter an error with psycogp2, run `brew install postgresql` first.

## 2. Flask app
Open a terminal (in the backend folder with virtual environment), run `python run.py` to start the Flask app.

## 3. Supabase
(ignore this unless told otherwise) IF need to get the table schema from Supabase: in the terminal, run `sqlacodegen [SUPABASE_DB_URL from env file] --outfile models.py`
- comment out the `class Base` section in `models.py`
- add `from app.services.db import Base` to the top of `models.py`
- change all capitalized class names from plural to singular. i.e. class Events --> class Event. Don't change the lowercase names in quotes.

## 4. Database Migrations
(ignore this unless told otherwise) 

Note: add `APP_ENV=development` or `APP_ENV=production` before you run any alembic operations. 

Example commands:
```
APP_ENV=development alembic revision --autogenerate -m "<insert your message>"
APP_ENV=development alembic upgrade head
APP_ENV=production alembic upgrade head
```

- `upgrade head` = run migrations + bump version.
- `stamp head` = bump version only, no migrations executed.



## 5. Course data
(ignore this unless told otherwise) IF need to scrape data from cmu schedule of classes
1. `git checkout rust` 
2. Follow the instructions in the `rust` directory's README file. 
3. Then `git checkout main` 
4. Run `flask import-courses`

## 6. Scraped Info
(ignore this unless told otherwise) IF need to scrape data from handshake, tartanconnect, si, peer tutoring
1. `git pull` the scraper branch, and switch to this branch
2. `cd scraper`
3. Run these commands:
    - `python exporters/handshake_export_to_excel.py`
    - `python exporters/tartanconnect_export_to_excel.py`
    - `python exporters/si_export_to_excel.py`
    - `python exporters/peer_tutoring_export_to_excel.py`
4. Then you can see an excel sheet exported to the base folder

