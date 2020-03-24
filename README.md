
# Predicting Match Outcomes for the FIFA Women's World Cup 2019
*Derek Miller*


## Introduction

For this case study, I will be using data I collected during the FIFA Women's World Cup 2019 to predict the winner of actual and hypothetical matches between each team. In particular, the tournament structure for a FIFA World Cup lends itself nicely to Bayesian analysis. Here's how the tournament is structured for the 2019 Women's World Cup.

*Group Phase*

The first stage of the tournament is called the group phase. Each of 24 teams are assigned to a group with 3 other teams. Each team will compete in at least 3 matches, one for every other team in their group. The match duration is 90 minutes. The possible outcomes for a team are a win, a loss, or a draw. Points are awarded for each outcome: 3 points for a win, 1 point for a draw, 0 points for a loss. The top 16 teams with the most points after the group stage advance to the knockout phase of the tournament. 

*Knockout Phase*

Each round after that eliminates half of the teams from the tournament. The naming conventions for each round are the Round of 16, the quarter finals, the semi-finals, and the final. The second stage of the tournament is the knockout phase, where a team must win to advance. No draws are allowed in this stage. When two teams are tied at the end of 90 minutes, the match continues for two additional 15-minute periods. If the teams are still tied at the end of extra time, the match proceeds to penalty kicks to determine the winner.

<<<<<<< HEAD
*For a case study on Bayesian modeling, check out ```tutorial.ipynb```.*
=======
## Problem Setup

Now that we have reviewed the tournament structure, let's set up the problem. The heart of the problem is that we know that teams will be eliminated over the course of the tournament but we don't know which ones (except a few at the end of the group stage). So in some sense, we want to be able to compute counterfactuals, the what-if scenarios where every team were to play every other team in the tournament. To do this, let's create a matrix where each team is indexed from 1-24, ordered first by their group (A-F) then by their rank within their group. This list looks like the following:


```python
for i,team in enumerate(utils.teams):
    print(i+1,'\t',team)
```

    1 	 FRANCE
    2 	 NORWAY
    3 	 NIGERIA
    4 	 KOREA
    5 	 GERMANY
    6 	 SPAIN
    7 	 CHINA
    8 	 SOUTH AFRICA
    9 	 ITALY
    10 	 AUSTRALIA
    11 	 BRAZIL
    12 	 JAMAICA
    13 	 ENGLAND
    14 	 JAPAN
    15 	 ARGENTINA
    16 	 SCOTLAND
    17 	 NETHERLANDS
    18 	 CANADA
    19 	 CAMEROON
    20 	 NEW ZEALAND
    21 	 USA
    22 	 SWEDEN
    23 	 CHILE
    24 	 THAILAND


Now let's create a 24x24 matrix with entries corresponding to the number of goals team ```i``` scored against team ```j``` in the group stage. The color corresponds to the numeric value of the goals scored with grey corresponding to empty values in the matrix. The empty values are exactly the values we want to fill. This is a matrix completion problem; our goal is to fill in this matrix with some estimate of the number of goals we expect each team to score on average. That is, we want to compute ```E[g_{i,j}]``` where ```g``` is the number of goals scored by team ```i``` against team ```j```.


```python
G = utils.get_goal_matrix(m=1,n=3) # the group stage scores
G_all = utils.get_goal_matrix(m=1,n=7) # the group stage scores plus the knockout stage scores
vis.plot_goal_matrix(G)
vis.plot_goal_matrix(G_all)
```


![png](Figures/output_5_0.png)



![png](Figures/output_5_1.png)


Below is a sample of the dataset we will work with. The variables are the number of goals scored, number of attempts to score, how many attempts were on-target, and how many attempts were off-target. From those numbers, I also created two variables for convenience, the rate at which shots were on-target in a match and the rate at which the keeper failed to save a shot that was on-target.


```python
df = utils.get_df()
df.sample(10)
```




<div>
<style>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>group</th>
      <th>team</th>
      <th>game</th>
      <th>opponent</th>
      <th>attempts</th>
      <th>on_target</th>
      <th>off_target</th>
      <th>goals_for</th>
      <th>goals_against</th>
      <th>on_target_against</th>
      <th>on_target_rate</th>
      <th>fail_to_save_rate</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>60</th>
      <td>D</td>
      <td>JAPAN</td>
      <td>3</td>
      <td>ENGLAND</td>
      <td>16</td>
      <td>5</td>
      <td>10</td>
      <td>0</td>
      <td>2</td>
      <td>6</td>
      <td>0.312500</td>
      <td>0.333333</td>
    </tr>
    <tr>
      <th>33</th>
      <td>B</td>
      <td>CHINA</td>
      <td>2</td>
      <td>SOUTH AFRICA</td>
      <td>17</td>
      <td>3</td>
      <td>9</td>
      <td>1</td>
      <td>0</td>
      <td>1</td>
      <td>0.176471</td>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>24</th>
      <td>A</td>
      <td>NIGERIA</td>
      <td>2</td>
      <td>KOREA</td>
      <td>12</td>
      <td>2</td>
      <td>7</td>
      <td>2</td>
      <td>0</td>
      <td>7</td>
      <td>0.166667</td>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>23</th>
      <td>F</td>
      <td>THAILAND</td>
      <td>1</td>
      <td>USA</td>
      <td>2</td>
      <td>2</td>
      <td>0</td>
      <td>0</td>
      <td>13</td>
      <td>21</td>
      <td>1.000000</td>
      <td>0.619048</td>
    </tr>
    <tr>
      <th>9</th>
      <td>C</td>
      <td>ITALY</td>
      <td>1</td>
      <td>AUSTRALIA</td>
      <td>5</td>
      <td>3</td>
      <td>1</td>
      <td>2</td>
      <td>1</td>
      <td>7</td>
      <td>0.600000</td>
      <td>0.142857</td>
    </tr>
    <tr>
      <th>10</th>
      <td>C</td>
      <td>BRAZIL</td>
      <td>1</td>
      <td>JAMAICA</td>
      <td>18</td>
      <td>6</td>
      <td>8</td>
      <td>3</td>
      <td>0</td>
      <td>3</td>
      <td>0.333333</td>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>35</th>
      <td>D</td>
      <td>SCOTLAND</td>
      <td>2</td>
      <td>JAPAN</td>
      <td>12</td>
      <td>4</td>
      <td>6</td>
      <td>1</td>
      <td>2</td>
      <td>6</td>
      <td>0.333333</td>
      <td>0.333333</td>
    </tr>
    <tr>
      <th>25</th>
      <td>A</td>
      <td>KOREA</td>
      <td>2</td>
      <td>NIGERIA</td>
      <td>15</td>
      <td>7</td>
      <td>3</td>
      <td>0</td>
      <td>2</td>
      <td>2</td>
      <td>0.466667</td>
      <td>1.000000</td>
    </tr>
    <tr>
      <th>81</th>
      <td>W</td>
      <td>USA</td>
      <td>4</td>
      <td>SPAIN</td>
      <td>12</td>
      <td>3</td>
      <td>8</td>
      <td>2</td>
      <td>1</td>
      <td>1</td>
      <td>0.250000</td>
      <td>1.000000</td>
    </tr>
    <tr>
      <th>34</th>
      <td>D</td>
      <td>JAPAN</td>
      <td>2</td>
      <td>SCOTLAND</td>
      <td>18</td>
      <td>6</td>
      <td>8</td>
      <td>2</td>
      <td>1</td>
      <td>4</td>
      <td>0.333333</td>
      <td>0.250000</td>
    </tr>
  </tbody>
