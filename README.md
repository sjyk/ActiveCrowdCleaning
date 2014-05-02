ActiveCrowdCleaning
===================

Loading Data
------------
* Update the paths in `crowdclean/loader.py` to reference your raw data files.
* Run `python crowdclean/loader.py`. You now have a sqlite database in
  `data/tweet_records.db`. Check out `crowdclean/sql.py` to get a sense of the
  schema.