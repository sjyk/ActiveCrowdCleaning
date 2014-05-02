import numpy as np
LAMBDA = 1.96 # 95% confidence intervals

def single_attribute_check_func(attribute, value):
    def predicate_func(row):
        return row[attribute] == value
    return predicate_func

def rawsc_count(sample_rows, sample_size, dataset_size, predicate_func):
    # compute the clean set
    clean_rows = [dataset_size if predicate_func(row) else 0
                  for row in sample_rows]

    # compute the estimate and error bars
    confidence_bound = LAMBDA * np.sqrt(np.var(clean_rows) / sample_size)
    estimate = np.mean(clean_rows)
    return (estimate, confidence_bound)
