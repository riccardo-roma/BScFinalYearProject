# Undergraduate Final Year Project May 2023 (University of Leicester)

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

This application works with a local connection to a MongoDB database. The DB should contain 3 collections:

- Users:
    - _id: document index.
    - name: user's full name.
    - email: user's email used to log in.
    - accountType: can be one of two values, ‘Player’ or ‘Manager’, it determines if a user is a
      player or manager.
    - profileCreated: default as False and changes to ‘True’ once a user inserted their statistics.
    - birthday: user’s birthday.
    - teamManaged: This field is included only if this user is a manager and shows the team they
      manage.
    - password: user login password (encrypted).
- Players:
    - _id: document index.
    - full_name: player's full name (in all capital letters).
    - birthday_GMT: player’s birthday.
    - position: player’s playing position.
    - Current Club: their current club.
    - minutes_played_overall: total number of minutes played.
    - minutes_played_home: number of minutes played at home.
    - minutes_played_away: number of minutes played away.
    - nationality: player's nationality.
    - appearances_overall: total number of appearances.
    - appearances_home: number of home appearances.
    - apperances_away: number of away appearances.
    - goals_overall: total number of goals scored.
    - goals_home: number of goals scored at home.
    - goals_away: number of goals scored away.
    - assists_overall: total number of assists.
    - assists_home: number of assists at home.
    - assists_away: number of assists away.
    - penalty_goals: total number of penalties scored.
    - penalty_misses: total number of penalties missed.
    - clean_sheets_overall: total number of clean sheets.
    - yellow_cards_overall: total number of yellow cards.
    - red_cards_overall: total number of red cards.
- Teams:
    - _id: document index.
    - team_name: the team's name (in all capital letters).
    - matches_played: total number of matches played.
    - matches_played_home: number of matches played at home.
    - matches_played_away: number of matches played away.
    - wins: total number of wins.
    - wins_home: number of wins at home.
    - wins_away: number of wins away.
    - draws: total number of draws.
    - draws_home: number of draws at home.
    - draws_away: number of draws away.
    - losses: total number of losses.
    - losses_home: number of losses at home.
    - losses_away: number of losses away.
    - goals_scored: the total number of goals scored.
    - goals_conceded: the total number of goals conceded.
    - goals_scored_home: number of goals scored at home.
    - goals_scored_away: number of goals scored away.
    - goals_conceded_home: number of goals conceded at home.
    - goals_conceded_away: number of goals conceded away.
    - clean_sheets: total number of clean sheets.
    - clean_sheets_home: number of clean sheets at home.
    - clean_sheets_away: number of clean sheets away.
    - cards_total: total number of red and yellow cards received by each player or staff member
      on the team.
    - cards_total_home: number of cards received at home.
    - cards_total_away: number of cards received away.
    - average_possesion: average possession of past games in the season.
    - average_possesion_home: average possession of past home games in the season.
    - average_possesion_away: average possession of previous away games in the season.
    - shots: total number of shots taken.
    - shots_on_target: number of shots taken on target.
    - shots_off_target: number of shots taken off target.
    - fouls: total number of fouls committed. 
