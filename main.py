#!/usr/bin/env python
import config
from models import *
import input_processor as ip
import output_processor as op
from upload import upload
import os
import glob
import sys
import datetime

# import ipdb; ipdb.set_trace()
def main():
    if not os.path.isfile(config.Config().processing_database):
        DbActions.create_db()
    else:
        DbActions.vacuum() # cleans up DB indices for speed

    the_filenames = config.Config().filenames_to_process()


    print(f'Running report for {config.Config().start_time().isoformat()} to {config.Config().end_time().isoformat()}')

    # process the log lines into a sqlite database
    print(f'{len(the_filenames)} log file(s) will be added to the database')
    print(f'Last processed date: {config.Config().last_processed_on()}')

    for lf in the_filenames:
        with open(lf) as infile:
            print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  importing {lf}')
            for line in infile:
                ll = ip.LogLine(line)
                ll.populate()

    config.Config().update_log_processed_date()
    config.Config().copy_db_to_disk()

    print('')
    DbActions.vacuum() # cleanup indices, etc, maybe makes queries faster
    # output for each unique identifier (that isn't robots)
    my_report = op.JsonReport()
    my_report.output()

    if config.Config().upload_to_hub == True:
        upload.send_to_datacite()

    if 'test_mode' not in globals():
        sys.exit(0) # this is causing the tests to fail

if __name__ == '__main__':
    main()
