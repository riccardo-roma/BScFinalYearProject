#Imports
from flask import render_template, Blueprint, session, redirect, url_for, flash
from flask_pymongo import MongoClient
from .forms import *
from werkzeug.security import generate_password_hash
import random
import pandas as pd
from .engine import recomend, topScorers, mostWins, teamsRank, playerRank, myStats, myTeamStats, teamTopScorers

main = Blueprint('main', __name__)

client = MongoClient('localhost', 27017) #Establish connection with local MongoDB server
db = client.footballRecommender

#Database collections
player_collection = db.players
user_collection = db.users
teams_collection = db.teams

@main.route('/', methods=('GET', 'POST'))
def homepage():
    #Index page
    #If the user has logged in this will show the user dashboard.

    playersDataLabels, playersDataValues = topScorers()
    teamsDataLabels, teamsDataValues = mostWins()

    if session.get('email') != None:
        user = user_collection.find_one({ 'email' : session.get('email')})
        if user['accountType'] == 'Player':
            if user['profileCreated'] is False:
                return render_template('homepageUserProfileFalse.html', playersDataValues = playersDataValues, playersDataLabels = playersDataLabels, teamsDataLabels = teamsDataLabels, teamsDataValues = teamsDataValues, user = user)
            rank = playerRank(user['name'].upper())
            statsLabels, statsValues = myStats(user['name'].upper())
            player = player_collection.find_one({'full_name' : user['name'].upper()})
            object = player['Current Club']
            if teams_collection.count_documents({'team_name' : object}) == 0:
                flash('You are not seeing any personalised recommendations as your manager has not added the club to the system. Ask him to insert the team statistics to be able to see your recommendations! ')
                return render_template('homepageLoggedIn.html', type = 'Team', showResults = 'No', showStats = 'Yes', player = player, playersDataValues = playersDataValues, playersDataLabels = playersDataLabels, teamsDataLabels = teamsDataLabels, teamsDataValues = teamsDataValues, rank = rank, statsLabels = statsLabels, statsValues = statsValues, user = user)               
            results = recomend(object, 'Team')
            recomendations = []
            for team in results:
                recomendations.append(teams_collection.find_one({'team_name' : team}))
            return render_template('homepageLoggedIn.html', recomendations = recomendations, collection = 'main.teamPersonalProfile', type = 'Team', showResults = 'Yes', showStats = 'Yes', player = player, playersDataValues = playersDataValues, playersDataLabels = playersDataLabels, teamsDataLabels = teamsDataLabels, teamsDataValues = teamsDataValues, rank = rank, statsLabels = statsLabels, statsValues = statsValues, user = user)
        if user['accountType'] == 'Manager':
            if user['profileCreated'] is False:
                return render_template('homepageUserProfileFalse.html', playersDataValues = playersDataValues, playersDataLabels = playersDataLabels, teamsDataLabels = teamsDataLabels, teamsDataValues = teamsDataValues, user = user)
            team = teams_collection.find_one({"team_name" : user['teamManaged']})
            rank = teamsRank(user['teamManaged'])
            statsLabels, statsValues = myTeamStats(user['teamManaged'].upper())
            teamTopGoalScorersList = teamTopScorers(user['teamManaged'].upper())
            teamTopGoalScorers = []
            for i in teamTopGoalScorersList:
                teamTopGoalScorers.append(player_collection.find_one({'full_name' : i}))
            nPlayers = player_collection.count_documents({'Current Club' : user['teamManaged']})
            players = player_collection.find({'Current Club' : user['teamManaged']})
            object = players[random.randint(0,nPlayers-1)].get('full_name')
            results = recomend(object, 'Player')
            recomendations = []
            for i in results:
                recomendations.append(player_collection.find_one({'full_name' : i}))
            goalDifference = team['goals_scored'] - team['goals_conceded']
            return render_template('homepageLoggedIn.html', recomendations = recomendations, collection = 'main.playerPersonalProfile',  showResults = 'Yes', showStats = 'Yes', type = 'Player', object = object, team = team, playersDataValues = playersDataValues, playersDataLabels = playersDataLabels, teamsDataLabels = teamsDataLabels, teamsDataValues = teamsDataValues, rank = rank, statsLabels = statsLabels, statsValues = statsValues, teamTopGoalScorers = teamTopGoalScorers, goalDifference = goalDifference, user = user)
    return render_template('homepage.html', playersDataValues = playersDataValues, playersDataLabels = playersDataLabels, teamsDataLabels = teamsDataLabels, teamsDataValues = teamsDataValues)

