data {
  int<lower=1> I; // number of teams
  int<lower=1> N; // number of matches
  int<lower=0> M[N, 2]; // match team i vs team j
  int<lower=0> G[I, I]; // number of goals for team i against team j
  int<lower=0> A[I]; // average number of attempts team i
  int<lower=0> T[I]; // average on target rate team i
  int<lower=0> K[I]; // average save rate team j
}

parameters {
}

transformed parameters {
}

model {
  alpha ~ gamma(2,6);
  tau ~ beta(1,1);
  kappa ~ beta(1,1);
  G ~ poisson(alpha*tau*kappa);
}

generated quantities {
}