</table>
</div>



## The MOM Estimator

Expected goals boils down to Arguably, the simplest way to estimate ```E[g_{i,j}]``` is to use the Method-of-Moments (MOM) estimator. The way to do this is ```E[g_{i,j}] = E[attempts * on\_target\_rate * fail\_to\_save\_rate]```. For simplicity, let's assume that ```attempts_i```, ```on\_target\_rate_i```, and ```fail\_to\_save\_rate_j``` are independent. This is a strong assumption but (spoiler alert!) this is not going to be our final model anyway. Assuming independence, we can separate out the expectation operator for each of the variables.

```E[g_{i,j}] = E[attempts_i] * E[on\_target\_rate_i] * E[fail\_to\_save\_rate_j]```.

The MOM tells us we can just substitute each of these expectations with the empirically observed averages from the data. I built a function to do just that called `EG_matrix()`. The matrix is printed below.


```python
EG_MOM = utils.EG_matrix()
print("\nTrue Expected Goals\n\n",EG_MOM)
```

    
    True Expected Goals
    
     [[1.85121283 1.27687016 2.28679231 4.35579488 0.34846359 2.25049402
      0.78404308 1.59712479 0.64299829 2.12345001 1.43741231 3.31870086
      0.74670769 1.28495949 0.99561026 2.46828377 1.09931966 2.03270428
      3.04905642 1.65935043 1.26318052 1.12006154 1.07857778 2.15715556]
     [1.22627287 0.84581913 1.51480766 2.88534792 0.23082783 1.49076309
      0.51936263 1.05796091 0.42593231 1.40660711 0.95216481 2.19836032
      0.49463107 0.85117764 0.6595081  1.63503049 0.72820686 1.3464957
      2.01974355 1.09918016 0.8367509  0.74194661 0.7144671  1.42893421]
     [0.27546296 0.19       0.34027778 0.64814815 0.05185185 0.33487654
      0.11666667 0.23765432 0.09567901 0.31597222 0.21388889 0.49382716
      0.11111111 0.1912037  0.14814815 0.36728395 0.16358025 0.30246914
      0.4537037  0.24691358 0.18796296 0.16666667 0.16049383 0.32098765]
     [1.68751006 1.16395652 2.08457126 3.97061192 0.31764895 2.05148282
      0.71471014 1.45589104 0.58613795 1.93567331 1.31030193 3.02522813
      0.68067633 1.17133052 0.90756844 2.25001342 1.00210682 1.85295223
      2.77942834 1.51261406 1.15147746 1.02101449 0.98319914 1.96639828]
     [2.44156104 1.6840616  3.01604599 5.7448495  0.45958796 2.96817224
      1.03407291 2.10644482 0.84804921 2.80061413 1.89580033 4.37702819
      0.98483134 1.6947306  1.31310846 3.25541472 1.44989059 2.68092977
      4.02139465 2.18851409 1.66600635 1.47724701 1.42253416 2.84506832]
     [1.82838542 1.261125   2.25859375 4.30208333 0.34416667 2.22274306
      0.774375   1.57743056 0.63506944 2.09726562 1.4196875  3.27777778
      0.7375     1.26911458 0.98333333 2.43784722 1.08576389 2.00763889
      3.01145833 1.63888889 1.24760417 1.10625    1.06527778 2.13055556]
     [0.62890625 0.43378676 0.77688419 1.47977941 0.11838235 0.7645527
      0.26636029 0.54258578 0.21844363 0.72139246 0.48832721 1.12745098
      0.25367647 0.43653493 0.33823529 0.83854167 0.37346814 0.69056373
      1.03584559 0.56372549 0.42913603 0.38051471 0.36642157 0.73284314]
     [0.53068783 0.36604082 0.65555556 1.24867725 0.09989418 0.64514991
      0.2247619  0.45784832 0.18432855 0.60873016 0.41206349 0.95137314
      0.21405896 0.36835979 0.28541194 0.70758377 0.31514235 0.58271605
      0.87407407 0.47568657 0.3621164  0.32108844 0.30919627 0.61839254]
     [1.50331944 1.03691143 1.85704167 3.53722222 0.28297778 1.82756481
      0.6367     1.29698148 0.52216138 1.72439583 1.16728333 2.69502646
      0.60638095 1.04348056 0.80850794 2.00442593 0.89272751 1.6507037
      2.47605556 1.34751323 1.02579444 0.90957143 0.8758836  1.7517672 ]
     [2.22773326 1.53657434 2.75190579 5.24172532 0.41933803 2.70822475
      0.94351056 1.92196595 0.7737785  2.55534109 1.72976936 3.99369548
      0.89858148 1.54630897 1.19810865 2.97031102 1.32291163 2.44613848
      3.66920773 1.99684774 1.52010034 1.34787223 1.29795103 2.59590206]
     [1.79296875 1.23669643 2.21484375 4.21875    0.3375     2.1796875
      0.759375   1.546875   0.62276786 2.05664062 1.3921875  3.21428571
      0.72321429 1.24453125 0.96428571 2.390625   1.06473214 1.96875
      2.953125   1.60714286 1.2234375  1.08482143 1.04464286 2.08928571]
     [0.94939782 0.65484515 1.17278555 2.23387723 0.17871018 1.1541699
      0.4020979  0.81908832 0.32976283 1.08901515 0.73717949 1.7020017
      0.38295038 0.65899378 0.51060051 1.26586377 0.56378806 1.04247604
      1.56371406 0.85100085 0.6478244  0.57442557 0.55315055 1.10630111]
     [1.93705245 1.33607786 2.3928295  4.55777048 0.36462164 2.35484808
      0.82039869 1.67118251 0.67281374 2.22191311 1.50406426 3.47258703
      0.78133208 1.34454229 1.04177611 2.5827366  1.15029445 2.12695956
      3.19043933 1.73629351 1.32175344 1.17199812 1.12859078 2.25718157]
     [1.61865234 1.11646205 1.99951172 3.80859375 0.3046875  1.96777344
      0.68554688 1.39648437 0.56222098 1.85668945 1.25683594 2.90178571
      0.65290179 1.12353516 0.87053571 2.15820312 0.96121652 1.77734375
      2.66601562 1.45089286 1.10449219 0.97935268 0.94308036 1.88616071]
     [0.94444444 0.65142857 1.16666667 2.22222222 0.17777778 1.14814815
      0.4        0.81481481 0.32804233 1.08333333 0.73333333 1.69312169
      0.38095238 0.65555556 0.50793651 1.25925926 0.56084656 1.03703704
      1.55555556 0.84656085 0.64444444 0.57142857 0.55026455 1.1005291 ]
     [1.78395062 1.23047619 2.2037037  4.19753086 0.33580247 2.16872428
      0.75555556 1.53909465 0.61963551 2.0462963  1.38518519 3.19811875
      0.71957672 1.2382716  0.95943563 2.37860082 1.05937684 1.95884774
      2.9382716  1.59905938 1.21728395 1.07936508 1.03938859 2.07877719]
     [1.43454659 0.98947549 1.77208696 3.37540373 0.2700323  1.7439586
      0.60757267 1.23764804 0.49827388 1.64550932 1.11388323 2.57173618
      0.57864064 0.9957441  0.77152085 1.91272878 0.85188761 1.57518841
      2.36278261 1.28586809 0.97886708 0.86796096 0.83581426 1.67162852]
     [1.17636324 0.81139407 1.45315459 2.76791351 0.22143308 1.43008865
      0.49822443 1.01490162 0.40859676 1.34935784 0.91341146 2.10888648
      0.47449946 0.81653449 0.63266595 1.56848432 0.69856865 1.29169297
      1.93753946 1.05444324 0.80269492 0.71174919 0.68538811 1.37077621]
     [0.96731771 0.66720536 1.19492187 2.27604167 0.18208333 1.17595486
      0.4096875  0.83454861 0.3359871  1.10957031 0.75109375 1.73412698
      0.39017857 0.67143229 0.5202381  1.28975694 0.57442956 1.06215278
      1.59322917 0.86706349 0.66005208 0.58526786 0.56359127 1.12718254]
     [0.55748457 0.38452381 0.68865741 1.3117284  0.10493827 0.67772634
      0.23611111 0.48096708 0.1936361  0.63946759 0.43287037 0.99941211
      0.22486772 0.38695988 0.29982363 0.74331276 0.33105526 0.61213992
      0.91820988 0.49970606 0.38040123 0.33730159 0.32480894 0.64961787]
     [2.94453384 2.03098603 3.63736533 6.92831492 0.55426519 3.57962937
      1.24709668 2.54038214 1.02275125 3.37755352 2.28634392 5.27871613
      1.18771113 2.0438529  1.58361484 3.92604512 1.74857472 3.23321363
      4.84982044 2.63935806 2.00921133 1.78156669 1.71558274 3.43116548]
     [2.25123445 1.55278423 2.78093668 5.29702224 0.42376178 2.73679483
      0.953464   1.94224149 0.78194138 2.58229834 1.74801734 4.03582647
      0.90806096 1.56262156 1.21074794 3.00164594 1.33686752 2.47194371
      3.70791557 2.01791324 1.53613645 1.36209143 1.3116436  2.62328721]
     [0.57806513 0.39871921 0.71408046 1.36015326 0.10881226 0.70274585
      0.24482759 0.49872286 0.20078453 0.66307471 0.44885057 1.03630724
      0.23316913 0.40124521 0.31089217 0.77075351 0.34327677 0.63473819
      0.95210728 0.51815362 0.39444444 0.34975369 0.33679985 0.67359971]
     [0.98904321 0.68219048 1.22175926 2.32716049 0.18617284 1.20236626
      0.41888889 0.85329218 0.34353322 1.13449074 0.76796296 1.77307466
      0.3989418  0.68651235 0.5319224  1.31872428 0.58733098 1.08600823
      1.62901235 0.88653733 0.67487654 0.5984127  0.57624927 1.15249853]]


