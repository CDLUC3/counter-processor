#!/usr/bin/env python
from config import *
from models import *
import input_processor as ip
import os

conf = Config()

ip.LogLine.setup_path_types(conf.path_types)
ip.LogLine.setup_robots_list(conf.robots_url)

if os.path.isfile(conf.processing_database):
    os.remove(conf.processing_database)
DbActions.create_db()

with open(conf.log_files) as infile:
    for line in infile:
        ll = ip.LogLine(line)
        ll.populate()