@main.route('/players/', methods=['GET', 'POST'])
def players():
    #Displays every PLAYER in the database and allows to filter through PLAYERS.
    searchPlayerForm = SearchPlayerBarForm()
    if searchPlayerForm.validate_on_submit():

        query = {}

        if searchPlayerForm.name.data != '':
            name = (searchPlayerForm.name.data).upper()
            query['full_name'] = name
        if searchPlayerForm.position.data is not None:
            position = (searchPlayerForm.position.data)
            query['position'] = position
        if searchPlayerForm.minMatchesPlayed.data is not None:
            minMatches = (searchPlayerForm.minMatchesPlayed.data)
            query['appearances_overall'] = { '$gte' : minMatches }
        if searchPlayerForm.minGoalsScored.data is not None:
            minGoals = (searchPlayerForm.minGoalsScored.data)
            query['goals_overall'] = { '$gte' : minGoals }
        if searchPlayerForm.assists.data is not None:
            minAssist = (searchPlayerForm.assists.data)
            query['assists_overall'] = { '$gte' : minAssist }
        if searchPlayerForm.cleanSheets.data is not None:
            minCleanSheets = (searchPlayerForm.cleanSheets.data)
            query['clean_sheets_overall'] = { '$gte' : minCleanSheets }
        results = list(player_collection.find(query))
        if len(results) == 0:
            flash('No results matching your criteria!')
            return redirect(url_for('main.players'))
        return render_template('players.html', players = results, form = searchPlayerForm)
        
    players = list(player_collection.find())
    return render_template('players.html', players = players, form = searchPlayerForm)

@main.route('/teams/', methods=['GET', 'POST'])
def teams():
    #Displays every TEAM in the database and allows to filter through TEAMS.

    searchTeamForm = SearchTeamBarForm()
    if searchTeamForm.validate_on_submit():

        query = {}

        if searchTeamForm.name.data != '':
            name = (searchTeamForm.name.data).upper()
            query['team_name'] = name
        if searchTeamForm.minGoalsScored.data is not None:
            minGoalsScored = (searchTeamForm.minGoalsScored.data)
            query['goals_scored'] = minGoalsScored
        if searchTeamForm.minWins.data is not None:
            minWins = (searchTeamForm.minWins.data)
            query['wins'] = { '$gte' : minWins }
        if searchTeamForm.maxLosses.data is not None:
            maxLosses = (searchTeamForm.maxLosses.data)
            query['losses'] = { '$lte' : maxLosses }
        if searchTeamForm.maxGoalsConceded.data is not None:
            maxGoalsConceded = (searchTeamForm.maxGoalsConceded.data)
            query['goals_conceded'] = { '$lte' : maxGoalsConceded }
        
        results = list(teams_collection.find(query))
        if len(results) == 0:
            flash('No results matching your criteria!')
            return redirect(url_for('main.teams'))
        return render_template('teams.html', teams = results, form = searchTeamForm)
    
    teams = list(teams_collection.find())
    return render_template('teams.html', teams = teams, form = searchTeamForm)

@main.route('/players/<name>',  methods=['GET', 'POST'])
def playerPersonalProfile(name):
    #Displays the full statistic profile of a particular player.
    #Variable 'name' rapresents the name of the player of which profile to return.
    
    if player_collection.count_documents({ 'full_name' : name }) == 0:
        flash('Sorry no player has been found!')
        return redirect(url_for('main.players'))
    player = player_collection.find_one({ 'full_name' : name.upper() })
    return render_template('playerPersonalProfile.html', player = player)

@main.route('/teams/<name>',  methods=['GET', 'POST']) 
def teamPersonalProfile(name):
    #Displays the full statistic profile of a particular team.
    #Variable 'name' rapresents the name of the team of which profile to return.

    if teams_collection.count_documents({ 'team_name' : name }) == 0:
        flash('Sorry no team has been found!')
        return redirect(url_for('main.teams'))
    team = teams_collection.find_one({ 'team_name' : name.upper() })
    return render_template('teamPersonalProfile.html', team = team)

