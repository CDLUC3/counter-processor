#!/bin/bash
rm state/counter_db_2020-09-01.sqlite3 || true
rm state/statefile.json || true
STARTTIME=$(date +%s)
echo "Starting"
YEAR_MONTH="2020-09" LOG_NAME_PATTERN="/Users/sfisher/counter-test-files/counter_(yyyy-mm-dd).log_combined" \
    UPLOAD_TO_HUB=False SIMULATE_DATE="2020-09-06" ./main.py
echo "Done"
ENDTIME=$(date +%s)
echo "It took $(($ENDTIME - $STARTTIME)) seconds to complete..."
date
