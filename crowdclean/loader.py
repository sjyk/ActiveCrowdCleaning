import json
from csv import reader
from h5py import File
from sqlite3 import connect

from sql import *

FEATURE_DATA_FILEPATH = '/Users/dhaas/Downloads/CrowdLabel/tweets10k.vis'
CROWD_LABEL_FILEPATH = '/Users/dhaas/Downloads/CrowdLabel/tweets10k.crd'
FEATURE_NAMES_FILEPATH = '/Users/dhaas/Downloads/CrowdLabel/tweets10k.dict'
TWEET_TEXT_FILEPATH = '/Users/dhaas/Downloads/CrowdLabel/tweets10k.details'

DB_FILEPATH = '../data/tweet_records.db'

class TweetRecord(object):
    FeatureNames = None

    def __init__(self, primary_key, true_label, features, text,
                 crowd_labels=None, true_label2=None):
        if not TweetRecord.FeatureNames:
            TweetRecord.FeatureNames = load_feature_names()
        self.primary_key = primary_key
        self.true_label = true_label
        if true_label2:
            assert true_label == true_label2
        self.features = features
        self.text = text
        self.crowd_labels = crowd_labels or {}

    def majority_crowd_vote(self):
        if not self.crowd_labels:
            return None
        return int(round(sum(self.crowd_labels.values())
                         / float(len(self.crowd_labels))))

    def as_tweet_row(self):
        return ((self.primary_key, self.true_label,
                 self.majority_crowd_vote(), self.text)
                + (','.join([str(feature) for feature in self.features]),))

    def as_crowd_rows(self):
        return [ (crowd_user, self.primary_key, vote, vote == self.true_label)
                 for crowd_user, vote in self.crowd_labels.iteritems()]

    @classmethod
    def from_data_files(cls):
        tweet_records = []
        feature_data = load_feature_data()
        labels = load_crowd_labels()
        tweet_data = load_tweet_text()
        for primary_key in feature_data.keys():
            crowd_labels = labels.get(primary_key, {})
            tweet_records.append(
                cls(
                    primary_key,
                    feature_data[primary_key][0],
                    feature_data[primary_key][1],
                    tweet_data[primary_key][1],
                    crowd_labels=crowd_labels,
                    true_label2 = tweet_data[primary_key][0]))
        return tweet_records

    @classmethod
    def dump(cls, tweet_records):
        try:
            conn = connect(DB_FILEPATH)
            c = conn.cursor()

            # Create tables
            for sql_command in TWEET_TABLE_SQL:
                c.execute(sql_command)
            for sql_command in CROWD_TABLE_SQL:
                c.execute(sql_command)
            for sql_command in FEATURE_TABLE_SQL:
                c.execute(sql_command)

            # Load feature definitions
            c.executemany(INSERT_FEATURE_SQL,
                          [(idx, word)
                           for idx, word in cls.FeatureNames.iteritems()])

            # Insert tweets
            c.executemany(INSERT_TWEET_SQL,
                          [tweet_record.as_tweet_row() for
                           tweet_record in tweet_records])

            # Insert crowd votes
            c.executemany(INSERT_CROWD_SQL,
                          [crowd_vote for tweet_record in tweet_records
                           for crowd_vote in tweet_record.as_crowd_rows()])
            conn.commit()
        finally:
            conn.close()

def load_feature_data(filepath=FEATURE_DATA_FILEPATH):
    raw_data = File(filepath, 'r')['dataset'][:,:].T
    return { int(row[0]) : (int(row[1]), row[2:]) for row in raw_data }

def load_crowd_labels(filepath=CROWD_LABEL_FILEPATH):
    labels = {}
    with open(filepath, 'rb') as crowd_label_file:
        csv_reader = reader(crowd_label_file)
        for row in csv_reader:
            primary_key = int(row[0])
            crowd_ids = row[1::3]
            votes = [int(vote) for vote in row[3::3]]
            labels[primary_key] = { crowd_id : vote for crowd_id, vote
                                    in zip(crowd_ids, votes) }
    return labels

def load_feature_names(filepath=FEATURE_NAMES_FILEPATH):
    feature_names = {}
    with open(filepath, 'r') as feature_name_file:
        return { int(line.split(':')[0]) :
                 unicode(line.split(':')[1].strip(), '8859')
                 for line in feature_name_file }

def load_tweet_text(filepath=TWEET_TEXT_FILEPATH):
    tweets = {}
    with open(filepath, 'rb') as tweet_text_file:
        csv_reader = reader(tweet_text_file)
        for row in csv_reader:
            primary_key = int(row[0])
            real_label = int(row[1])
            tweet_text = unicode(','.join(row[2:]).strip(), '8859')
            tweets[primary_key] = (real_label, tweet_text)
    return tweets

if __name__ == '__main__':
    TweetRecord.dump(TweetRecord.from_data_files())
