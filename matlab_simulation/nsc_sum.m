function result = nsc_sum(dirty_labels, clean_labels, budget)
N = size(clean_labels, 1);
sample_perm = randperm(N);
sample = sample_perm(1:budget);
result = sum(dirty_labels) - N * mean(dirty_labels(sample) - clean_labels(sample));
end

