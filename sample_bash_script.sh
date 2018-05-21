#!/usr/bin/env bash
# This is a sample script to be run nightly.  It makes sure that python is in the path,
# and sets up some env variables for the month to run a report for (yesterday's month)
# and where to find the logs and runs the processor
export PATH=$HOME/src/python/Python-3.6.4/:$PATH
export PYTHONPATH=$HOME/src/python/Python-3.6.4
python --version
# cd counter-processor
# may need to do this to get dependencies
# ~/src/python/bin/pip3 install -r requirements.txt
YESTMONTH="`date -d "yesterday 13:00" '+%Y-%m'`"
YEAR_MONTH=$YESTMONTH LOG_NAME_PATTERN="/apps/dash2/apps/ui/current/log/counter_(yyyy-mm-dd).log" ./main.py
