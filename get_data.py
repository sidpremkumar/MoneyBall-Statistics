# 3rd Party Modules
import pandas as pd

def get_price_line(data):
    """Helper function that takes pd dataframe and calculates price line 1 and 2"""
    # If price X is positive, we risk 100 to win X
    # If price X is negative, we risk X to win 100
    # We can standardize negative values by:
    # Amount we win = (100 * risk) / X = risk is 100 = (100 * 100) / X = 10,000 / X
    price1 = data.price1.values[0]
    price2 = data.price2.values[0]
    # Format them if they are negative
    if price1 < 0:
        price1 = abs(10000/price1)
    if price2 < 0:
        price2 = abs(10000/price2)
    return price1, price2

def get_data_for_year(year):
    # Load in our file
    nba_games_all = pd.read_csv('nba-historical-stats-and-betting-data/nba_games_all.csv')
    nba_betting_spread = pd.read_csv('nba-historical-stats-and-betting-data/nba_betting_spread.csv')
    nba_betting_totals = pd.read_csv('nba-historical-stats-and-betting-data/nba_betting_totals.csv')
    nba_betting_money_line = pd.read_csv('nba-historical-stats-and-betting-data/nba_betting_money_line.csv')
    relevent_columns = ['game_id', 'game_date', 'matchup', 'team_id',
                        'is_home', 'wl', 'w', 'l', 'w_pct', 'min', 'fgm',
                        'fga', 'fg_pct', 'fg3m', 'fg3a', 'fg3_pct', 'ftm',
                        'fta', 'ft_pct', 'oreb', 'dreb', 'reb', 'ast', 'stl',
                        'blk', 'tov', 'pf', 'pts', 'num_game', 'a_team_id', 'a_fgm', 'a_fga',
                        'a_fg_pct', 'a_fg3m', 'a_fg3a', 'a_fg3_pct', 'a_ftm', 'a_fta',
                        'a_ft_pct', 'a_oreb', 'a_dreb', 'a_reb', 'a_ast', 'a_stl',
                        'a_blk', 'a_tov', 'a_pf', 'a_pts', 'a_num_game', 'spread', 'OU',
                        'a_ML', 'ML', 'season_year']
    formatted_data = pd.DataFrame(columns = relevent_columns)
    # Loop over game_id
    lost_value = 0
    for game_id in nba_games_all.game_id.unique():
        try:
            games = nba_games_all.loc[nba_games_all['game_id'] == game_id]
            game1 = games.iloc[0]
            game2 = games.iloc[1]
            if game1.season_type != "Regular Season" or game2.season_type != "Regular Season":
                # Skip anything that is not a regular season
                continue
            if game1.season_year != year:
                # Skip any year that is not relevent
                continue
            # Else, find which game is home
            game1_num_game = game1.w + game1.l
            game2_num_game = game2.w + game2.l
            # Pull spread from spread data
            spread = nba_betting_spread.loc[nba_betting_spread['game_id'] == game_id].loc[nba_betting_spread['book_name'] == 'Bovada'].spread1.values[0]
            betting_total = nba_betting_totals.loc[nba_betting_totals['game_id'] == game_id].loc[nba_betting_totals['book_name'] == 'Bovada'].total1.values[0]
            price_line1, price_line2 =  get_price_line(nba_betting_money_line.loc[nba_betting_money_line['game_id'] == game_id].loc[nba_betting_money_line['book_name'] == 'Bovada'])
            if game1.is_home == 't':
                # Game 1 is the home team
                data = [[game1.game_id, game1.game_date, game1.matchup, game1.team_id, game1.is_home, game1.wl, game1.w,
                     game1.l, game1.w_pct, game1.loc['min'], game1.fgm, game1.fga, game1.fg_pct, game1.fg3m, game1.fg3a,
                    game1.fg3_pct, game1.ftm, game1.fta, game1.ft_pct, game1.oreb, game1.dreb, game1.reb, game1.ast, game1.stl, game2.blk, game2.tov, game2.pf,
                    game1.pts, game1_num_game, game1.a_team_id, game2.fgm, game2.fga, game2.fg_pct, game2.fg3m, game2.fg3a,
                    game2.fg3_pct, game2.ftm, game2.fta, game2.ft_pct, game2.oreb, game2.dreb, game2.reb , game2.ast, game2.stl, game1.blk, game1.tov, game1.pf,
                    game2.pts, game2_num_game, spread, betting_total, price_line1, price_line2, game1.season_year]]
            else:
                # Game 2 is the away team
                data = [[game2.game_id, game2.game_date, game2.matchup, game2.team_id, game2.is_home, game2.wl, game2.w,
                     game2.l, game2.w_pct, game2.loc['min'], game2.fgm, game2.fga, game2.fg_pct, game2.fg3m, game2.fg3a,
                    game2.fg3_pct, game2.ftm, game2.fta, game2.ft_pct, game2.oreb, game2.dreb, game2.reb, game2.ast, game2.stl, game2.blk, game2.tov, game2.pf,
                    game2.pts, game2_num_game, game2.a_team_id, game1.fgm, game1.fga, game1.fg_pct, game1.fg3m, game1.fg3a,
                    game1.fg3_pct, game1.ftm, game1.fta, game1.ft_pct, game1.oreb, game1.dreb, game1.reb , game1.ast, game1.stl, game1.blk, game1.tov, game1.pf,
                    game1.pts, game1_num_game, spread, betting_total, price_line1, price_line2, game1.season_year]]
            new_row = pd.DataFrame(data ,columns=relevent_columns)
            formatted_data = pd.concat([new_row, formatted_data], ignore_index=True)
        except Exception as e:
            lost_value += 1
    print(f"[INFO] Lost {lost_value} values.")
    return formatted_data

