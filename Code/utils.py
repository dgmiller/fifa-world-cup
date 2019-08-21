import pandas as pd
import numpy as np
import pystan
import pickle
from TEAMS import team_dict


def get_teams(year):
    teams = team_dict[year]['teams']
    teamsGS = team_dict[year]['teamsGS']
    teams16 = team_dict[year]['teams16']
    teamsQF = team_dict[year]['teamsQF']
    teamsSF = team_dict[year]['teamsSF']
    teamsFF = team_dict[year]['teamsFF']
    return teams, teamsGS, teams16, teamsQF, teamsSF, teamsFF


def get_df(year, m=1,n=7, model=0):
    """
    Returns the dataframe with data for games in [m, n].

    INPUT
        m (int) first game to include, default=1
        n (int) last game to include, default=7
        model (int) determines how to compute the fail_to_save_rate, default=0

    RETURNS
        df (pandas.DataFrame) the dataset from worldcup[year].csv

    """
    df = pd.read_csv("../Data/worldcup{0}.csv".format(year))
    df['on_target_rate'] = df['on_target']/df['attempts']

    if model == 0:
        df['fail_to_save_rate'] = df['goals_against']/df['on_target_against']
    elif model == 1:
        df['fail_to_save_rate'] = 1-df['goals_against']/df['on_target_against']
    elif model == 2:
        df['fail_to_save_rate'] = (df['goals_against']/df['on_target_against']).mean()
        mu = df['fail_to_save_rate'].mean()
        df['fail_to_save_rate'] = .25*df['fail_to_save_rate'] + .75*mu
    elif model == 3:
        df['fail_to_save_rate'] = (df['goals_against']/df['on_target_against']).mean()
    else:
        raise ValueError("input not valid")

    df = df.loc[(df['game']>=m) & (df['game']<=n)]
    return df


def get_team_to_index(teams):
    """
    Returns a dictionary mapping a team name to its index.

    RETURNS
        team_to_index (dict) maps to an index that does not start at zero.
    """
    team_to_index = {}
    for team,i in zip(teams, np.arange(1,len(teams)+1)):
        team_to_index[team] = i
    return team_to_index
   

def get_goal_matrix(year, **kwargs):
    """
    Returns the matrix with actual goals scored between two teams.

    INPUT
        **kwargs passed to get_df()

    RETURNS
        G (numpy.array) 24x24 matrix of observed goals with nans elsewhere
    """
    teams = get_teams(year)[0]
    df = get_df(year, **kwargs)
    team_to_index = get_team_to_index(teams)

    G = -np.ones((len(teams),len(teams)))
    G[G==-1] = np.nan
    for k in range(df.shape[0]):
        i = team_to_index[df.iloc[k]['team']]
        j = team_to_index[df.iloc[k]['opponent']]
        G[i-1, j-1] = df.iloc[k]['goals_for']

    return G


def logistic(x):
    """
    The logistic function of a variable x.
     
    """
    return np.exp(x)/(np.exp(x)+1)


