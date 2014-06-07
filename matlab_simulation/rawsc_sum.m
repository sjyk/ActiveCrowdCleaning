function result = rawsc_sum(clean_labels, budget)
N = size(clean_labels, 1);
sample_perm = randperm(N);
sample = sample_perm(1:budget);
result = N * mean(clean_labels(sample));
end

