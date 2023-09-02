from flask_pymongo import MongoClient
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

client = MongoClient('localhost', 27017)
db = client.footballRecommender

def recomend(object, type):
    # This function take an entity's name (team or player) along with their type (Team or Player) adn returns five similar entities.

    if type == 'Team':
        teamsData = pd.DataFrame(list((db.teams).find()))
        teamsData.drop(labels=['_id'], inplace=True, axis=1)
        data = teamsData.copy()
        data = teamsData.select_dtypes(exclude='object')
        data.fillna(0, inplace=True)
        similarityMatrix = cosine_similarity(data,data)
        objectIndex = teamsData[teamsData['team_name'] == object].index.values
        similarToIndexDf = pd.DataFrame(similarityMatrix[objectIndex[0],:], columns = ['similar'])
        similarToIndexDf.sort_values(by='similar', ascending=False, inplace=True)
        result = []
        for i in similarToIndexDf.index[1:6]:
            result.append(teamsData.iloc[i, 0])
        return result
    if type == 'Player':
        playersData = pd.DataFrame(list((db.players).find()))
        playersData.drop(labels=['_id'], inplace=True, axis=1)
        data = playersData.copy()
        objectIndex = data[data['full_name'] == object].index.values
        position = db.players.find_one({'full_name' : object})['position']
        data.drop(data[data['position'] != position].index, inplace=True)
        data.reset_index(drop=True, inplace=True)
        objectIndex = data[data['full_name'] == object].index.values
        dataCopy = data.copy()
        data = data.select_dtypes(exclude='object')
        data.fillna(0, inplace=True)
        similarityMatrix = cosine_similarity(data,data)
        similarToIndexDf = pd.DataFrame(similarityMatrix[objectIndex[0],:], columns = ['similar'])
        similarToIndexDf.sort_values(by='similar', ascending=False, inplace=True)
        result = []
        for i in similarToIndexDf.index[1:6]:
            result.append(dataCopy.iloc[i, 0])  
        return result
    
def topScorers():
    #Returns the top 10 goal scorers in the database

    playersData = pd.DataFrame(list((db.players).find()))
    playersData.drop(labels=['_id'], inplace=True, axis=1)
    data = playersData.copy()
    data = data[['full_name', 'goals_overall']]
    data.sort_values(by='goals_overall', ascending=False, inplace=True)
    data = data.head(10)
    playersDataLabels = []
    playersDataValues = []
    for index, row in data.iterrows():
        playersDataLabels.append(row['full_name'])
        playersDataValues.append(row['goals_overall'])
    return playersDataLabels, playersDataValues

def mostWins():
    #Returns the top 10 teams with the most wins.

    teamsData = pd.DataFrame(list((db.teams).find()))
    teamsData.drop(labels=['_id'], inplace=True, axis=1)
    data = teamsData.copy()
    data = data[['team_name', 'wins']]
    data.sort_values(by='wins', ascending=False, inplace=True)
    data = data.head(10)
    data['team_name'] = data.team_name.str.rsplit(n=2, expand=True)[0]+' '+data.team_name.str.rsplit(n=3, expand=True)[1]
    teamsDataLabels = []
    teamsDataValues = []
    for index, row in data.iterrows():
        teamsDataLabels.append(row['team_name'])
        teamsDataValues.append(row['wins'])
    return teamsDataLabels, teamsDataValues

def teamsRank(team):
    #Returns where the team ranks in terms of wins

    teamsData = pd.DataFrame(list((db.teams).find()))
    teamsData.drop(labels=['_id'], inplace=True, axis=1)
    data = teamsData.copy()
    data = data[['team_name', 'wins']]
    data.sort_values(by='wins', ascending=False, inplace=True)
    data.reset_index(inplace=True)
    position = data.index[data['team_name'] == team]+1
    return position[0]

def playerRank(player):
    #Returns where the player ranks in terms of goals

    playersData = pd.DataFrame(list((db.players).find()))
    playersData.drop(labels=['_id'], inplace=True, axis=1)
    data = playersData.copy()
    data = data[['full_name', 'goals_overall']]
    data.sort_values(by='goals_overall', ascending=False, inplace=True)
    data.reset_index(inplace=True)
    position = data.index[data['full_name'] == player]+1
    return position[0]

def myStats(player):
    #Returns statistics about the player

    playersData = pd.DataFrame(list((db.players).find()))
    playersData.drop(labels=['_id'], inplace=True, axis=1)
    data = playersData.copy()
    data = data[data['full_name'] == player]
    data = data.select_dtypes(include=np.number)
    data = data[['appearances_overall', 'goals_overall', 'assists_overall', 'penalty_goals', 'penalty_misses', 'clean_sheets_overall', 'yellow_cards_overall', 'red_cards_overall']]
    data = data.rename(columns={'appearances_overall' : 'Total Apperances', 'goals_overall' : 'Total Goals', 'assists_overall' : 'Total Assist', 'penalty_goals' : 'Penalty Scored', 'penalty_misses' : 'Penalty Missed', 'clean_sheets_overall' : 'Clean Sheets', 'yellow_cards_overall' : 'Yellow Cards', 'red_cards_overall' : 'Red Cards'})
    statsLabels = data.columns.tolist()
    statsValues = data.values.tolist()[0]
    return statsLabels, statsValues

def myTeamStats(team):
    #Returns statistics about the team

    teamsData = pd.DataFrame(list((db.teams).find()))
    teamsData.drop(labels=['_id'], inplace=True, axis=1)
    data = teamsData.copy()
    data = data[data['team_name'] == team]
    data = data.select_dtypes(include=np.number)
    data = data[['matches_played', 'wins', 'draws', 'losses', 'goals_scored', 'clean_sheets', 'cards_total']]
    data = data.rename(columns={'matches_played' : 'Matches Played', 'wins' : 'Wins', 'draws' : 'Draws', 'losses' : 'Losses', 'goals_scored' : 'Goals Scored', 'clean_sheets' : 'Clean Sheets', 'cards_total' : 'Cards'})
    statsLabels = data.columns.tolist()
    statsValues = data.values.tolist()[0]
    return statsLabels, statsValues

def teamTopScorers(team):
    #Returns the top 10 goals scorers for a team

    playersData = pd.DataFrame(list((db.players).find()))
    playersData.drop(labels=['_id'], inplace=True, axis=1)
    data = playersData.copy()
    data = data[data['Current Club'] == team]
    data = data[['full_name', 'goals_overall']]
    data.sort_values(by='goals_overall', ascending=False, inplace=True)
    data = data.head(10)
    teamTopGoalScorers = []
    for index, row in data.iterrows():
        teamTopGoalScorers.append(row['full_name'])
    return teamTopGoalScorers