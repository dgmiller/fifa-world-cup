import utils
import vis
import numpy as np
import pandas as pd

G = utils.get_goal_matrix()
vis.plot_goal_matrix(np.round(G))

EG_MOM = utils.EG_matrix()
vis.plot_goal_matrix(np.round(EG_MOM))

FIT4 = utils.run_stan_model('poisson4.stan', 'UEFA2020', m=1,n=3, num_samples=5000)
EG_poisson4 = FIT4['EG']
print("Gamma Distribution")
vis.plot_goal_matrix(np.round(EG_poisson4.mean(axis=0)))