@main.route('/engine/', methods=['GET', 'POST'])
def engine():
    #Uses the recommend function in the engine.py file to recommend players or teams.

    searchForm = SearchBarForm()
    if searchForm.validate_on_submit():
        object = (searchForm.search.data).upper()
        if player_collection.count_documents({ 'full_name' : object }) == 1:
            results = recomend(object.upper(), 'Player')
            recomendations = []
            for player in results:
                recomendations.append(player_collection.find_one({'full_name' : player}))
            collection = 'main.playerPersonalProfile'
            type = 'Player'
        elif teams_collection.count_documents({'team_name' : object}) == 1:
            results = recomend(object.upper(), 'Team')
            recomendations = []
            for team in results:
                recomendations.append(teams_collection.find_one({'team_name' : team}))
            collection = 'main.teamPersonalProfile'
            type = 'Team'
        else: 
            flash('No team or player with that name have been found')
            return redirect(url_for('main.engine'))
        return render_template('engine.html', recomendations = recomendations, collection = collection, searchForm = searchForm, type = type)
    return render_template('engine.html', searchForm = searchForm)    
    
@main.route('/manageAccount/', methods=['GET', 'POST']) 
def manageAccount():
    #Allows the user to change their name, email and password.

    if session.get('email') == None:
        flash('Please login first!')
        return redirect(url_for('auth.login'))
    
    form = ManageAccountForm()

    if form.validate_on_submit():
        user = user_collection.find_one({ 'email' : session.get('email')})
        if user_collection.count_documents({ 'email' : form.email.data }) != 0:
            flash('An account with this email already exists: ' + form.email.data)
            return redirect(url_for('main.manageAccount')) 
        if form.name.data != '' :
            newName = { '$set': { 'name': form.name.data } }
            user_collection.update_one(user, newName)
            if session.get('accountType') == 'Player':
                player = player_collection.find_one({ 'full_name' : user['name'].upper()})
                newPlayerName = { '$set': { 'full_name': form.name.data.upper() } }
                player_collection.update_one(player, newPlayerName)
            user = user_collection.find_one({ 'email' : session.get('email')})
            flash('Name updated to: ' + form.name.data)
        if form.email.data != '' and user_collection.count_documents({ 'email' : form.email.data }) == 0:
            newEmail = { '$set': { 'email': form.email.data } }
            user_collection.update_one(user, newEmail)
            session['email'] = form.email.data
            user = user_collection.find_one({ 'email' : session.get('email')})
            flash('Email updated to: ' + form.email.data)
        if form.password.data != '':
            print(form.password.data, generate_password_hash(form.password.data))
            newPassword = { '$set': { 'password': generate_password_hash(form.password.data) } }
            user_collection.update_one(user, newPassword)
            user = user_collection.find_one({ 'email' : session.get('email')})
            flash('Password changed.')
    return render_template('manageAccount.html', form = form)

