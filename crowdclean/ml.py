from operator import itemgetter
from scipy.sparse import csr_matrix, vstack
#from sklearn.feature_extraction import DictVectorizer
from sklearn.svm import SVC
from sqlite3 import connect

from loader import DB_FILEPATH

FEATURE_VECTOR_CACHE_SIZE = 1000
FEATURE_VECTOR_CACHE = {}
EVAL_MODELS = True

def svm_count_positive(train_rows, test_rows, label_attr):
    label_selection_func = itemgetter(label_attr)
    model = train_svm(train_rows, label_selection_func)
    predictions = model.predict(featurize_tweets(test_rows))

    # TODO: add confidences
    return (float(len([label for label in predictions if label == 1])), 0.)

def train_svm(sample_rows, label_selection_func):
    # build the train set
    X, y = featurize_tweets(sample_rows, label_selection_func)
    model = SVC() # crossvalidate? add probability estimates?
    model.fit(X, y)
    if EVAL_MODELS:
        print "Model training accuracy:",  model.score(X, y)
    return model

def featurize_tweets(tweet_rows, label_selection_func=None):
    labels = []
    feature_vectors = []
    for row in tweet_rows:
        if label_selection_func:
            feature_vector, label = featurize_tweet(row, label_selection_func)
            labels.append(label)
        else:
            feature_vector = featurize_tweet(row)
        feature_vectors.append(csr_matrix(feature_vector))
    X = vstack(feature_vectors)
    if label_selection_func:
        return (X, labels)
    else:
        return X

def featurize_tweet(tweet_row, label_selection_func=None):
    pk = tweet_row['pk']
    if pk in FEATURE_VECTOR_CACHE:
        feature_vector = FEATURE_VECTOR_CACHE[pk]
    else:
#        vectorizer_data = get_vectorizer_data()
#        feature_dict = {}
        str_feature_list = tweet_row['features'].split(',')
        feature_vector = [float(feature) for feature in str_feature_list]
#        for idx in sorted(vectorizer_data['idx_mapping'].keys()):
#            feature_dict[
#                vectorizer_data['idx_mapping'][idx]] = float(str_feature_list[idx])
#        feature_vector = vectorizer_data['vectorizer'].transform(feature_dict)
        if len(FEATURE_VECTOR_CACHE) < FEATURE_VECTOR_CACHE_SIZE:
            FEATURE_VECTOR_CACHE[pk] = feature_vector

    if label_selection_func:
        label = label_selection_func(tweet_row)
        return (feature_vector, label)
    else:
        return feature_vector

_VECTORIZER_DATA = {}
def get_vectorizer_data():
    if _VECTORIZER_DATA:
        return _VECTORIZER_DATA
    features = (connect(DB_FILEPATH)
                .cursor().execute("Select idx, word from feature;"))
    words_to_idxs = {}
    idxs_to_words = {}
    for feature in features:
        words_to_idxs[feature[1]] = feature[0]
        idxs_to_words[feature[0]] = feature[1]
    _VECTORIZER_DATA['vectorizer'] = DictVectorizer().fit([words_to_idxs])
    _VECTORIZER_DATA['idx_mapping'] = idxs_to_words
    return _VECTORIZER_DATA
