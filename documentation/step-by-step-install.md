# Step by step install steps and example running the python script

## Get the code

<pre>
git clone https://github.com/CDLUC3/counter-processor.git
cd counter-processor
git checkout <em>branch-or-tag</em>
</pre>

## Set an environment for python besides your system environment

You may need to install python 3.7 or later on your system if it is not there already.
3.7+ is required because of some sqlite3 options not available in earlier versions.  This
may be set as the command `python` or `python3` on your system.

This may be through your package manager (apt, yum, homebrew, etc) or manually.

Programs for managing multiple versions of Python such as pyenv, virtualenv or update-alternatives or others
exist, but are beyond the scope of this readme and are documented on the internet. 

Maybe [this big page of installation instructions](https://realpython.com/installing-python/) is helpful.

## Get the GeoLite2 Country database

I'm leaving the previous instructions about obtaining the database below.  MaxMind has
changed their licensing terms for new updates.

In the future, they require registration, obtaining a key and updating the database on a regular
schedule and perhaps other changes to the software to use their databases.  See
[Ycombinator discussion](https://news.ycombinator.com/item?id=21915160) about this.

Until that work can be completed and incorporated as part of the processor, the best bet is
to use an old database from before the license changes.
[Internet Archive](https://web.archive.org/web/20191222130401/https://dev.maxmind.com/geoip/geoip2/geolite2/)
has copies of those old databases.


<hr>


## download the database
```
wget https://web.archive.org/web/20191222130401/https://geolite.maxmind.com/download/geoip/database/GeoLite2-Country.tar.gz

tar zxvf GeoLite2-Country.tar.gz # extract the database

# copy it to the maxmind_geoip directory inside the app for defaults
cp GeoLite2-Country_<em>release-date</em>/GeoLite2-Country.mmdb <app_directory>/maxmind_geoip
</pre>
```

## Edit the *config/config.yaml* file
- to have your correct *platform* name.
This would be your repository name that is submitted to the Counter hub.
- modify the regular expressions in the *path_types* section of the config.yaml file
for classifying urls (or any string patterns) into *investigations* and *requests*.
  - While the Counter CoP, counts a *request* as an *investigation*, you will want to classify each as a distinct type
  with your regular expression and not overlap the two. The processor will
  take care of "double-counting"  all *requests* as an *investigation* for you.
- *hub_api_token*: set this value in a *secrets.yaml* file in the same directory as your *config.yaml*
if you are committing your *config.yaml* to a public repository. Be sure to exclude the *secrets.yaml*
from being committed to a public place such as with a .gitignore file.  The *hub_api_token* is used for
automatically submitting to the hub if you have that option enabled.

## Ensure that the program's dependencies are installed

<pre>
# to get back to your counter-processor top-level directory
cd ..

# be sure pip has the correct requirements installed
pip3 install -r requirements.txt
</pre>

## Copy a very simple log file and be sure the counter-processor runs

<pre>
# copy a small sample log to process
cp sample_logs/counter_2018-05-01.log log/

# try running the processor to simulate adding one day to the database
YEAR_MONTH=2018-05 SIMULATE_DATE=2018-05-02 ./main.py
</pre>

## Further info
The processor tracks some state in the *state/* directory.  It creates a
sqlite database for each month and also tracks the last processed date
and any existing identifiers for re-submitting a monthly report
(given out by the hub server).  This allows
the script to run on a daily basis to send updates to the hub. It means it
only reprocesses log files that have not been processed yet before
recalculating states again for the month.

To clear all state for a month, you may delete the sqlite database for that
month and remove the month's section in the *statefile.json* file with
a text editor.

## Examples

### Process all daily log files (from separate files) for a month and year using the default naming pattern

<pre>
# assuming the current date is later than May 2018, this will process all daily log files
# that have not been processed yet for that month and year.

YEAR_MONTH=2018-05 ./main.py
</pre>

### Process an entire month from one log file
<pre>
# I want to process old things with the processor for an entire month from one log file

# This is creating a report for 2014-01 with the log file you specify.
# The LOG_NAME_PATTERN doesn't contain the exact string "(yyyy-mm-dd)"
# and so daily log files are not iterated through for adding to the database.

YEAR_MONTH=2014-01 LOG_NAME_PATTERN="/path/to/my/log/counter_2014-01.log" ./main.py
</pre>

### Process January 2014 from two seperate log files for the first and last halves of month
<pre>
# I want to process from logs divided into January 1-15th and January 16-31

# This is similar to the example above for the month from one log file (see that for background info).

# The processor normally processes everything up until yesterday to save the date for
# what has been processed and continue pulling in logs the next day.

# Simulating the date to be a day after the last date will help it track the state of what is processed correctly.

# No need to simulate the date for the second time it is run since any current time after
# that month will save state that is has processed everything through the end of the month.

YEAR_MONTH=2014-01 SIMULATE_DATE="2014-01-16" LOG_NAME_PATTERN="/my/log/counter_2014-first-half.log" ./main.py
YEAR_MONTH=2014-01 LOG_NAME_PATTERN="/my/log/counter_2014-second-half.log" ./main.py
</pre>

### I'm running the processor every single day from the previous night's log files

Make a bash script like this one:
<pre>
#!/bin/sh

# set up any environment things you need for paths to python, etc.

cd counter-processor

# set a variable for yesterday's month and year
YESTMONTH="`date -d "yesterday 13:00" '+%Y-%m'`"

# This will process any daily logs with "(yyyy-mm-dd)" being replaced with the actual
# date in the filename (and no parenthesis in the actual filenames).  It will try to
# pull in any daily log files not yet pulled in according to the state in state/statefile.json
# for that year and month.

YEAR_MONTH=$YESTMONTH LOG_NAME_PATTERN="/my/directory/counter_(yyyy-mm-dd).log" ./main.py
</pre>

## Other quick information and options

- Change *upload\_to\_hub* to "True" in order to automatically submit to the hub after calculating stats.
Using this option will also track the identifier returned from the hub for use in future PUT
requests to update the stats for this month.
- You may run the script multiple times on the same day and it will not pull in the same log files
(such as for yesterday) additional times since it tracks state and knows the last day that has been processed.
It will only recalculate stats in this case.
- See the main README.md for information about other configuration options.
- You may either set configuration options in the *config.yaml* or else set
environment variables such as shown in examples above.  Setting an environment variable
overrides the setting in the config.
