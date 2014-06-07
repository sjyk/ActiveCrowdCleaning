function error = eval_sc_sum(sc_estimate, labels)
error = abs(sc_estimate - sum(labels))/sum(labels);