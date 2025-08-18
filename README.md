# Directions to run the backend

## 1. Virtual Environment
(ignore this step if already have venv) If there isn't a venv folder, run `python3 -m venv venv` in terminal to create an venv.


- Next, run the following command to activate venv
    - macOS: `source venv/bin/activate`
    - windows: `venv\Scripts\activate`

- Once activated, you can install dependencies by `pip install -r requirements.txt`, and save them by running `pip freeze > requirements.txt`
- If you encounter an error with psycogp2, run `brew install postgresql` first.

## 2. Course data
IF need to scrape data from cmu schedule of classes
- first follow the instructions in the `rust` directory's README file. 
- Then, cd into the backend folder, and run `flask import-courses`
