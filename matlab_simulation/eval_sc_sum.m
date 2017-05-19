function error = eval_sc_sum(sc_estimate, labels)
error = (sc_estimate - sum(labels))^2/(sum(labels))^2;