It's much easier to comprehend this matrix through visualization.  The color in the visualization corresponds to the MOM estimate while the numerical value of the visualization is the MOM estimate rounded to the nearest whole number.


```python
vis.plot_goal_matrix(EG_MOM)
```


![png](Figures/output_11_0.png)


Compare these predictions to the actual observed scores from the tournament. Remember, the model has access to (only) the group stage data.


```python
vis.plot_goal_matrix(G_all)
```


![png](Figures/output_13_0.png)


## The Bayesian Approach

The MOM estimator is a simple way to estimate the quality of a team and predict the outcome of a match. With not very much data, we shouldn't place a lot of confidence in the MOM estimator. Scenarios with small amounts of data but some good prior knowledge calls for a more Bayesian approach.

A simple Bayesian model of soccer matches models scored goals as a Poisson distribution, ```g_{i,j} \sim Poisson(\theta_{i,j})```. The parameter ```\theta_{i,j}``` is a rate parameter which in this example can be interpreted as the average number of goals scored in 90 minutes for team ```i``` against team ```j```. Note that ```\theta_{i,j}``` does not have to be an integer---it can take on any real value greater than zero. We don't really know what ```\theta_{i,j}``` is for each team, so maybe we should put a hyperprior on that. How should we choose the hyperparameters? Why not use the MOM estimator for the hyperparameters? What we get is ```\theta \sim Normal(\mu, \sigma)``` where ```\mu``` is the MOM estimated mean and ```\sigma``` is the MOM estimated variance. The full model in Stan is written as follows.


