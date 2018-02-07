#!/usr/bin/env python
from models import *
import os

DB_FILE = 'db/counter_db.sqlite3'
LOG_FILE = 'log/counter_2018-02-06.log'
os.remove(DB_FILE)
#import ipdb; ipdb.set_trace()
DbActions.create_db()

with open(LOG_FILE) as infile:
    for line in infile:
        ll = LogLine(line)
        ll.populate()
