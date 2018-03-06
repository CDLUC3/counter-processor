#!/usr/bin/env python
import config
from models import *
import input_processor as ip
import output_processor as op
import os
import glob
# import ipdb; ipdb.set_trace()

if not config.only_calculate == True:
    if os.path.isfile(config.processing_database):
        os.remove(config.processing_database)
    DbActions.create_db()

print(f'Running report for {config.start_time.isoformat()} to {config.end_time.isoformat()}')

# process the log lines into a sqlite database
if not config.only_calculate == True:
    for lf in sorted(glob.glob(config.log_glob)):
        with open(lf) as infile:
            print(f'processing {lf}')
            for line in infile:
                ll = ip.LogLine(line)
                ll.populate()

# output for each unique identifier (that isn't robots)
my_report = op.TsvReport()
my_report.output()
