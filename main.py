#!/usr/bin/env python
# from config import Config as cf
import settings
from models import *
import input_processor as ip
import output_processor as op
from upload import upload
import os
import glob
import sys

# import ipdb; ipdb.set_trace()
def main():
    # global config
    # config = cf()
    if not os.path.isfile(config.processing_database):
        DbActions.create_db()
    else:
        DbActions.vacuum() # cleans up DB indices for speed

    the_filenames = config.filenames_to_process()


    print(f'Running report for {config.start_time().isoformat()} to {config.end_time().isoformat()}')

    # process the log lines into a sqlite database
    print(f'{len(the_filenames)} log file(s) will be added to the database')
    print(f'Last processed date: {config.last_processed_on()}')

    for lf in the_filenames:
        with open(lf) as infile:
            print(f'processing {lf}')
            for line in infile:
                ll = ip.LogLine(line)
                ll.populate()
    config.update_log_processed_date()

    print('')
    DbActions.vacuum() # cleanup indices, etc, maybe makes queries faster
    # output for each unique identifier (that isn't robots)
    my_report = op.JsonReport()
    my_report.output()

    if config.upload_to_hub == True:
        upload.send_to_datacite()

    sys.exit(0)

if __name__ == '__main__':
    main()