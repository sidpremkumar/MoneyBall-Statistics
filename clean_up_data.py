# 3rd Party Modules
import pandas as pd

def main():
    # Import our file
    raw_games = pd.read_csv('2016_nba/games16.csv')

    # Add Cover
    raw_games['cover'] = raw_games['pts'] - raw_games['a_pts'] - raw_games['spread']

    # Clean up our raw_games:
    # Drop the following columns
    to_drop = ['w', 'l', 'w_pct', 'is_home', 'min']

    def create_team_table(team):
        """
        Helper function to create a per-team table
        """
        # Table is either away or home team
        table = raw_games[(raw_games['team_id'] ==  team )| (raw_games['a_team_id'] == team)]
        table['home'] = (raw_games['team_id'] == team)

        # Sort by game number
        table = table.sort_values(by = 'num_game')

        # Drop the stats we don't want to use
        table.drop(to_drop, axis = 1, inplace = True)
        return table

    # Loop over all team_ids and create a entry per team
    ret = {}
    for team in raw_games['team_id'].unique():
        ret[team] = create_team_table(team)

    # Per Team, make sure their stats are first, and opponent is second
    away_stats = ['a_fgm', 'a_fga', 'a_fg_pct', 'a_fg3m', 'a_fg3a', 'a_fg3_pct', 'a_ftm', 'a_fta', 'a_ft_pct', 'a_oreb', 'a_dreb', 'a_reb', 'a_ast', 'a_stl', 'a_blk', 'a_tov', 'a_pf', 'a_pts', 'a_num_game', 'a_team_id']
    home_stats = ['fgm', 'fga', 'fg_pct', 'fg3m', 'fg3a', 'fg3_pct', 'ftm', 'fta', 'ft_pct', 'oreb', 'dreb', 'reb', 'ast', 'stl', 'blk', 'tov', 'pf', 'pts', 'team_id', 'num_game']
    for team, games in ret.items():
        for index, game in games.iterrows():
            dict = game.to_dict()
            # If !game['home'], then we have to swap away and home
            if not dict['home']:
                new_away = {}
                new_home = {}
                # Away is home, home is away
                for stat in away_stats:
                    new_home[stat] = dict[stat]
                for stat in home_stats:
                    new_away[stat] = dict[stat]
                # Update our data
                for stat in away_stats:
                    games.loc[index, stat] = new_away[stat.replace('a_', '')]
                    # dict[stat] =
                for stat in home_stats:
                    games.loc[index, stat] = new_home['a_' + stat]

if __name__ == '__main__':
    main()
