# 3rd Party Modules
import pandas as pd

def main(games_dict, n = 10):
    """
    takes games dictionary and returns single data frame ready for regression
    
    games_dict: dictionary of games,
    n: running team stats size
    
    cols_to_add are columns which we add to default
    cols_to_remove are columns which we remove from default
    
    default columns*: ['pts','a_pts', 'poss', 'a_poss', 'ort', 'drt',
       'efg', 'a_efg', 'ast_pct', 'win', 't1_score', 't2_score', 'game_cover',
       'game_spread', 'game_OU', 't1_ML', 't2_ML']
    
    * NOTE: all these columns are AVERAGED over n games, except 't1_score', 't2_score', 'game_cover', 'ML', 'a_ML'
        
    """
    all_games = pd.DataFrame()
    for team in games_dict.keys():
        df = games_dict[team]
        # select columns to roll on
        columns_to_roll = ['fgm', 'fga',
        'fg3m', 'fg3a',  'ftm', 'fta', 'oreb',
       'dreb', 'reb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts',
        'a_fgm', 'a_fga',
       'a_fg3m', 'a_fg3a', 'a_ftm', 'a_fta',
        'a_oreb', 'a_dreb', 'a_reb', 'a_ast', 'a_stl', 'a_blk',
       'a_tov', 'a_pf', 'a_pts', 'cover', 'win', 'OU']        
        # first make new columns where we want to keep important data for a game instead of rolling on it
        new_unrolled_columns = ['t1_score', 't2_score', 'game_cover','game_spread', 'game_OU', 't1_ML', 't2_ML']
        corresp_columns = ['pts', 'a_pts', 'cover', 'spread', 'OU', 'ML', 'a_ML']
        df[new_unrolled_columns] = df[corresp_columns]
        # new win indicator column
        df['win'] = df['t1_score'] > df['t2_score']
        # roll data, drop first n games
        new_df = df[columns_to_roll].rolling(window=n).sum().shift()
        df[columns_to_roll] = new_df
        df = df.dropna()
        # update percentages & put in advanced stats
        df.loc[:,'fg3_pct'] = df['fg3m']/df['fg3a']
        df.loc[:,'a_fg3_pct'] = df['a_fg3m']/df['a_fg3a']
        df.loc[:,'fg_pct'] = df['fgm']/df['fga']
        df.loc[:,'a_fg_pct'] = df['a_fgm']/df['a_fga']
        df.loc[:,'ft_pct'] = df['ftm']/df['fta']
        df.loc[:,'a_ft_pct'] = df['a_ftm']/df['a_fta']
        df['poss'] = df['fga'] + 0.5*df['fta'] - df['oreb'] + df['tov']
        df['a_poss'] = df['a_fga'] + 0.5*df['a_fta'] - df['a_oreb'] + df['a_tov']
        df['ort'] = df['pts']/df['poss']
        df['drt'] = df['a_pts']/df['a_poss']
        df['efg'] = (df['fgm'] + 0.5*df['fg3m'])/df['fga']
        df['a_efg'] = (df['a_fgm'] + 0.5*df['fg3m'])/df['a_fga']
        df['ast_pct'] = df['ast']/df['fgm']
        #averaging certain columns
        columns_to_avg = ['poss', 'cover', 'spread', 'pts', 'a_pts', 'a_poss', 'win', 'OU', 'ML', 'a_ML']
        df[columns_to_avg] = df[columns_to_avg]/n
        # columns used for regression
        columns_for_regression = ['pts','a_pts', 'poss', 'a_poss', 'ort', 'drt', 'OU', 
       'efg', 'a_efg', 'ast_pct', 'win', 't1_score', 't2_score', 'game_spread', 'game_OU', 't1_ML', 't2_ML']
        # necessary columns for identifying game:
        identifiers = ['game_id', 'home']
        # add all games to master dataframe
        # NOTE: games will be double counted
        all_games = all_games.append(df[identifiers + columns_for_regression])
    return all_games

if __name__ == '__main__':
    main()