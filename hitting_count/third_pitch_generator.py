import argparse
from tokenize import String
import numpy as np
import pandas as pd
import seaborn as sns
sns.set_theme(style="darkgrid")
import matplotlib.pyplot as plt
from pybaseball import statcast
from pybaseball import schedule_and_record
from pybaseball import batting_stats_range
from pybaseball import statcast_pitcher
from pybaseball import playerid_lookup
from sklearn import tree

def get_player_id(last, name):
    player = playerid_lookup(last, name)
    return player.key_mlbam[0]

def get_df(start, end, player_id):
    df = statcast_pitcher(start, end, player_id)
    return df

def third_pitch_df(df):
    # select desired columns
    df = df[['pitch_type', 'game_date','events','balls','strikes','pitch_number','at_bat_number']]
    # make binary out columns
    df['out'] = (df['events'] == 'field_out') | (df['events'] ==
                'strikeout') | (df['events'] ==
                'force_out') | (df['events'] ==
                'grounded_into_double_play') | (df['events'] ==
                'sac_fly') | (df['events'] ==
                'fielders_choice_out') | (df['events'] ==
                'strikeout_double_play')

    conditions = [
        df['balls'].eq(2) & df['strikes'].eq(1),
        df['balls'].eq(1) & df['strikes'].eq(2)
    ]
    first_conditions = [
        df['balls'].eq(0) & df['strikes'].eq(1),
        df['balls'].eq(1) & df['strikes'].eq(0)
    ]
    choices = ["2-1","1-2"]
    first_choices = ["0-1","1-0"]
    # select at bat numbers based on count conditions
    df['third_pitch'] = np.select(conditions, choices)
    df['first_pitch'] = np.select(first_conditions, first_choices)
    # select at bats with just first & third pitches that are not empty
    ab_num_third = df[df['third_pitch'] != "0"][['game_date', 'at_bat_number','third_pitch']].drop_duplicates(subset=['game_date','at_bat_number'])
    ab_num_first = df[df['first_pitch'] != "0"][['game_date', 'at_bat_number','third_pitch','first_pitch']].drop_duplicates(subset=['game_date','at_bat_number'])
    # merge first & third pitch count dfs
    counts_df = ab_num_first.merge(ab_num_third, on=['game_date', 'at_bat_number'],how='left')
    counts_df = counts_df[['game_date','at_bat_number','third_pitch_y', 'first_pitch']]
    # merge original df with counts df
    df = df.drop_duplicates(subset=['game_date','at_bat_number']).merge(counts_df, on=['game_date','at_bat_number'], how='outer')
    df['events'] = df['events'].astype(str)
    df['out'] = df['out'].astype(str)
    df = df[['out','game_date','third_pitch_y','first_pitch_y','at_bat_number']]
    df = df.dropna(subset=['third_pitch_y','first_pitch_y'])
    return df

def augment_df(df):
    ab_num = third_pitch_df(df)
    return(ab_num)

def main(args):
    player_id = get_player_id(args.pitcher_last_name, args.pitcher_first_name)
    df = get_df(args.start_date, args.end_date, player_id)
    # filter df to get Buster posey's
    # df = df[df['batter']==457763]
    aug_df = augment_df(df)
    aug_df.to_csv("counts_" + args.pitcher_last_name + ".csv")
    # plot_pitch_outcomes(aug_df, args.pitcher_last_name)
    # print(aug_df.head())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pitcher Sequence Comparer for Pitchers")
    parser.add_argument( "-l", "--pitcher_last_name", help="Last name of pitcher", required=True)
    parser.add_argument( "-f", "--pitcher_first_name", help="First name of pitcher", required=True)
    parser.add_argument( "-s", "--start_date", help="Start date of pitcher career", required=True)
    parser.add_argument( "-e", "--end_date", help="End/Current date of pitcher career", required=True)
    args = parser.parse_args()
    main(args)