@main.route('/manageProfile/', methods = ['GET', 'POST'])
def manageProfile():
    #Allows user to change profile statistics of their player or team profile 

    if session.get('email') == None:
        flash('Please login first!')
        return redirect(url_for('auth.login'))

    user = user_collection.find_one({ 'email' : session.get('email') })

    if session.get('accountType') == 'Player':
        if user['profileCreated'] == False:
            playerForm = PlayerProfile()
            if playerForm.validate_on_submit():
                newPlayer = { 
                    'full_name' : user['name'].upper(), 
                    'birthday_GMT' : user['birthday'], 
                    'position' : playerForm.position.data, 
                    'Current Club' : playerForm.currentClub.data, 
                    'minutes_played_overall' : playerForm.minutesPlayedOverall.data, 
                    'minutes_played_home' : playerForm.minutesPlayedHome.data, 
                    'minutes_played_away' : playerForm.minutesPlayedAway.data, 
                    'nationality' : playerForm.nationality.data, 
                    'appearances_overall' : playerForm.apperancesOverall.data, 
                    'appearances_home' : playerForm.apperancesHome.data, 
                    'appearances_away' : playerForm.apperancesAway.data, 
                    'goals_overall' : playerForm.overallGoals.data, 
                    'goals_home' : playerForm.goalsHome.data, 
                    'goals_away' : playerForm.goalsAway.data, 
                    'assists_overall' : playerForm.overallAssist.data, 
                    'assists_home' : playerForm.assistHome.data, 
                    'assists_away' : playerForm.assistAway.data, 
                    'penalty_goals' : playerForm.penaltyScored.data, 
                    'penalty_misses' : playerForm.penaltyMiss.data, 
                    'clean_sheets_overall' : playerForm.cleanSheets.data, 
                    'yellow_cards_overall' : playerForm.yellowCards.data, 
                    'red_cards_overall' : playerForm.redCards.data
                }
                player_collection.insert_one(newPlayer)
                profileCreated = { '$set': { 'profileCreated': True } }
                user_collection.update_one(user, profileCreated)
                flash('Your player profile has sucesfully been created!')
                return redirect(url_for('main.playerPersonalProfile', name = user['name'].upper()))
            flash('You have not created your player profile yet! Do it now!')
            return render_template('addPlayerEntry.html', form = playerForm) 
        if user['profileCreated'] == True:
                modifyPlayerForm = ModifyPlayerProfile()
                player = player_collection.find_one({ 'full_name' : (user['name'].upper()) })
                if modifyPlayerForm.validate_on_submit():
                    if modifyPlayerForm.currentClub.data != '':
                        playerUpdateClub = { '$set': { 'Current Club': modifyPlayerForm.currentClub.data } }
                        player_collection.update_one(player, playerUpdateClub)
                        player = player_collection.find_one({ 'full_name' : (user['name'].upper()) })
                    if modifyPlayerForm.minutesPlayedOverall.data is not None:
                        playerUpdatePlayed = { '$set': { 'minutes_played_overall': modifyPlayerForm.minutesPlayedOverall.data } }
                        player_collection.update_one(player, playerUpdatePlayed)
                        player = player_collection.find_one({ 'full_name' : user['name'].upper() })
                    if modifyPlayerForm.minutesPlayedHome.data is not None:
                        playerUpdatePlayedHome = { '$set': { 'minutes_played_home': modifyPlayerForm.minutesPlayedHome.data } }
                        player_collection.update_one(player, playerUpdatePlayedHome)
                        player = player_collection.find_one({ 'full_name' : (user['name'].upper()) })
                    if modifyPlayerForm.minutesPlayedAway.data is not None:
                        playerUpdatePlayedAway = { '$set': { 'minutes_played_away': modifyPlayerForm.minutesPlayedAway.data } }
                        player_collection.update_one(player, playerUpdatePlayedAway)
                        player = player_collection.find_one({ 'full_name' : (user['name'].upper()) })
                    if modifyPlayerForm.apperancesOverall.data is not None:
                        playerUpdateAppOverall = { '$set': { 'appearances_overall': modifyPlayerForm.apperancesOverall.data } }
                        player_collection.update_one(player, playerUpdateAppOverall)
                        player = player_collection.find_one({ 'full_name' : (user['name'].upper()) })
                    if modifyPlayerForm.apperancesHome.data is not None:
                        playerUpdateAppHome = { '$set': { 'appearances_home': modifyPlayerForm.apperancesHome.data } }
                        player_collection.update_one(player, playerUpdateAppHome)
                        player = player_collection.find_one({ 'full_name' : (user['name'].upper()) })
                    if modifyPlayerForm.apperancesAway.data is not None:
                        playerUpdateAppAway = { '$set': { 'appearances_away': modifyPlayerForm.apperancesAway.data } }
                        player_collection.update_one(player, playerUpdateAppAway)
                        player = player_collection.find_one({ 'full_name' : (user['name'].upper()) })
                    if modifyPlayerForm.overallGoals.data is not None:
                        playerUpdateGoals = { '$set': { 'goals_overall': modifyPlayerForm.overallGoals.data } }
                        player_collection.update_one(player, playerUpdateGoals)
                        player = player_collection.find_one({ 'full_name' : (user['name'].upper()) })
                    if modifyPlayerForm.goalsHome.data is not None:
                        playerUpdateGoalsHome = { '$set': { 'goals_home': modifyPlayerForm.goalsHome.data } }
                        player_collection.update_one(player, playerUpdateGoalsHome)
                        player = player_collection.find_one({ 'full_name' : (user['name'].upper()) })
                    if modifyPlayerForm.goalsAway.data is not None:
                        playerUpdateGoalsAway = { '$set': { 'goals_away': modifyPlayerForm.goalsAway.data } }
                        player_collection.update_one(player, playerUpdateGoalsAway)
                        player = player_collection.find_one({ 'full_name' : (user['name'].upper()) })
                    if modifyPlayerForm.overallAssist.data is not None:
                        playerUpdateAssist = { '$set': { 'assists_overall': modifyPlayerForm.overallAssist.data } }
                        player_collection.update_one(player, playerUpdateAssist)
                        player = player_collection.find_one({ 'full_name' : (user['name'].upper()) })
                    if modifyPlayerForm.assistHome.data is not None:
                        playerUpdateAssistHome = { '$set': { 'assists_home': modifyPlayerForm.assistHome.data } }
                        player_collection.update_one(player, playerUpdateAssistHome)
                        player = player_collection.find_one({ 'full_name' : (user['name'].upper()) })
                    if modifyPlayerForm.assistAway.data is not None:
                        playerUpdateAssistAway = { '$set': { 'assists_away': modifyPlayerForm.assistAway.data } }
                        player_collection.update_one(player, playerUpdateAssistAway)
                        player = player_collection.find_one({ 'full_name' : (user['name'].upper()) })
                    if modifyPlayerForm.penaltyScored.data is not None:
                        playerUpdatePenalty = { '$set': { 'penalty_goals': modifyPlayerForm.penaltyScored.data } }
                        player_collection.update_one(player, playerUpdatePenalty)
                        player = player_collection.find_one({ 'full_name' : (user['name'].upper()) })
                    if modifyPlayerForm.penaltyMiss.data is not None:
                        playerUpdatePenaltyMiss = { '$set': { 'penalty_misses': modifyPlayerForm.penaltyMiss.data } }
                        player_collection.update_one(player, playerUpdatePenaltyMiss)
                        player = player_collection.find_one({ 'full_name' : (user['name'].upper()) })
                    if modifyPlayerForm.cleanSheets.data is not None:
                        playerUpdateCS = { '$set': { 'clean_sheets_overall': modifyPlayerForm.cleanSheets.data } }
                        player_collection.update_one(player, playerUpdateCS)
                        player = player_collection.find_one({ 'full_name' : (user['name'].upper()) })
                    if modifyPlayerForm.yellowCards.data is not None:
                        playerUpdateYC = { '$set': { 'yellow_cards_overall': modifyPlayerForm.yellowCards.data } }
                        player_collection.update_one(player, playerUpdateYC)
                        player = player_collection.find_one({ 'full_name' : (user['name'].upper()) })
                    if modifyPlayerForm.redCards.data is not None:
                        playerUpdateRC = { '$set': { 'red_cards_overall': modifyPlayerForm.redCards.data } }
                        player_collection.update_one(player, playerUpdateRC)
                        player = player_collection.find_one({ 'full_name' : (user['name'].upper()) })
                    flash('Your profile is up to date!')
                    return redirect(url_for('main.playerPersonalProfile', name = user['name'].upper()))
                return render_template('managePlayerProfile.html', form = modifyPlayerForm)
    if session.get('accountType') == 'Manager':
        if user['profileCreated'] == False:
            newTeamForm = TeamProfile()
            if newTeamForm.validate_on_submit():
                newTeam = { 
                    'team_name' : user['teamManaged'], 
                    'matches_played' : newTeamForm.matches_played.data, 
                    'matches_played_home' : newTeamForm.matches_played_home.data, 
                    'matches_played_away' : newTeamForm.matches_played_away.data, 
                    'wins' : newTeamForm.wins.data, 
                    'wins_home' : newTeamForm.wins_home.data, 
                    'wins_away' : newTeamForm.wins_away.data, 
                    'draws' : newTeamForm.draws.data, 
                    'draws_home' : newTeamForm.draws_home.data, 
                    'draws_away' : newTeamForm.draws_away.data, 
                    'losses' : newTeamForm.losses.data, 
                    'losses_home' : newTeamForm.losses_home.data, 
                    'losses_away' : newTeamForm.losses_away.data, 
                    'goals_scored' : newTeamForm.goals_scored.data,
                    'goals_conceded' : newTeamForm.goals_conceeded.data, 
                    'goals_scored_home' : newTeamForm.goals_scored_home.data, 
                    'goals_scored_away' : newTeamForm.goals_scored_away.data, 
                    'goals_conceded_home' : newTeamForm.goals_conceeded_home.data, 
                    'goals_conceded_away' : newTeamForm.goals_conceeded_away.data, 
                    'clean_sheets' : newTeamForm.clean_sheets.data, 
                    'clean_sheets_home' : newTeamForm.clean_sheets_home.data, 
                    'clean_sheets_away' : newTeamForm.clean_sheets_away.data, 
                    'cards_total' : newTeamForm.cards_total.data, 
                    'cards_total_home' : newTeamForm.cards_total_home.data, 
                    'cards_total_away' : newTeamForm.cards_total_away.data, 
                    'average_possesion' : newTeamForm.average_possesion.data, 
                    'average_possesion_home' : newTeamForm.average_possesion_home.data, 
                    'average_possesion_away' : newTeamForm.average_possesion_away.data, 
                    'shots' : newTeamForm.shots.data,
                    'shots_on_target' : newTeamForm.shots_on_target.data, 
                    'shots_off_target' : newTeamForm.shots_off_target.data, 
                    'fouls' : newTeamForm.fouls.data 
                }
                teams_collection.insert_one(newTeam)
                profileCreated = { '$set': { 'profileCreated': True } }
                user_collection.update_one(user, profileCreated)
                flash('Your team profile has sucesfully been created!')
                return redirect(url_for('main.homepage'))
            flash('You have not created your team profile yet! Do it now!')
            return render_template('addTeamEntry.html', form = newTeamForm)
        if user['profileCreated'] == True:
            ModifyTeamForm = ModifyTeamProfile()
            team = teams_collection.find_one({'team_name' : user['teamManaged']})
            if ModifyTeamForm.validate_on_submit():
                if teams_collection.count_documents({ 'team_name' : (ModifyTeamForm.team.data.upper()) }) == 1:
                    flash('This team already exists! Please ask the manager to delete the team.')
                    return redirect(url_for('main.manageProfile', type = 'Manager'))
                if teams_collection.count_documents({ 'team_name' : (ModifyTeamForm.team.data.upper()) }) == 0 and ModifyTeamForm.team.data != '':
                    team = teams_collection.find_one({ 'team_name' : user['teamManaged'] })
                    teams_collection.delete_one(team)
                    profileDeleted = { '$set': { 'profileCreated': False, 'teamManaged' : (ModifyTeamForm.team.data.upper()) } }
                    user_collection.update_one(user, profileDeleted)
                    return redirect(url_for('main.manageProfile'))
                if (ModifyTeamForm.team.data.upper()) == user['teamManaged']:
                    flash('You already manage this team')
                    return redirect(url_for('main.manageProfile'))
                if ModifyTeamForm.team.data != '':
                    teamUpdateTeam = { '$set': { 'teamManaged': (ModifyTeamForm.team.data).upper() } }
                    user_collection.update_one(user, teamUpdateTeam)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.matches_played.data is not None:
                    teamUpdateMatchesPLayed = { '$set': { 'matches_played': ModifyTeamForm.matches_played.data } }
                    teams_collection.update_one(team, teamUpdateMatchesPLayed)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.matches_played_home.data is not None:
                    teamUpdateMatchesPLayedHome = { '$set': { 'matches_played_home': ModifyTeamForm.matches_played_home.data } }
                    teams_collection.update_one(team, teamUpdateMatchesPLayedHome)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.matches_played_away.data is not None:
                    teamUpdateMatchesPLayedAway = { '$set': { 'matches_played_away': ModifyTeamForm.matches_played_away.data } }
                    teams_collection.update_one(team, teamUpdateMatchesPLayedAway)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.wins.data is not None:
                    teamUpdateWins = { '$set': { 'wins': ModifyTeamForm.wins.data } }
                    teams_collection.update_one(team, teamUpdateWins)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.wins_home.data is not None:
                    teamUpdateWinsHome = { '$set': { 'wins_home': ModifyTeamForm.wins_home.data } }
                    teams_collection.update_one(team, teamUpdateWinsHome)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.wins_away.data is not None:
                    teamUpdateWinsAway = { '$set': { 'wins_away': ModifyTeamForm.wins_away.data } }
                    teams_collection.update_one(team, teamUpdateWinsAway)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.draws.data is not None:
                    teamUpdateDraws = { '$set': { 'draws': ModifyTeamForm.draws.data } }
                    teams_collection.update_one(team, teamUpdateDraws)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.draws_home.data is not None:
                    teamUpdateDrawsHome = { '$set': { 'draws_home': ModifyTeamForm.draws_home.data } }
                    teams_collection.update_one(team, teamUpdateDrawsHome)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.draws_away.data is not None:
                    teamUpdateDrawsAway = { '$set': { 'draws_away': ModifyTeamForm.draws_away.data } }
                    teams_collection.update_one(team, teamUpdateDrawsAway)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.losses.data is not None:
                    teamUpdateLosses = { '$set': { 'losses': ModifyTeamForm.losses.data } }
                    teams_collection.update_one(team, teamUpdateLosses)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.losses_home.data is not None:
                    teamUpdateLossesHome = { '$set': { 'losses_home': ModifyTeamForm.losses_home.data } }
                    teams_collection.update_one(team, teamUpdateLossesHome)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.losses_away.data is not None:
                    teamUpdateLossesAway = { '$set': { 'losses_away': ModifyTeamForm.losses_away.data } }
                    teams_collection.update_one(team, teamUpdateLossesAway)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.goals_scored.data is not None:
                    teamUpdateGoals = { '$set': { 'goals_scored': ModifyTeamForm.goals_scored.data } }
                    teams_collection.update_one(team, teamUpdateGoals)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.goals_scored_home.data is not None:
                    teamUpdateGoalsHome = { '$set': { 'goals_scored_home': ModifyTeamForm.goals_scored_home.data } }
                    teams_collection.update_one(team, teamUpdateGoalsHome)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.goals_scored_away.data is not None:
                    teamUpdateGoalsAway = { '$set': { 'goals_scored_away': ModifyTeamForm.goals_scored_away.data } }
                    teams_collection.update_one(team, teamUpdateGoalsAway)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.goals_conceeded.data is not None:
                    teamUpdateGoalsConceded = { '$set': { 'goals_conceeded': ModifyTeamForm.goals_conceeded.data } }
                    teams_collection.update_one(team, teamUpdateGoalsConceded)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.goals_conceeded_home.data is not None:
                    teamUpdateGoalsConcededHome = { '$set': { 'goals_conceeded_home': ModifyTeamForm.goals_conceeded_home.data } }
                    teams_collection.update_one(team, teamUpdateGoalsConcededHome)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.goals_conceeded_away.data is not None:
                    teamUpdateGoalsConcededAway = { '$set': { 'goals_conceeded_away': ModifyTeamForm.goals_conceeded_away.data } }
                    teams_collection.update_one(team, teamUpdateGoalsConcededAway)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.clean_sheets.data is not None:
                    teamUpdateCS = { '$set': { 'clean_sheets': ModifyTeamForm.clean_sheets.data } }
                    teams_collection.update_one(team, teamUpdateCS)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.clean_sheets_home.data is not None:
                    teamUpdateCSHome = { '$set': { 'clean_sheets_home': ModifyTeamForm.clean_sheets_home.data } }
                    teams_collection.update_one(team, teamUpdateCSHome)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.clean_sheets_away.data is not None:
                    teamUpdateCSAway = { '$set': { 'clean_sheets_away': ModifyTeamForm.clean_sheets_away.data } }
                    teams_collection.update_one(team, teamUpdateCSAway)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.cards_total.data is not None:
                    teamUpdateCT = { '$set': { 'cards_total': ModifyTeamForm.cards_total.data } }
                    teams_collection.update_one(team, teamUpdateCT)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.cards_total_home.data is not None:
                    teamUpdateCTHome = { '$set': { 'cards_total_home': ModifyTeamForm.cards_total_home.data } }
                    teams_collection.update_one(team, teamUpdateCTHome)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.cards_total_away.data is not None:
                    teamUpdateCTAway = { '$set': { 'cards_total_away': ModifyTeamForm.cards_total_away.data } }
                    teams_collection.update_one(team, teamUpdateCTAway)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.average_possesion.data is not None:
                    teamUpdateAveragePossesion = { '$set': { 'average_possesion': ModifyTeamForm.average_possesion.data } }
                    teams_collection.update_one(team, teamUpdateAveragePossesion)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.average_possesion_home.data is not None:
                    teamUpdateAveragePossesionHome = { '$set': { 'average_possesion_home': ModifyTeamForm.average_possesion_home.data } }
                    teams_collection.update_one(team, teamUpdateAveragePossesionHome)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.average_possesion_away.data is not None:
                    teamUpdateAveragePossesionAway = { '$set': { 'average_possesion_away': ModifyTeamForm.average_possesion_away.data } }
                    teams_collection.update_one(team, teamUpdateAveragePossesionAway)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.shots.data is not None:
                    teamUpdateShots = { '$set': { 'shots': ModifyTeamForm.shots.data } }
                    teams_collection.update_one(team, teamUpdateShots)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.shots_on_target.data is not None:
                    teamUpdateShotsTarget = { '$set': { 'shots_on_target': ModifyTeamForm.shots_on_target.data } }
                    teams_collection.update_one(team, teamUpdateShotsTarget)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.shots_off_target.data is not None:
                    teamUpdateShotsOffTarget = { '$set': { 'shots_off_target': ModifyTeamForm.shots_off_target.data } }
                    teams_collection.update_one(team, teamUpdateShotsOffTarget)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                if ModifyTeamForm.fouls.data is not None:
                    teamUpdateFouls = { '$set': { 'fouls': ModifyTeamForm.fouls.data } }
                    teams_collection.update_one(team, teamUpdateFouls)
                    team = teams_collection.find_one({'team_name' : user['teamManaged']})
                flash('Your teams profile has been updated!')
                return(redirect(url_for('main.homepage')))
            return render_template('manageTeamProfile.html', form = ModifyTeamForm)

