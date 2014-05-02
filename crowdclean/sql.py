TWEET_TABLE_SQL = [
    '''DROP TABLE IF EXISTS tweet;''',
    '''
CREATE TABLE tweet (
    pk INTEGER PRIMARY KEY,
    true_label INT NOT NULL,
    majority_crowd_vote INT,
    text TEXT,
    features TEXT
);
    '''
]

INSERT_TWEET_SQL = '''
INSERT INTO tweet VALUES (?, ?, ?, ?, ?);
'''


CROWD_TABLE_SQL = [
    '''DROP TABLE IF EXISTS crowd;''',
    '''
CREATE TABLE crowd (
    user_id TEXT,
    tweet_id INTEGER REFERENCES tweet(pk) NOT NULL,
    vote INT,
    is_correct INT,
    PRIMARY KEY (user_id, tweet_id)
);
    '''
]


INSERT_CROWD_SQL = '''
INSERT INTO crowd VALUES(?, ?, ?, ?);
'''


FEATURE_TABLE_SQL = [
    '''DROP TABLE IF EXISTS feature;''',
    '''
CREATE TABLE feature (
    idx INTEGER PRIMARY KEY,
    word TEXT
);
    '''
]


INSERT_FEATURE_SQL = '''INSERT INTO feature VALUES(?, ?);'''
