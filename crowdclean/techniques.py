class Techniques:

    # Use RawSC on a sample to estimate the full answer, with sample values
    # provided by ground truth.
    GROUND_TRUTH_RAWSC = 0

    # Use RawSC on a sample to estimate the full answer, with sample values
    # provided by a simple majority crowd vote.
    CROWD_MAJORITY_RAWSC = 1

    # Train an SVM on a sample with ground truth values, then test it on the
    # full dataaset to estimate an answer.
    SVM_SAMPLE_GT_TRAIN = 2

    # Train an SVM on a sample with crowd majority votes, then test it on the
    # full dataset to estimate an answer.
    SVM_SAMPLE_CROWD_TRAIN = 3

    ALL_TECHNIQUES = [
        GROUND_TRUTH_RAWSC,
        CROWD_MAJORITY_RAWSC,
        SVM_SAMPLE_GT_TRAIN,
        SVM_SAMPLE_CROWD_TRAIN,
    ]
