# Visualizations for World Cup data
import numpy as np
from utils import get_team_to_index
import matplotlib as mpl
import matplotlib.pyplot as plt
from TEAMS import team_dict

teams = team_dict['2019']['teams']


def truncate(i, j=8):
    if i > 6:
        return j
    else:
        return i


def plot_goal_matrix(G, score=False, colormap='Reds', fname=None, figsize=(9,9), **kwargs):
    tempG = G.flatten()
    tempG = np.array([i if ~np.isnan(i) else truncate(i) for i in tempG]).reshape(G.shape)
    tempG += np.diag([np.nan]*tempG.shape[0])
    G += np.diag([np.nan]*tempG.shape[0])
    
    fig,ax = plt.subplots(figsize=figsize)

    bad = mpl.cm.get_cmap(name=colormap)
    bad.set_bad("grey",alpha=.3)
    if score:
        plt.imshow(tempG-tempG.T, cmap=bad, **kwargs)
    else:

        plt.imshow(tempG, cmap=bad, **kwargs)

    plt.xticks(np.arange(len(teams)),teams,rotation='vertical',fontsize=8)
    plt.yticks(np.arange(len(teams)),teams,fontsize=8)

    if score:
        plt.ylabel("home",labelpad=15)
        plt.xlabel("away",labelpad=15)
    else:
        plt.ylabel("goals for",labelpad=15)
        plt.xlabel("goals against",labelpad=15)
    plt.tight_layout(pad=5.0,rect=(0,-.25,1,1))
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    for i in range(len(teams)):
        for j in range(len(teams)):
            if not G[i,j] >= 0:
                continue
            else:
                if score:
                    tt = "{0}-{1}".format(G[i,j].astype(int),G[j,i].astype(int))
                else:
                    tt = "{0}".format(G[i,j].astype(int))
                if G[i,j] > 6:
                    text = ax.text(j,i,tt,ha='center',va='center',color='white',alpha=.5)
                else:
                    text = ax.text(j,i,tt,ha='center',va='center',color='k',alpha=.5)

    if fname:
        plt.savefig(fname)
    plt.show()

    
def plot_goals(team1, team2, posterior, teamcor=['r', 'b']):
    tix = get_team_to_index(teams)
    
    fig,ax = plt.subplots(ncols=2, figsize=(16,4))
    #ax = plt.gca()
    for i in range(2):
        if i == 0:
            match = posterior[:, tix[team1]-1, tix[team2]-1]
            vals,counts = np.unique(match, return_counts=True)
        else:
            match = posterior[:, tix[team2]-1, tix[team1]-1]
            vals,counts = np.unique(match, return_counts=True)
        ax[i].bar(vals, counts, color=['k'] + [teamcor[i]]*(len(vals) - 1), alpha=.5)
        if i == 0:
            ax[i].set_title("Goals for {0} against {1}".format(team1, team2))
        else:
            ax[i].set_title("Goals for {0} against {1}".format(team2, team1))
        ax[i].spines['top'].set_visible(False)
        ax[i].spines['right'].set_visible(False)
        ax[i].set_frame_on(False)
        ax[i].set_xticks(vals)
    plt.show()

    
def plot_goaldiff(team1, team2, posterior, color1='r', color2='b'):
    tix = get_team_to_index(teams)
    match1 = posterior[:, tix[team1]-1, tix[team2]-1]
    match2 = posterior[:, tix[team2]-1, tix[team1]-1]
    vals,counts = np.unique(match2-match1, return_counts=True)
    
    ix0 = np.where(vals==0)[0][0]
    remnant = len(vals) - ix0
    barcors = [color1]*ix0 + ['k'] + [color2]*remnant
    plt.figure(figsize=(16,4))
    ax = plt.gca()
    ax.bar(vals, counts, color=barcors, alpha=.5)
    ax.set_title("Goal Differential\n\n{0} vs {1}".format(team1, team2))
    
    absvals = np.absolute(vals).astype(int)
    ax.set_xlim(-max(absvals), max(absvals))
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_frame_on(False)
    ax.set_xticks(vals)
    ax.set_xticklabels(absvals)
    plt.show()


### END ###
