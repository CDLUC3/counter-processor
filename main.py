#!/usr/bin/env python
from models import *
import input_processor as ip
import os

DB_FILE = 'db/counter_db.sqlite3'
LOG_FILE = 'log/counter_2018-02-13.log'
PATH_TYPE_REGEXP = {
    'investigations': ('^/api/datasets/[^\/]+$', '^/api/versions/\d+$', '^/stash/dataset/\S+$', '^/stash/data_paper/\S+$'),
    'requests': (
        '^/api/datasets/[^\/]+/download$',
        '^/api/versions/\d+/download$',
        '^/api/downloads/\d+$',
        '^/stash/downloads/download_resource/\d+$',
        '^/stash/downloads/file_download/\d+$',
        '^/stash/downloads/file_stream/\d+$',
        '^/stash/downloads/async_request/\d+$',
        '^/stash/share/\S+$'
        )}

ip.LogLine.setup_path_types(PATH_TYPE_REGEXP)

os.remove(DB_FILE)
#import ipdb; ipdb.set_trace()
DbActions.create_db()

with open(LOG_FILE) as infile:
    for line in infile:
        ll = ip.LogLine(line)
        ll.populate()