```python
with open('poisson.stan','r') as f:
    print(f.read())
```

    data {
      int<lower=1> N; // number of matches
      int<lower=1> T; // number of teams
      int<lower=1, upper=T> I[N]; // home team for match n
      int<lower=1, upper=T> J[N]; // away team for match n
      matrix<lower=0>[T, T] X; // expected goals for prior
      int<lower=0> Y[T, T]; // goals from matches
    }
    
    parameters {
      matrix<lower=0, upper=13>[T, T] theta;
    }
    
    model {
      to_vector(theta) ~ normal(to_vector(X),sd(to_vector(X)));
      for (n in 1:N) {
        Y[I[n], J[n]] ~ poisson(theta[I[n], J[n]]);
        Y[J[n], I[n]] ~ poisson(theta[J[n], I[n]]);
      }
    }
    
    generated quantities {
      matrix[T, T] EG; // expected goals prediction
      for (i in 1:T) {
        for (j in 1:T) {
          EG[i,j] = poisson_rng(theta[i,j]);
          EG[j,i] = poisson_rng(theta[j,i]);
        }
      }
    }
    
    


To see how this performs, let's run the model.


```python
# run the model using only group stage data (matches 1-3)
FIT = utils.run_stan_model('poisson.stan',m=1,n=3)
```


