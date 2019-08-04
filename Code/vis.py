# Visualizations for World Cup data
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

year = input("YEAR: ")
if year == '2019':
    from TEAMS19 import *
elif year == '2018':
    from TEAMS18 import *
else:
    print("NO DATA AVAILABLE FOR YEAR {0}".format(year))


def plot_goal_matrix(G, score=False, colormap='Reds', fname=None, **kwargs):
    mpl.rcParams['font.family'] = 'monospace'
    fig,ax = plt.subplots(figsize=(10,10))

    bad = mpl.cm.get_cmap(name=colormap)
    bad.set_bad("grey",alpha=.3)
    if score:
        plt.imshow(G-G.T, cmap=bad, **kwargs)
    else:
        plt.imshow(G, cmap=bad, **kwargs)

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
                if len(teams) > 24:
                    fsize = '6'
                else:
                    fsize = '8'
                text = ax.text(j,i,tt,ha='center',va='center',color='k',alpha=.5,size='6')

    if fname:
        plt.savefig(fname)
    plt.show()




### END ###