def predict_match_outcome(year, team1, team2, df=None, verbose=True):
    if df is None:
        df = get_df(year)


    avg_on_target_team1 = df[df['team']==team1]['on_target_rate'].mean()
    avg_attempts_per_match_team1 = df[df['team']==team1]['attempts'].sum()/df[df['team']==team1]['game'].max()
    
    avg_on_target_team2 = df[df['team']==team2]['on_target_rate'].mean()
    avg_attempts_per_match_team2 = df[df['team']==team2]['attempts'].sum()/df[df['team']==team2]['game'].max()

    avg_fail_to_save_rate_team1 = df[df['team']==team1]['fail_to_save_rate'].mean()
    avg_fail_to_save_rate_team2 = df[df['team']==team2]['fail_to_save_rate'].mean()

    E_goals_team1 = avg_attempts_per_match_team1 * avg_on_target_team1 * avg_fail_to_save_rate_team2
    E_goals_team2 = avg_attempts_per_match_team2 * avg_on_target_team2 * avg_fail_to_save_rate_team1

    Pwin_team1 = logistic(E_goals_team1 - E_goals_team2)
    Pwin_team2 = 1 - Pwin_team1

    if verbose:
        if E_goals_team1 == max(E_goals_team1, E_goals_team2):
            team1 += '*'
        else:
            team2 += '*'
        print("\n----\n")
        print(team1)
        print('\texpected goals:', np.round(E_goals_team1,2))
        print('\tprob of win   :', np.round(Pwin_team1,2))
        print("\tavg attempts  :", np.round(avg_attempts_per_match_team1,2))
        print("\tavg on target :", np.round(avg_on_target_team1,2))
        print("\tavg save rate :", np.round(1-avg_fail_to_save_rate_team1,2))
        print(team2)
        print('\texpected goals:', np.round(E_goals_team2,2))
        print('\tprob of win   :', np.round(Pwin_team2,2))
        print("\tavg attempts  :", np.round(avg_attempts_per_match_team2,2))
        print("\tavg on target :", np.round(avg_on_target_team2,2))
        print("\tavg save rate :", np.round(1-avg_fail_to_save_rate_team2,2))
    else:
        return E_goals_team1, E_goals_team2, Pwin_team1, Pwin_team2



def EG_matrix(year, m=1, n=3, EG=True):
    teams = get_teams(year)[0]
    D = np.zeros((len(teams),len(teams)))
    df = get_df(year, m=m, n=n)
    for i in range(len(teams)):
        for j in range(len(teams)):
            EG1,EG2,Pwin1,Pwin2 = predict_match_outcome(year, teams[i], teams[j], df=df, verbose=False)
            if EG:
                D[i,j] = EG1
                D[j,i] = EG2
            else:
                D[i,j] = Pwin1
                D[j,i] = Pwin2
    return D



def predict_matches(df, matches_list):
    for t in matches_list:
        team1,team2 = t
        predict_match_outcome(year, team1, team2, df=df)



def get_stan_data(year, **kwargs):

    teams,teamsGS,teams16,teamsQF,teamsSF,teamsFF = get_teams(year)

    df = get_df(year, **kwargs)
    matches = np.array(teamsGS + teams16 + teamsQF + teamsSF + teamsFF)
    team_to_index = get_team_to_index(teams)
    G = get_goal_matrix(year)
    I = list()
    J = list()

    N = matches.shape[0]
    T = len(teams)
    Y = np.zeros((T,T))
    for n in range(N):
        i = team_to_index[matches[n,0]]
        j = team_to_index[matches[n,1]]
        I.append(i)
        J.append(j)
        Y[i-1,j-1] = G[i-1,j-1]
        Y[j-1,i-1] = G[j-1,i-1]

    X = EG_matrix(year)

    X1 = np.zeros((2,T))
    X2 = np.zeros((2,T))
    X3 = np.zeros((2,T))

    for team in teams:
        teamdf = df[df['team']==team]
        i = team_to_index[team]

        X1[0,i-1] = teamdf['attempts'].mean()
        X1[1,i-1] = teamdf['attempts'].var()

        X2[0,i-1] = teamdf['on_target'].sum() + 1
        X2[1,i-1] = teamdf['off_target'].sum() + 1

        X3[0,i-1] = teamdf['goals_against'].sum() + 1
        X3[1,i-1] = teamdf['on_target_against'].sum() - X3[0,i-1] + 1


    stan_data = {'N':N,
                 'T':T,
                 'I':I,
                 'J':J,
                 'X':X,
                 'X1':X1,
                 'X2':X2,
                 'X3':X3,
                 'Y':Y.astype(np.int64)}
    return stan_data




def run_stan_model(model_name, year, m=1, n=7, **kwargs):
    data = get_stan_data(year, m=m, n=n)
    with open(model_name, 'r') as f:
        stan_model = f.read()
    try:
        sm = pickle.load(open('{0}.pkl'.format(model_name),'rb'))
    except:
        sm = pystan.StanModel(model_code=stan_model)
        with open('{0}.pkl'.format(model_name), 'wb') as f:
            pickle.dump(sm, f)
    FIT = sm.sampling(data, **kwargs)
    return FIT



### END ###
