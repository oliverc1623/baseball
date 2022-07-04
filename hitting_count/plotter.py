import argparse
import numpy as np
import pandas as pd
import seaborn as sns
sns.set_theme(style="darkgrid")
import matplotlib.pyplot as plt

palette = {
    '1-2': 'tab:blue',
    '2-1': 'tab:orange',
    '1-0': 'tab:orange',
    '0-1': 'tab:blue',
}

def plot_pitch_outcomes(df, fname):
    plt.figure(figsize = (8,6))
    ax_third = sns.histplot(data=df,x='out',hue='third_pitch_y',multiple='stack',palette=palette) 
    fig = ax_third.get_figure()
    fig.savefig(fname + "_third.png")

    plt.figure(figsize = (8,6))
    ax_first = sns.histplot(data=df,x='out',hue='first_pitch_y',multiple='stack',palette=palette) 
    fig_first = ax_first.get_figure()
    fig_first.savefig(fname + "_first.png")

def plot_heatmap(df, fname):
    df = df[['out', 'game_date', 'third_pitch_y', 'first_pitch_y', 'at_bat_number']]
    first = df[['out', 'third_pitch_y', 'first_pitch_y']]
    table = first.groupby(['out', 'third_pitch_y', 'first_pitch_y']).size()
    tdf = table.to_frame()
    tdf.reset_index(inplace=True)
    tdf.rename(columns = {0:'count'}, inplace = True)
    tdf = tdf.pivot(index='out',columns=['first_pitch_y','third_pitch_y'],values='count')
    ax = sns.heatmap(tdf, cmap="YlGnBu")
    ax.set(xlabel='First pitch - Third pitch',ylabel='Out', title='First and Third Pitch Outcome Frequencies')
    fig = ax.get_figure()
    fig.savefig(fname + "_heatmap.png")

def main(args):
    df = pd.read_csv(args.data)
    df['out'] = df['out'].astype(str)
    plot_heatmap(df, args.name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pitcher Sequence Plotter for Pitchers")
    parser.add_argument( "-d", "--data", help="Augmented pitch dataframe", required=True)
    parser.add_argument( "-n", "--name", help="File name", required=False, default="output")
    args = parser.parse_args()
    main(args)