```python
FIT
```

    WARNING:pystan:Truncated summary with the 'fit.__repr__' method. For the full summary use 'print(fit)'





    
    Warning: Shown data is truncated to 100 parameters
    For the full summary use 'print(fit)'
    
    Inference for Stan model: anon_model_aace7765c73ec40c6ee031186a1d1a5d.
    4 chains, each with iter=2000; warmup=1000; thin=1; 
    post-warmup draws per chain=1000, total post-warmup draws=4000.
    
                  mean se_mean     sd   2.5%    25%    50%    75%  97.5%  n_eff   Rhat
    theta[1,1]    1.95    0.02    0.9   0.31   1.29   1.92   2.56   3.79   3023    1.0
    theta[2,1]    1.36    0.01   0.68   0.27   0.84   1.28    1.8   2.83   4401    1.0
    theta[3,1]    0.58  7.9e-3   0.48   0.02    0.2   0.46   0.83   1.81   3735    1.0
    theta[4,1]    1.13    0.01   0.73   0.06   0.55   1.02   1.61   2.78   4335    1.0
    theta[5,1]    2.47    0.01   0.98   0.63    1.8   2.44   3.13   4.44   4280    1.0
    theta[6,1]    1.92    0.01   0.92    0.3   1.25    1.9   2.54   3.83   3959    1.0
    theta[7,1]    1.07    0.01   0.71   0.06   0.52   0.95   1.54   2.65   4385    1.0
    theta[8,1]    1.03    0.01    0.7   0.05   0.49   0.92   1.47   2.65   4029    1.0
    theta[9,1]    1.62    0.02    0.9   0.14   0.93   1.53   2.24   3.53   2922    1.0
    theta[10,1]   2.25    0.02   0.97   0.39   1.57   2.25   2.92   4.14   3479    1.0
    theta[11,1]   1.66    0.01   0.76   0.35    1.1   1.62   2.17   3.28   4214    1.0
    theta[12,1]   1.26    0.01   0.79   0.09   0.63   1.18   1.79   2.99   3805    1.0
    theta[13,1]    2.0    0.02   0.94   0.28   1.33   1.99   2.62   3.96   3855    1.0
    theta[14,1]   1.75    0.02    0.9   0.19   1.06   1.71   2.36   3.62   3420    1.0
    theta[15,1]   1.24    0.01   0.79   0.09   0.62   1.16   1.74   2.98   3918    1.0
    theta[16,1]   1.86    0.02   0.92   0.23   1.18   1.82   2.48   3.79   2812    1.0
    theta[17,1]   1.59    0.02   0.88   0.15   0.93   1.54   2.18   3.42   3257    1.0
    theta[18,1]   1.42    0.01   0.82   0.11   0.79   1.34   1.97    3.2   3861    1.0
    theta[19,1]   1.28    0.01   0.78    0.1   0.66    1.2    1.8   2.98   4243    1.0
    theta[20,1]   1.03    0.01   0.73   0.03   0.45    0.9   1.48    2.7   3069    1.0
    theta[21,1]   2.77    0.01   0.86   1.17   2.17   2.75   3.34   4.51   4927    1.0
    theta[22,1]   2.28    0.02   0.97   0.46   1.58   2.26   2.94   4.23   3513    1.0
    theta[23,1]   1.02    0.01   0.72   0.04   0.45   0.89   1.45   2.69   3920    1.0
    theta[24,1]   1.29    0.01    0.8   0.08   0.66   1.19   1.81   3.06   3726    1.0
    theta[1,2]    1.72  9.9e-3   0.71   0.48   1.22   1.67   2.17   3.25   5049    1.0
    theta[2,2]    1.21    0.01   0.77   0.07   0.59   1.12   1.68   2.92   4029    1.0
    theta[3,2]    0.56  6.4e-3   0.48   0.02   0.19   0.43    0.8   1.79   5774    1.0
    theta[4,2]    1.32  9.4e-3   0.66   0.26   0.83   1.25   1.75   2.76   4990    1.0
    theta[5,2]    1.79    0.02    0.9   0.23   1.13   1.74   2.43   3.64   2764    1.0
    theta[6,2]    1.47    0.01   0.84   0.14   0.83   1.39   2.02   3.26   5268    1.0
    theta[7,2]    0.97    0.01   0.68   0.05   0.43   0.84   1.38   2.61   4397    1.0
    theta[8,2]    0.96    0.01   0.68   0.04   0.44   0.86   1.36   2.56   4006    1.0
    theta[9,2]    1.33    0.01    0.8   0.09    0.7   1.25   1.84    3.1   4401    1.0
    theta[10,2]   1.51 10.0e-3   0.72   0.34   0.96   1.44   1.98   3.13   5289    1.0
    theta[11,2]   1.45    0.01   0.84    0.1    0.8   1.37   1.99   3.24   3460    1.0
    theta[12,2]   1.08    0.01   0.73   0.05   0.51   0.97   1.54   2.74   4792    1.0
    theta[13,2]   2.02    0.01   0.71   0.76   1.51   1.98   2.49    3.5   4316    1.0
    theta[14,2]   1.35    0.01   0.79   0.08   0.75   1.26   1.85   3.07   3677    1.0
    theta[15,2]   1.09    0.01   0.75   0.04    0.5   0.98   1.54    2.8   3687    1.0
    theta[16,2]   1.47    0.01   0.85   0.11   0.81    1.4   2.04   3.28   3952    1.0
    theta[17,2]   1.29    0.01   0.79   0.08   0.67    1.2   1.83   3.01   3690    1.0
    theta[18,2]   1.18    0.01   0.76   0.07   0.58   1.06   1.66    2.9   4871    1.0
    theta[19,2]   1.09    0.01   0.72   0.07   0.52   0.98   1.55   2.74   3538    1.0
    theta[20,2]   0.96  9.4e-3   0.68   0.05   0.42   0.84    1.4   2.51   5200    1.0
    theta[21,2]   2.05    0.02   0.98   0.24   1.34   2.01   2.71   4.06   3456    1.0
    theta[22,2]   1.67    0.01   0.91   0.17    1.0   1.63   2.27   3.61   3860    1.0
    theta[23,2]   0.97  9.1e-3    0.7   0.05   0.41   0.83   1.41   2.59   5988    1.0
    theta[24,2]    1.1    0.01   0.74   0.06   0.51    1.0   1.58   2.74   4302    1.0
    theta[1,3]    1.96    0.01   0.83   0.53   1.34    1.9   2.52   3.69   4939    1.0
    theta[2,3]    2.15    0.01   0.74   0.84   1.61   2.11   2.62   3.74   5118    1.0
    theta[3,3]    0.94    0.01   0.66   0.04   0.42   0.83   1.34   2.46   4023    1.0
    theta[4,3]    1.34    0.01   0.79   0.09   0.72   1.26   1.85   3.02   4190    1.0
    theta[5,3]    3.07    0.01   0.85   1.51   2.44   3.06   3.64    4.8   4425    1.0
    theta[6,3]    2.29    0.01   0.94   0.54    1.6   2.27   2.94   4.14   4056    1.0
    theta[7,3]    1.15    0.01   0.74   0.07   0.57   1.06   1.64   2.79   4390    1.0
    theta[8,3]    1.09    0.01   0.72   0.06   0.51   0.98   1.57   2.73   4489    1.0
    theta[9,3]    1.94    0.01   0.92   0.34   1.25   1.89   2.57   3.82   3786    1.0
    theta[10,3]   2.76    0.02   0.98   0.86    2.1   2.75   3.42   4.74   3390    1.0
    theta[11,3]   2.25    0.02   0.94   0.48   1.56   2.24    2.9   4.08   3346    1.0
    theta[12,3]   1.39    0.01   0.82   0.12   0.76   1.31   1.94   3.16   3245    1.0
    theta[13,3]   2.43    0.02   0.96   0.63   1.76   2.42   3.09   4.38   4065    1.0
    theta[14,3]   2.05    0.02   0.93   0.33   1.38   2.01   2.69   3.94   3536    1.0
    theta[15,3]    1.4    0.01   0.79   0.12   0.79   1.33   1.92   3.08   3677    1.0
    theta[16,3]   2.23    0.02    1.0   0.34   1.53   2.22   2.91    4.3   3559    1.0
    theta[17,3]   1.88    0.01   0.88   0.27   1.26   1.85   2.46    3.7   3845    1.0
    theta[18,3]   1.64    0.01   0.85   0.19    1.0   1.59   2.22   3.39   4112    1.0
    theta[19,3]   1.41    0.01   0.84    0.1   0.75   1.33   1.96   3.25   3650    1.0
    theta[20,3]   1.11    0.01   0.74   0.06   0.52    1.0    1.6   2.77   4072    1.0
    theta[21,3]   3.62    0.01   0.99   1.68   2.92   3.64    4.3   5.57   4642    1.0
    theta[22,3]    2.8    0.01   0.97    0.9   2.15   2.82   3.47   4.72   4198    1.0
    theta[23,3]   1.11    0.01   0.71   0.05   0.54   1.03   1.57   2.66   4182    1.0
    theta[24,3]   1.44    0.01   0.83   0.08   0.81   1.35    2.0   3.21   3449    1.0
    theta[1,4]    4.33    0.01   0.91   2.58    3.7   4.32   4.97    6.1   4875    1.0
    theta[2,4]    2.72    0.01   0.86   1.16   2.12   2.67   3.31   4.49   3653    1.0
    theta[3,4]    1.45  9.1e-3   0.62   0.43   0.97   1.39   1.86   2.76   4677    1.0
    theta[4,4]    3.98    0.01    1.0   2.01   3.31   3.98   4.63   5.99   6116    1.0
    theta[5,4]    5.76    0.01   1.03   3.78   5.05   5.73   6.47   7.76   4854    1.0
    theta[6,4]    4.31    0.01   1.01    2.3   3.65   4.32    5.0   6.24   4787    1.0
    theta[7,4]    1.66    0.01   0.85   0.21   1.03   1.61   2.22   3.43   4292    1.0
    theta[8,4]    1.42    0.02   0.85   0.07   0.76   1.34    2.0   3.25   2299    1.0
    theta[9,4]    3.58    0.02   0.98   1.65   2.92   3.59   4.23   5.51   4074    1.0
    theta[10,4]   5.25    0.01   0.97   3.37   4.57   5.24   5.92   7.14   4494    1.0
    theta[11,4]    4.2    0.01   1.01   2.18   3.52    4.2    4.9   6.16   4862    1.0
    theta[12,4]   2.27    0.02   0.94   0.47   1.61   2.27   2.91   4.09   2451    1.0
    theta[13,4]   4.56    0.01   1.02    2.6   3.83   4.56   5.26   6.59   5412    1.0
    theta[14,4]   3.81    0.02   0.98   1.89   3.14   3.81   4.46   5.71   4188    1.0
    theta[15,4]   2.25    0.02   0.99   0.38   1.57   2.24    2.9   4.25   3667    1.0
    theta[16,4]   4.19    0.01   1.01   2.26   3.51   4.17   4.89   6.17   6009    1.0
    theta[17,4]   3.38    0.01    1.0   1.44    2.7   3.39   4.04   5.39   4757    1.0
    theta[18,4]   2.76    0.01   0.96   0.89    2.1   2.76   3.41    4.7   4193    1.0
    theta[19,4]   2.28    0.02   0.98    0.4    1.6   2.26   2.95   4.28   2960    1.0
    theta[20,4]   1.51    0.01   0.86   0.11   0.85   1.42   2.09   3.34   3385    1.0
    theta[21,4]    6.9    0.01   1.02   4.87    6.2   6.92    7.6   8.88   5321    1.0
    theta[22,4]   5.28    0.01   0.97   3.33   4.62   5.28   5.91   7.23   5167    1.0
    theta[23,4]   1.51    0.01   0.84   0.13   0.87   1.44   2.05   3.32   3769    1.0
    theta[24,4]   2.37    0.02   0.95   0.56    1.7   2.37    3.0   4.22   3971    1.0
    theta[1,5]    0.96  9.2e-3   0.66   0.06   0.43   0.85   1.35   2.51   5201    1.0
    theta[2,5]    0.89    0.01   0.66   0.04   0.37   0.75   1.28   2.49   4212    1.0
    theta[3,5]    0.54  6.1e-3   0.45   0.02   0.18   0.43   0.76   1.74   5524    1.0
    lp__        -293.2    0.64  20.64 -334.4 -306.5 -293.0 -279.1 -254.3   1046    1.0
    
    Samples were drawn using NUTS at Tue Jul 16 15:37:30 2019.
    For each parameter, n_eff is a crude measure of effective sample size,
    and Rhat is the potential scale reduction factor on split chains (at 
    convergence, Rhat=1).