@main.route('/deleteEntry/<type>/', methods =['GET', 'POST'])
def deleteEntry(type):
    #Deletes player or team profile

    if session.get('email') == None:
        flash('Please login first!')
        return redirect(url_for('auth.login'))
    
    user = user_collection.find_one({ 'email' : session.get('email') })

    if type == 'Player':
        player_collection.find_one_and_delete({ 'full_name' : user['name'].upper() })
        profileDeleted = { '$set': { 'profileCreated': False } }
        user_collection.update_one(user, profileDeleted)
        flash('Your player profile has been deleted!')
        return redirect(url_for('main.homepage'))
    if type == 'Team':
        teams_collection.find_one_and_delete({ 'team_name' : user['teamManaged'].upper() })
        profileDeleted = { '$set': { 'profileCreated': False } }
        user_collection.update_one(user, profileDeleted)
        flash('Your Team profile has been deleted!')
        return redirect(url_for('main.homepage'))

@main.route('/deleteAccount/', methods =['GET', 'POST'])
def deleteAccount():
    #Deletes user account and profile (if created). Logs out user.

    if session.get('email') == None:
        flash('Please login first!')
        return redirect(url_for('auth.login'))

    user = user_collection.find_one({ 'email' : session.get('email') })

    if user['profileCreated'] == False:
        user_collection.delete_one(user)
        session.pop('email', None)
        session.pop('accountType', None)
        flash('Account deleted!')
        return redirect(url_for('main.homepage'))
    if user['profileCreated'] == True:
        if user['accountType'] == 'Player':
            player_collection.find_one_and_delete({ 'full_name' : user['name'].upper() })
            user_collection.delete_one(user)
            session.pop('email', None)
            session.pop('accountType', None)
            flash('Your account and player profile have been!')
            return redirect(url_for('main.homepage'))
        if user['accountType'] == 'Manager':
            teams_collection.find_one_and_delete({ 'team_name' : user['teamManaged'] })
            user_collection.delete_one(user)
            session.pop('email', None)
            session.pop('accountType', None)
            flash('Your account and team profile have been!!')
            return redirect(url_for('main.homepage'))