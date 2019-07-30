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