Convergence and Rhat look good. Let's see how the predictions turned out.


```python
EG_poisson = FIT.extract(pars=['EG'])['EG']
vis.plot_goal_matrix(EG_poisson.mean(axis=0))
```


![png](Figures/output_20_0.png)


Again, compare with the actual observed scores.


```python
vis.plot_goal_matrix(G_all)
```


![png](Figures/output_22_0.png)


The predictions looks very similar to the MOM estimator matrix. That makes sense because we used the MOM estimator to inform the hyperprior for our Poisson model. However, it still looks like not much of an improvement. Can we do better? (We can.)

## A More Structural Poisson Model

One way we can improve this model is by deconstructing the ```\theta_{i,j}``` into it's various components. By adding structure to the model, we will improve estimation. Recall how we computed the MOM estimate:

```E[g_{i,j}] = E[attempts_i] * E[on\_target\_rate_i] * E[fail\_to\_save\_rate_j]```.

Let's improve our model by giving each of these independent variables its own hyperprior. For simplicity, we can assign a normal distribution to the number of attempts with the mean and variance computed from the empirical data as before. This is reasonable.

To model the on-target and failure-to-save rates, we can use the beta distribution. One way to interpret the two parameters of a beta distribution is as "pseudocounts" for the number of successes and failures respectively of a Bernoulli process.

```rate \sim Beta(\alpha, \beta)```

Thus, we can model the on-target and failure-to-save rates with a beta distribution. Using the on-target rate as an example, the hyperparameter ```\alpha``` is chosen to be equal to the number of shots on-target + 1. Likewise, the hyperparameter ```\beta``` is chosen to be equal to the number of shots off-target + 1. The addition of the ones has to do with the interpretation of the ```Beta(1,1)``` distribution, which is the same as a uniform distribution between 0 and 1. In other words, we know that shots can be on-target and they can be off-target. The failure-to-save rate hyperparameters are chosen similarly with a success being the number of goals scored against the opponent and a failure being the number of shots on-target minus the number of goals scored against the opponent.

Let's see how this model fares.


