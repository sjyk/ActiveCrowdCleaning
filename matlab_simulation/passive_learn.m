function predictions = passive_learn(X, Y, budget)
N = size(Y, 1);
sample_perm = randperm(N);
sample = sample_perm(1:budget);
model = logistic(X(sample,3:end), Y(sample));
predictions = 1./(1+exp(-X(1:N,3:end)*model));
predictions = (predictions >= .5);