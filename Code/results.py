import utils
import vis

# Method of Moments estimator matrix
EG_mom_gs = utils.EG_matrix(m=1, n=3)
EG_mom_ff = utils.EG_matrix()

# Simple poisson model (poisson.stan)
# group stage
FIT_poisson_gs = utils.run_stan_model('poisson.stan', m=1, n=3)
# full data
FIT_poisson_ff = utils.run_stan_model('poisson.stan')

# Structural poisson model (poisson2.stan)
# with group stage data
FIT_poisson2_gs = utils.run_stan_model('poisson2.stan', m=1, n=3)
# full dataset
FIT_poisson2_ff = utils.run_stan_model('poisson2.stan')

# extract expected goal matrices
EG_poisson_gs = FIT_poisson_gs.extract(pars=['EG'])['EG']
EG_poisson_ff = FIT_poisson_ff.extract(pars=['EG'])['EG']
EG_poisson2_gs = FIT_poisson2_gs.extract(pars=['EG'])['EG']
EG_poisson2_ff = FIT_poisson2_ff.extract(pars=['EG'])['EG']


# make visualizations
vis.plot_goal_matrix(EG_mom_gs, score=True, colormap='bwr', fname='../Figures/{0}_mom_gs_score.png'.format(year))
vis.plot_goal_matrix(EG_mom_gs, score=True, colormap='bwr', fname='../Figures/{0}_mom_gs_score.png'.format(year))

vis.plot_goal_matrix(EG_poisson_gs, score=True, colormap='bwr', fname='../Figures/{0}_poisson_gs_score.png'.format(year))
vis.plot_goal_matrix(EG_poisson_ff, score=True, colormap='bwr', fname='../Figures/{0}_poisson_ff_score.png'.format(year))

vis.plot_goal_matrix(EG_poisson2_gs, score=True, colormap='bwr', fname='../Figures/{0}_poisson2_gs_score.png'.format(year))
vis.plot_goal_matrix(EG_poisson2_ff, score=True, colormap='bwr', fname='../Figures/{0}_poisson2_ff_score.png'.format(year))