```python
with open('poisson2.stan','r') as f:
    print(f.read())
    
# use data from group stage only (matches 1-3)
FIT2 = utils.run_stan_model('poisson2.stan',m=1,n=3)
FIT2
```

    data {
      int<lower=1> N; // number of matches
      int<lower=1> T; // number of teams
      int<lower=1, upper=T> I[N]; // home team for match n
      int<lower=1, upper=T> J[N]; // away team for match n
      real<lower=0> X1[2,T]; // attempts mean and variance
      real<lower=0> X2[2,T]; // on/off target pseudocounts
      real<lower=0> X3[2,T]; // save/goal pseudocounts
      int<lower=0> Y[T, T]; // goals from matches
    }
    
    parameters {
      real<lower=0> attempts[T]; // attempts at goal
      real<lower=0, upper=1> sot_rate[T]; // shot on target rate
      real<lower=0, upper=1> fts_rate[T]; // fail to save rate
    }
    
    model {
      attempts ~ normal(X1[1], X1[2]);
      sot_rate ~ beta(X2[1], X2[2]);
      fts_rate ~ beta(X3[1], X3[2]);
      for (n in 1:N) {
        Y[I[n], J[n]] ~ poisson(attempts[I[n]]*sot_rate[I[n]]*fts_rate[J[n]]);
        Y[J[n], I[n]] ~ poisson(attempts[J[n]]*sot_rate[J[n]]*fts_rate[I[n]]);
      }
    }
    
    generated quantities {
      matrix[T, T] EG; // expected goals prediction
      for (i in 1:T) {
        for (j in 1:T) {
          EG[i,j] = poisson_rng(attempts[i]*sot_rate[i]*fts_rate[j]);
          EG[j,i] = poisson_rng(attempts[j]*sot_rate[j]*fts_rate[i]);
        }
      }
    }
    
    


    WARNING:pystan:Truncated summary with the 'fit.__repr__' method. For the full summary use 'print(fit)'





    
    Warning: Shown data is truncated to 100 parameters
    For the full summary use 'print(fit)'
    
    Inference for Stan model: anon_model_5f7680b71b0bbd9eaceb12f7e4e2a56a.
    4 chains, each with iter=2000; warmup=1000; thin=1; 
    post-warmup draws per chain=1000, total post-warmup draws=4000.
    
                   mean se_mean     sd   2.5%    25%    50%    75%  97.5%  n_eff   Rhat
    attempts[1]   17.51    0.07   5.63   8.18  13.48  16.89  20.97  30.29   7057    1.0
    attempts[2]   10.43    0.04    3.6   4.36   7.83   10.1  12.58  18.44   7111    1.0
    attempts[3]    14.7    0.14   10.0    2.5   7.49   12.4  19.35   39.4   5388    1.0
    attempts[4]    5.43    0.06   4.28   0.63   2.46   4.34   7.27  16.34   5027    1.0
    attempts[5]   18.42    0.08   6.12   8.69   14.0  17.68  21.94  32.27   5913    1.0
    attempts[6]   15.24     0.1    7.6   4.43   9.71  13.92  19.31  33.59   6295    1.0
    attempts[7]   11.61    0.16   10.6   1.13   4.52   8.62  15.28  40.69   4236    1.0
    attempts[8]    5.74    0.03    2.1   1.85   4.23   5.66   7.13  10.07   5523    1.0
    attempts[9]   11.69    0.06   4.58   4.92   8.48  10.92  14.12  23.01   5189    1.0
    attempts[10]  13.86    0.06   5.06   6.06  10.15  13.13  16.85  25.61   6290    1.0
    attempts[11]  12.73    0.06   5.07    5.0   8.96  11.99  15.69  24.15   6483    1.0
    attempts[12]  11.82    0.01   0.97   9.95  11.16  11.83  12.47   13.7   9267    1.0
    attempts[13]  14.46    0.05   4.22   7.28  11.41  14.14  17.06  23.84   7184    1.0
    attempts[14]   11.7    0.09   6.74   2.69   6.76  10.39  15.01  28.93   6241    1.0
    attempts[15]  11.85     0.1   6.84    2.8   6.89  10.44  15.16  29.17   5144    1.0
    attempts[16]  12.75    0.05   3.95   5.77   9.89   12.5  15.29  21.05   7323    1.0
    attempts[17]  18.49     0.1   7.21   7.98  13.39  17.19  22.35  35.58   5163    1.0
    attempts[18]  14.09    0.09    7.5    4.0   8.73  12.55  17.86  32.48   6279    1.0
    attempts[19]   15.6    0.14   9.87   3.42   8.93  13.45   19.7  40.91   4706    1.0
    attempts[20]   6.53    0.06   4.66   0.79   3.13   5.41   8.73  18.96   5227    1.0
    attempts[21]  35.03    0.14    9.7  19.16  28.33  33.87  40.57  57.84   4796    1.0
    attempts[22]  20.64     0.1   7.41   9.34   15.3  19.45  24.79  37.97   5702    1.0
    attempts[23]  17.85    0.18  12.66   2.94   9.06  15.01  22.96  50.47   5096    1.0
    attempts[24]   5.09    0.04   2.84   0.89   2.92    4.7   6.84  11.77   6473    1.0
    sot_rate[1]     0.4  8.6e-4   0.07   0.27   0.35    0.4   0.45   0.55   7016    1.0
    sot_rate[2]     0.4  1.1e-3    0.1   0.23   0.33    0.4   0.47    0.6   7391    1.0
    sot_rate[3]    0.17  9.3e-4   0.08   0.05   0.11   0.16   0.22   0.36   7275    1.0
    sot_rate[4]     0.5  1.1e-3   0.09   0.33   0.44    0.5   0.56   0.68   7358    1.0
    sot_rate[5]    0.53  8.0e-4   0.07    0.4   0.49   0.53   0.58   0.67   7490    1.0
    sot_rate[6]    0.52  7.6e-4   0.08   0.37   0.47   0.52   0.58   0.67   9892    1.0
    sot_rate[7]    0.25  1.2e-3    0.1   0.09   0.18   0.24   0.32   0.49   6926    1.0
    sot_rate[8]    0.37  1.2e-3   0.12   0.16   0.28   0.36   0.44   0.61   9632    1.0
    sot_rate[9]    0.54  1.1e-3    0.1   0.36   0.47   0.54   0.61   0.74   7746    1.0
    sot_rate[10]   0.53  9.2e-4   0.08   0.38   0.48   0.53   0.59   0.68   7428    1.0
    sot_rate[11]   0.44  9.5e-4   0.09   0.28   0.38   0.44    0.5   0.61   8243    1.0
    sot_rate[12]   0.29  8.9e-4   0.08   0.15   0.24   0.29   0.35   0.47   8778    1.0
    sot_rate[13]    0.5  8.9e-4   0.08   0.35   0.45    0.5   0.56   0.66   7933    1.0
    sot_rate[14]   0.37  8.2e-4   0.08   0.22   0.31   0.36   0.42   0.53   9187    1.0
    sot_rate[15]   0.42  1.3e-3   0.11   0.21   0.34   0.42    0.5   0.65   7005    1.0
    sot_rate[16]   0.58  9.6e-4   0.09   0.41   0.52   0.58   0.64   0.75   8639    1.0
    sot_rate[17]   0.38  1.0e-3   0.09   0.22   0.32   0.38   0.44   0.56   7226    1.0
    sot_rate[18]   0.33  7.9e-4   0.08   0.19   0.28   0.33   0.39   0.49   9797    1.0
    sot_rate[19]   0.32  9.5e-4   0.08   0.18   0.26   0.32   0.38    0.5   7756    1.0
    sot_rate[20]   0.36  1.3e-3   0.11   0.16   0.28   0.35   0.43   0.59   7782    1.0
    sot_rate[21]    0.5  7.2e-4   0.06   0.38   0.46    0.5   0.54   0.62   7507    1.0
    sot_rate[22]   0.44  7.4e-4   0.07   0.31   0.39   0.44   0.48   0.57   7838    1.0
    sot_rate[23]   0.24  7.6e-4   0.07   0.12   0.19   0.23   0.28   0.38   8229    1.0
    sot_rate[24]   0.56  1.4e-3   0.12   0.32   0.48   0.57   0.65    0.8   8228    1.0
    fts_rate[1]     0.2  1.2e-3   0.09   0.06   0.13   0.18   0.24   0.42   6096    1.0
    fts_rate[2]    0.28  9.6e-4   0.08   0.14   0.22   0.28   0.33   0.46   7464    1.0
    fts_rate[3]    0.31  9.3e-4   0.09   0.17   0.25   0.31   0.37   0.49   8424    1.0
    fts_rate[4]    0.68  1.3e-3   0.12   0.44    0.6   0.68   0.77   0.89   8433    1.0
    fts_rate[5]    0.12  7.9e-4   0.07   0.02   0.06    0.1   0.15   0.29   7952    1.0
    fts_rate[6]    0.18  8.0e-4   0.07   0.07   0.13   0.17   0.22   0.35   7892    1.0
    fts_rate[7]    0.12  6.3e-4   0.06   0.04   0.08   0.12   0.16   0.25   7797    1.0
    fts_rate[8]    0.35  9.3e-4   0.08   0.21    0.3   0.35    0.4   0.51   6992    1.0
    fts_rate[9]    0.19  7.9e-4   0.07   0.07   0.14   0.18   0.23   0.36   8131    1.0
    fts_rate[10]   0.44  1.4e-3   0.12   0.23   0.36   0.44   0.52   0.69   7093    1.0
    fts_rate[11]   0.26 10.0e-4   0.09   0.12    0.2   0.25   0.31   0.46   7412    1.0
    fts_rate[12]   0.65  1.1e-3   0.09   0.46   0.59   0.66   0.72   0.83   7535    1.0
    fts_rate[13]   0.12  5.4e-4   0.05   0.04   0.08   0.11   0.14   0.23   7545    1.0
    fts_rate[14]   0.26  1.0e-3   0.09   0.12   0.19   0.25   0.31   0.46   7436    1.0
    fts_rate[15]   0.25  8.8e-4   0.08   0.12    0.2   0.25   0.31   0.43   8445    1.0
    fts_rate[16]   0.47  1.2e-3   0.11   0.27   0.39   0.47   0.54   0.68   7825    1.0
    fts_rate[17]   0.16  6.9e-4   0.06   0.07   0.11   0.15   0.19    0.3   7399    1.0
    fts_rate[18]   0.26  1.5e-3   0.12   0.09   0.17   0.24   0.33   0.55   6319    1.0
    fts_rate[19]   0.46  1.2e-3   0.11   0.26   0.38   0.45   0.54    0.7   9300    1.0
    fts_rate[20]   0.35  1.1e-3    0.1   0.17   0.28   0.34   0.41   0.55   8303    1.0
    fts_rate[21]   0.09  5.4e-4   0.04   0.02   0.05   0.08   0.11   0.19   6968    1.0
    fts_rate[22]   0.18  7.0e-4   0.06   0.08   0.13   0.17   0.22   0.32   8186    1.0
    fts_rate[23]   0.25  8.7e-4   0.07   0.13   0.19   0.24   0.29   0.41   6940    1.0
    fts_rate[24]   0.53  7.7e-4   0.07   0.39   0.48   0.53   0.57   0.66   7879    1.0
    EG[1,1]        1.34    0.02   1.39    0.0    0.0    1.0    2.0    5.0   4427    1.0
    EG[2,1]        0.77    0.01   0.99    0.0    0.0    0.0    1.0    3.0   4523    1.0
    EG[3,1]        0.41    0.01    0.7    0.0    0.0    0.0    1.0    2.0   4403    1.0
    EG[4,1]        0.48    0.01   0.81    0.0    0.0    0.0    1.0    3.0   4024    1.0
    EG[5,1]        1.88    0.02   1.72    0.0    1.0    1.0    3.0    6.0   4863    1.0
    EG[6,1]        1.52    0.02   1.65    0.0    0.0    1.0    2.0    6.0   4914    1.0
    EG[7,1]        0.47    0.01   0.79    0.0    0.0    0.0    1.0    3.0   4554    1.0
    EG[8,1]        0.43    0.01   0.72    0.0    0.0    0.0    1.0    2.0   3836    1.0
    EG[9,1]        1.23    0.02   1.29    0.0    0.0    1.0    2.0    4.0   4568    1.0
    EG[10,1]        1.4    0.02   1.45    0.0    0.0    1.0    2.0    5.0   4279    1.0
    EG[11,1]       1.03    0.02   1.16    0.0    0.0    1.0    2.0    4.0   4212    1.0
    EG[12,1]       0.67    0.01   0.93    0.0    0.0    0.0    1.0    3.0   4194    1.0
    EG[13,1]        1.4    0.02    1.4    0.0    0.0    1.0    2.0    5.0   4289    1.0
    EG[14,1]       0.79    0.02   1.06    0.0    0.0    0.0    1.0    3.0   4543    1.0
    EG[15,1]        0.9    0.02   1.17    0.0    0.0    1.0    1.0    4.0   4558    1.0
    EG[16,1]       1.43    0.02   1.44    0.0    0.0    1.0    2.0    5.0   4644    1.0
    EG[17,1]       1.32    0.02    1.4    0.0    0.0    1.0    2.0    5.0   3894    1.0
    EG[18,1]       0.88    0.02   1.09    0.0    0.0    1.0    1.0    4.0   4302    1.0
    EG[19,1]        0.9    0.02   1.17    0.0    0.0    1.0    1.0    4.0   3982    1.0
    EG[20,1]       0.45    0.01   0.77    0.0    0.0    0.0    1.0    3.0   3833    1.0
    EG[21,1]       3.24    0.03   2.25    0.0    2.0    3.0    4.0    9.0   4615    1.0
    EG[22,1]       1.72    0.02   1.62    0.0    0.0    1.0    3.0    6.0   4614    1.0
    EG[23,1]       0.75    0.02   1.06    0.0    0.0    0.0    1.0    3.0   3773    1.0
    EG[24,1]       0.54    0.01   0.82    0.0    0.0    0.0    1.0    3.0   3922    1.0
    EG[1,2]        1.91    0.02   1.55    0.0    1.0    2.0    3.0    6.0   4499    1.0
    EG[2,2]        1.17    0.02   1.21    0.0    0.0    1.0    2.0    4.0   4352    1.0
    EG[3,2]        0.63    0.01   0.88    0.0    0.0    0.0    1.0    3.0   4146    1.0
    lp__         -755.6    0.17   6.27 -769.2 -759.7 -755.2 -751.3 -744.6   1395    1.0
    
    Samples were drawn using NUTS at Tue Jul 16 15:37:42 2019.
    For each parameter, n_eff is a crude measure of effective sample size,
    and Rhat is the potential scale reduction factor on split chains (at 
    convergence, Rhat=1).



Convergence and Rhat look great and the model finished much faster which likely indicates that we probably have a better model. Let's look at the predictions.


```python
EG_poisson2 = FIT2.extract(pars=['EG'])['EG']
vis.plot_goal_matrix(EG_poisson2.mean(axis=0))
```


![png](Figures/output_27_0.png)


Compare to the actual observed goals.


```python
vis.plot_goal_matrix(G_all)
```


![png](Figures/output_29_0.png)


These predictions are much better than those of the previous two models. By adding structure to the model, we were able to improve the predictions.


>>>>>>> master
