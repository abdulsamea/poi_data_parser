# Django POI Admin

A Django 4/5 application (Python 3.10+) that imports Points of Interest (PoIs) from CSV, JSON, and XML via a management command and lets the data be browsed in the Django Admin with search and category filtering.

## Working of this project

- I have built this app to utilize sqlite for easier db access.
- Also added progress logs in case the file to be uploaded is large (e.g. 100K records)

## How to setup this codebase on your local machine

1. Clone and enter the project directory

2. Create and activate a virtual environment (Windows)

- python -m venv .venv
- .venv\Scripts\activate

3. Install dependencies (Only Django is added in here)

- pip install -r requirements.txt

4. Database setup (migrations)

- python manage.py makemigrations
- python manage.py migrate

5. Create an admin user

- Use CMD or powershell or editor terminal and type in `python manage.py createsuperuser` and follow the instructions shown. Remember the credentials for the admin user created in this step.

6. Prepare sample data

- Place sample data somewhere in your local machine

7. Import data (one or multiple files)

- Examples:
  - python manage.py import_pois data/pois.json
  - python manage.py import_pois data/pois.csv data/pois.xml data/pois.csv

8. Run the development server

- Default: python manage.py runserver

9. Browse the Admin

- Open http://127.0.0.1:8000/admin/ (the URL is set by default on running the server) and log in with the superuser created earlier.
- Navigate to PoIs to view records with:
  - Columns: id, name, external_id, category, avg_rating.
  - Filters: category (sidebar).
  - Search: internal ID (pk), external_id, name.
