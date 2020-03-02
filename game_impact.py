from nba_api.stats.endpoints import *
from nba_api.stats.static import *  
import pandas as pd
from statistics import mean
import clean_up_data
import regression_df
import get_data
import pandas as pd
import sklearn
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
import numpy as np
import seaborn as sns
import copy
from itertools import chain, combinations
import matplotlib.pyplot as plt
from matplotlib import style

""" 
Helper function to return the updated data frame of team data but only from games where a specific player played 
(i.e. and not out from injury, trade, etc.)
"""
def only_with_player(games, player):
    res = games.copy()
    row = 0   
    team = games['Game_ID']
    for game in team.values:
        if(game not in player.values):
            res = res.drop(row)
        row+=1
    return res

""" 
Helper function to return the updated data frame of player data but only from games with that specific team
(eg., when a player is traded midseason to this team)
"""
def only_with_team(games, team):
    res = games.copy()
    row = 0   
    player = games['Game_ID']
    for game in player.values:
        if(game not in team.values):
            res = res.drop(row)
        row+=1
    return res

""" 
Helper function to calculate the slope and intercept for the true and predicted data to plot a line
"""
def best_fit_slope_and_intercept(xs,ys):
    m = (((mean(xs)*mean(ys)) - mean(xs*ys)) /
         ((mean(xs)*mean(xs)) - mean(xs*xs)))
    
    b = mean(ys) - m*mean(xs)
    
    return m, b
"""
This function calculates how well we can predict the score of a game based on an individual player's stats
This indirectly quantifies a player's impact on the game
"""
def game_impact(player):
    print("*****", player[3], "******") # player name

    # Call the API endpoint passing in player's ID & which season 
    # '.player_game_log.get_data_frame()' converts gamelog object into a pandas dataframe, can also convert to JSON or dictionary  
    contributions = playergamelog.PlayerGameLog(player_id=player[12], season = '2018').player_game_log.get_data_frame()
    team = only_with_player(HOU_18.team_game_log.get_data_frame(), contributions[['Game_ID']])
    games_played = len(team.index)
    print("Games Played:", games_played)
    if(games_played<10):
        return 0
    contributions = only_with_team(contributions, team[['Game_ID']])

    # Get relevent columns and split up our data (still experimenting)
    # TODO: implement hustle stats and advanced stats
    x_cols = ['MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 
              'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'PLUS_MINUS']
   # all values: ['SEASON_ID', 'Player_ID', 'Game_ID', 'GAME_DATE', 'MATCHUP', 'WL', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'PLUS_MINUS', 'VIDEO_AVAILABLE']
   
    # 2/3 of the games for training, rest for testing
    x_train = contributions[0:(2*games_played//3)][x_cols]
    y_train = team[0:(2*games_played//3)]['PTS']

    x_test = contributions[(2*games_played//3):][x_cols]
    y_test = team[(2*games_played//3):]['PTS']

    LR = LinearRegression()
    LR.fit(x_train, y_train)

    # Predict our data
    LR_pred = LR.predict(x_test)

    # Plot expected vs actual
    m, b = best_fit_slope_and_intercept(y_test,LR_pred)
    regression_line = [(m*x)+b for x in y_test]
    style.use('ggplot')
    fig = plt.figure()
    fig.suptitle(player[3])
    plt.scatter(y_test,LR_pred,color='#003F72')
    plt.plot(y_test, regression_line)
    plt.xlabel("Actual Score")
    plt.ylabel("Predicted Score")
    return m



player_dict = players.get_players()

teams = teams.get_teams()
# EXAMPLE: HOUSTON, 2018
HOU = [x for x in teams if x['full_name'] == 'Houston Rockets'][0]
HOU_id = HOU['id']
HOU_18 = teamgamelog.TeamGameLog(team_id=HOU_id, season = '2018', season_type_all_star='Regular Season')

roster = commonteamroster.CommonTeamRoster(season = '2018', team_id=HOU_id).common_team_roster.get_data_frame()
ranking = {}
for player in roster.values:
    ranking[player[3]] = game_impact(player) # store the game_impact for each player

for key, value in sorted(ranking.items(), key=lambda item: item[1], reverse = True):
    print("%s: %s" % (key, value))

plt.show()