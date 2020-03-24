
# Predicting Match Outcomes for the FIFA Women's World Cup 2019
*Derek Miller*


## Introduction

For this case study, I will be using data I collected during the FIFA Women's World Cup 2019 to predict the winner of actual and hypothetical matches between each team. In particular, the tournament structure for a FIFA World Cup lends itself nicely to Bayesian analysis. Here's how the tournament is structured for the 2019 Women's World Cup.

*Group Phase*

The first stage of the tournament is called the group phase. Each of 24 teams are assigned to a group with 3 other teams. Each team will compete in at least 3 matches, one for every other team in their group. The match duration is 90 minutes. The possible outcomes for a team are a win, a loss, or a draw. Points are awarded for each outcome: 3 points for a win, 1 point for a draw, 0 points for a loss. The top 16 teams with the most points after the group stage advance to the knockout phase of the tournament. Each round after that eliminates half of the teams from the tournament. The naming conventions for each round are the Round of 16, the quarter finals, the semi-finals, and the final.

*Knockout Phase*

The second stage of the tournament is the knockout phase, where a team must win to advance. No draws are allowed in this stage. When two teams are tied at the end of 90 minutes, the match continues for two additional 15-minute periods. If the teams are still tied at the end of extra time, the match proceeds to penalty kicks to determine the winner.

*For a case study on Bayesian modeling, check out ```tutorial.ipynb```.*
