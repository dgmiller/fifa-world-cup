import pandas as pd
import numpy as np
from scipy import stats
import matplotlib
import matplotlib.pyplot as plt

teams = ["FRANCE",
         "NORWAY",
         "NIGERIA",
         "KOREA",
         "GERMANY",
         "SPAIN",
         "CHINA",
         "SOUTH AFRICA",
         "ITALY",
         "AUSTRALIA",
         "BRAZIL",
         "JAMAICA",
         "ENGLAND",
         "JAPAN",
         "ARGENTINA",
         "SCOTLAND",
         "NETHERLANDS",
         "CANADA",
         "CAMEROON",
         "NEW ZEALAND",
         "USA",
         "SWEDEN",
         "CHILE",
         "THAILAND"]


def get_df():
    df = pd.read_csv("worldcup2019.csv")
    df['on_target_rate'] = df['on_target']/df['attempts']
    df['save_rate'] = 1 - df['goals_against']/df['on_target_against']
    return df


def data(game=7):
    df = get_df()
    df = df[df['game']<=game]
    team_to_index = {}
    for team,i in zip(teams, np.arange(1,25)):
        team_to_index[team] = i

    G = -np.ones((24,24))
    G[G==-1] = np.nan
    for k in range(df.shape[0]):
        i = team_to_index[df.iloc[k]['team']]
        j = team_to_index[df.iloc[k]['opponent']]
        G[i-1, j-1] = df.iloc[k]['goals_for']


    return G


def predict_match_outcome(team1, team2):
    df = get_df()

    avg_on_target_team1 = df[df['team']==team1]['on_target_rate'].mean()
    avg_attempts_per_match_team1 = df[df['team']==team1]['attempts'].sum()/df[df['team']==team1]['game'].max()
    
    avg_on_target_team2 = df[df['team']==team2]['on_target_rate'].mean()
    avg_attempts_per_match_team2 = df[df['team']==team2]['attempts'].sum()/df[df['team']==team2]['game'].max()

    avg_save_rate_team1 = df[df['team']==team1]['save_rate'].mean()
    avg_save_rate_team2 = df[df['team']==team2]['save_rate'].mean()

    E_goals_team1 = avg_attempts_per_match_team1 * avg_on_target_team1 * avg_save_rate_team2
    E_goals_team2 = avg_attempts_per_match_team2 * avg_on_target_team2 * avg_save_rate_team1

    print(team1, E_goals_team1, "\n", team2, E_goals_team2)


def plot_goals(n):
    matplotlib.rcParams['font.family'] = 'monospace'
    bad = matplotlib.cm.get_cmap(name='magma_r')
    bad.set_bad("grey",alpha=.3)
    plt.figure(figsize=(10,10))
    plt.imshow(np.log(data(game=n)+1),cmap=bad,alpha=.7)
    plt.xticks(np.arange(24),teams,rotation='vertical',fontsize=8)
    plt.yticks(np.arange(24),teams,fontsize=8)
    plt.xlabel("goals against")
    plt.ylabel("goals for")
    plt.grid(alpha=.15)
    #plt.colorbar(shrink=.5, orientation='horizontal')
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    plt.show()

#if __name__ == "__main__":
#    plot_goals(3)
#    plot_goals(4)


### END ###
