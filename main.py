#!/usr/bin/env python
import models
import os

DB_FILE = 'db/counter_db.sqlite3'
LOG_FILE = 'log/counter_2018-02-06.log'
os.remove(DB_FILE)

models.DbActions.create_db()

with open(LOG_FILE) as infile:
    for line in infile:
        line = line.strip()
        if line.startswith('#'): continue
        fields = [( None if x == '' or x == '-' else x) for x in line.split("\t")]
        print(fields)
        #import ipdb; ipdb.set_trace()
        log_item = models.LogItem.create(
            event_time=fields[0],
            client_ip=fields[1],
            session_id=fields[2],
            request_url=fields[3],
            identifier=fields[4],
            filename=fields[5],
            size=fields[6],
            user_agent=fields[7],
            metadata_item_id=1) # TODO: fix this up.
