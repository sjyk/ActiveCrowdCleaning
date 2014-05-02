import json
import os
from matplotlib import pyplot as plt
from sqlite3 import connect, Row

from loader import DB_FILEPATH
from ml import svm_count_positive
from techniques import Techniques
from rawsc import rawsc_count, single_attribute_check_func

RESULTS_DIR = '../results'

# Output: 0.491
GT_QUERY_FULL_SAMPLE = '''
SELECT COUNT(*) * 1.0 /
       (SELECT COUNT(*) FROM tweet where majority_crowd_vote is not null)
FROM tweet
WHERE true_label = 1
      and majority_crowd_vote is not null;
'''

# Output: 0.261--huge crowd bias!
CROWD_QUERY_FULL_SAMPLE = '''
SELECT COUNT(*) * 1.0 /
       (SELECT COUNT(*) FROM tweet where majority_crowd_vote is not null)
FROM tweet
WHERE majority_crowd_vote = 1;
'''

def db():
    conn = connect(DB_FILEPATH)
    conn.row_factory = Row
    return conn

def get_dataset():
    return db().cursor().execute(
        'select * from tweet where majority_crowd_vote is not null;').fetchall()

def get_dataset_size():
    return (db().cursor().execute(
        'select count(*) from tweet where majority_crowd_vote is not null;')
            ).fetchone()[0]

def get_full_gt():
    return db().cursor().execute(GT_QUERY_FULL_SAMPLE).fetchone()[0]

def get_crowd_answer():
    return db().cursor().execute(CROWD_QUERY_FULL_SAMPLE).fetchone()[0]

def uniform_random_sample(sample_size, require_crowd_annotation=True):
    conn = db()
    c = conn.cursor()
    sql = "select * from tweet"
    if require_crowd_annotation:
        sql += " where majority_crowd_vote is not null"
    sql += " order by random() limit " + str(sample_size)
    return c.execute(sql)

def estimate_percent_positive(sample_rows, all_rows, sample_size, dataset_size,
                                 techniques):
    results = {}
    for technique in techniques:
        count, confidence = estimate_count_positive(
            sample_rows, all_rows, sample_size, dataset_size, technique)
        results[technique] = (count/dataset_size, confidence/dataset_size)
    return results

def estimate_count_positive(sample_rows, all_rows, sample_size,
                            dataset_size, technique):
    if technique == Techniques.GROUND_TRUTH_RAWSC:
        return rawsc_count(sample_rows, sample_size, dataset_size,
                           single_attribute_check_func('true_label', 1))
    elif technique == Techniques.CROWD_MAJORITY_RAWSC:
        return rawsc_count(
            sample_rows, sample_size, dataset_size,
            single_attribute_check_func('majority_crowd_vote', 1))
    elif technique == Techniques.SVM_SAMPLE_GT_TRAIN:
        return svm_count_positive(sample_rows, all_rows, 'true_label')
    elif technique == Techniques.SVM_SAMPLE_CROWD_TRAIN:
        return svm_count_positive(sample_rows, all_rows, 'majority_crowd_vote')

def eval_percentage_estimate_on_samples(*sample_size_range_args, **output_args):
    gt_results = []
    majority_results = []
    svm_crowd_results = []
    svm_gt_results = []
    all_rows = get_dataset()
    dataset_size = get_dataset_size()
    sample_sizes = range(*sample_size_range_args)
    for i, sample_size in enumerate(sample_sizes):
        if i % 10 == 0:
            print "processed %d/%d sample sizes..." % (i, len(sample_sizes))

        sample_rows = uniform_random_sample(sample_size).fetchall()
        results = estimate_percent_positive(sample_rows, all_rows, sample_size,
                                            dataset_size,
                                            Techniques.ALL_TECHNIQUES)
        gt_results.append(results[Techniques.GROUND_TRUTH_RAWSC])
        majority_results.append(results[Techniques.CROWD_MAJORITY_RAWSC])
        svm_crowd_results.append(results[Techniques.SVM_SAMPLE_CROWD_TRAIN])
        svm_gt_results.append(results[Techniques.SVM_SAMPLE_GT_TRAIN])
    print "Done!"

    # Plot errors
    correct_val = get_full_gt()
    crowd_bias = abs(get_crowd_answer() - correct_val)
    plt.figure()
    crowd_optimal = plt.axhline(y=crowd_bias, color='r', ls='--',
                                label="Optimal crowd error")
    crowd_optimal = plt.axhline(y=0, color='b', ls='--',
                                label="Optimal gt error")
    gt_plot = plt.errorbar(sample_sizes,
                           [abs(result[0] - correct_val)
                            for result in gt_results],
                           yerr=[result[1] for result in gt_results],
                           fmt='b-', label="RawSC with ground truth labels")
    crowd_plot = plt.errorbar(sample_sizes,
                              [abs(result[0] - correct_val)
                               for result in majority_results],
                              yerr=[result[1] for result in majority_results],
                              fmt='r-',
                              label="RawSC with majority crowd labels")
    svm_crowd_plot = plt.plot(sample_sizes,
                              [abs(result[0] - correct_val)
                               for result in svm_crowd_results],
                              'g-',
                              label="SVM with crowd labels")
    svm_gt_plot = plt.plot(sample_sizes,
                           [abs(result[0] - correct_val)
                            for result in svm_gt_results],
                           'c-',
                           label="SVM with ground truth labels")

    plt.xlabel('Sample size (in rows)')
    plt.ylabel('Error on simple percentage query')
    plt.title('Error estimating percent of positive tweet labels')
    legend = plt.legend(bbox_to_anchor=(1.01, 1), loc=2, borderaxespad=0.)

    log_filename = output_args.get('log_filename')
    if log_filename:
        results = {
            'GT_QUERY_RESPONSE': correct_val,
            'CROWD_QUERY_RESPONSE': get_crowd_answer(),
            'GROUND_TRUTH_RAW_SC': gt_results,
            'CROWD_MAJORITY_RAWSC': majority_results,
            'SVM_SAMPLE_CROWD_TRAIN': svm_crowd_results,
            'SVM_SAMPLE_GT_TRAIN': svm_gt_results,
        }
        with open(os.path.join(RESULTS_DIR, log_filename), 'w') as outfile:
            json.dump(results, outfile, indent=4)

    plot_filename = output_args.get('plot_filename')
    if plot_filename:
        plt.savefig(os.path.join(RESULTS_DIR, plot_filename),
                    bbox_extra_artists=(legend,), bbox_inches='tight')

    show = output_args.get('show', True)
    if show:
        plt.show()

if __name__ == '__main__':
    eval_percentage_estimate_on_samples(
        10, 1001, 20, plot_filename='percentage_estimate_error.png',
        log_filename="percentage_estimate_data.txt",
        show=False)
