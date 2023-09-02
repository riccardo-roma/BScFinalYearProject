# Undergraduate Final Year Project May 2023

## Supervisor and Second Marker
Bo Yuan and Tatiana Tyukina

## Files
- application:
    - static: holds images for demonstration purposes
    - templates: holds all HTML files.
    - tests: contains unit tests file.
    - __init__.py
    - auth.py: contains routes related to authentication.
    - main.py: contains all other routes.
    - engine.py: contains all the functions used
    - forms.py: contains the WTForms classes for each form
- screenshots: contains commit screenshots form the previous gitlab repository
- .gitignore
- requirements.txt: contains all libraries that are needed.

## Installation (Mac Ventura 13.3.1)
1. Donwload MongoDB on your machine. Instruction can be found at: https://www.mongodb.com/try/download/community-kubernetes-operator
    1. Download MongoDB Compass at: https://www.mongodb.com/try/download/compass 
    2. Create a new connection and in the field 'URI' insert: mongodb://localhost:27017
    3. Click 'Connect'
    4. Create a database called footballRecommender
    5. Create 3 collections in that database called: 'players', 'teams' and 'users'
2. Open Terminal.
3. Create a new directory. 
4. cd into the new directory.
5. Clone the repository in the directory.
6. Open 'rr270' directory using command 'cd rr270'
7. Use command: 'python -m venv venv' to create a virtual enviroment in that directory.
8. Activate the virtual enviroment with command: source venv/bin/activate.
9. Use command: 'pip install -r requirements.txt' to install ALL required libraries.
10. Use command: export FLASK_APP=application
11. Use command: flask run to run the software.

