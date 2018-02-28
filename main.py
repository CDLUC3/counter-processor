#!/usr/bin/env python
from config import *
from models import *
import input_processor as ip
import output_processor as op
import os
import glob

conf = Config()

ip.LogLine.setup_path_types(conf.path_types)
ip.LogLine.setup_robots_list(conf.robots_url)
ip.LogLine.setup_machines_list(conf.machines_url)

if os.path.isfile(conf.processing_database):
    os.remove(conf.processing_database)
DbActions.create_db()

# process the log lines into a sqlite database
for lf in sorted(glob.glob(conf.log_glob)):
    with open(lf) as infile:
        print(f'processing {lf}')
        for line in infile:
            ll = ip.LogLine(line)
            ll.populate()

# output for each unique identifier in range that isn't robot
my_report = op.Report()
my_report.iterate_stats()
