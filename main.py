#!/usr/bin/env python
import config
from models import *
import input_processor as ip
import output_processor as op
from upload import upload
import os
import glob
# import ipdb; ipdb.set_trace()

if not config.only_calculate == True:
    if os.path.isfile(config.processing_database):
        os.remove(config.processing_database)
    DbActions.create_db()

print(f'Running report for {config.start_time().isoformat()} to {config.end_time().isoformat()}')
print('')

# process the log lines into a sqlite database
if not config.only_calculate == True:
    for lf in sorted(glob.glob(config.log_glob)):
        with open(lf) as infile:
            print(f'processing {lf}')
            for line in infile:
                ll = ip.LogLine(line)
                ll.populate()

print('')
# output for each unique identifier (that isn't robots)
if config.output_format == 'tsv':
    my_report = op.TsvReport()
    my_report.output()
elif config.output_format == 'json':
    my_report = op.JsonReport()
    my_report.output()

if config.upload_to_hub == True:
    upload.send_to_datacite()
