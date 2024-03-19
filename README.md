# Counter Processor

## Introduction

The Counter Processor is a Python 3 (3.10) script for processing dataset access statistics from logs
using the COUNTER Code of Practice for Research Data.

I'd strongly recommend installing python using a tool such as `pyenv` (*nix/MacOS) or `anaconda` or `miniconda`
for managing multiple Python versions and dependencies separate from versions of Python
installed by the operating system.  `pyenv` also has the nice feature of automatically
using the correct version of python when you `cd` into a project directory with a `.python-version`
file that indicates the version of python to use.  `venv` is a built-in tool for creating
virtual environments for Python and does something similar to `pyenv` and can work in tandem
with it.

If using python from the global OS version, you may need to use `pip3` instead of `pip` and
`python3` instead of `python` in the examples below.  If you have a local version of
python installed, you can use `pip` and `python` as shown in the examples.

The software assumes you area already logging your COUNTER dataset *investigations* and *requests* to a log file using a format somewhat similar to extended log format.  The COUNTER Code of Practice requires that descriptive metadata be submitted along with statistics--these items are included in logs to ease later processing.

Log items are separated by tabs (\t) and any missing values may be logged with a dash (-) or by a an empty string.

## Go through an example of installing and running the script

See the [step-by-step-install.md](documentation/step-by-step-install.md) to get started
with some examples.

## Items to log per line for processing
- Event datetime in ISO8601 format
- Client IP address
- Session cookie id (if available, otherwise blank)
- User cookie id (if available, otherwise blank)
- User identifier (if available, otherwise blank)
- Requested URL
- Identifier of requested item (likely a DOI)
- Filename (optional)
- Size of request (required for requests)
- User-agent sent in the request
- Title
- Publisher
- Publisher ID (such as ISNI or GRID)
- Authors, separated by a pipe character (|) if there is more than one author
- Publication Date (ISO8601 format)
- Version
- Other/Alternate ID
- Target URL that the itentifer such as the DOi would resolve to
- Year of Publication

## Overview of processing logs

- Make your logs available to the script on the file system
- Set up the configuration file
- Override any settings you need to change with environment variables
- Run the script, it will go through these stages
  - Log processing
  - Statistic generation and output
  - Submission of statistics

## Make logs available  
You will need to run the script on a computer where the log files you're trying to process are available on the file system for the script to access.

## Download the free IP to geolocation database
The geo-ip uses GeoLite2 data created by MaxMind and is available from
<a href="https://web.archive.org/web/20191222130401/https://dev.maxmind.com/geoip/geoip2/geolite2/" target="_blank">
Internet Archive</a>
(you only need the country database in binary database format).

GeoLite2 is a free IP geolocation database that must be installed. You can download the
database above. Choose the GeoLite2 Country database (binary, gzipped) and extract it to
the maxmind_geoip directory inside the application to use with default configuration,
or put it elsewhere and configure the path as mentioned below.

Newer versions of the database cannot be used with the current version of the script since
additional licensing terms are required such as registering for accounts, having an auto-update
functionality and ensuring it runs regularly. The script has not been updated to take these
additional requirements into account.

## Set up the configuration file
The script takes a number of different configuration parameters in order to run correctly.  See **config/config.yaml** for an example.  To change the configuration you may edit it at config/config.yaml or you can put it at a different location and then specify it with an environment variable when starting the script like the example below.

```CONFIG_FILE=path/to/my/config.yaml ./main.py```

If you don't set a CONFIG_FILE the script will use the one at *config/config.yaml*.

### The options
- **log\_name\_pattern**: This pattern indicates the daily log files it should look for.  Include the string "(yyyy-mm-dd)" in your log file pattern.  It will look for log files and replace this string, without parenthesis and with actual year, month and day.
- **path_types** have two sub-keys, *investigations* and *requests*. Each sub-key has an array of regular expressions for classifying the path (and after) portion of URLs for requests as either an *investigation* or a *request* for the URLs in your system.
- **robots_url** is a url to download a list of regular expressions (one per line in a text file) that the script uses to classify a user-agent as a robot/crawler.
- **machines_url** is a url to download a list of regular expressions (one per line in a text file) that the script uses to classify a user-agent as a machine (rather than human) access.
- **year_month** is the year and month for which you are desiring to create a report.  For example, 2018-05.
- **output_file**: the path and file to write the report to.  Leave off the extension because it will be automatically supplied based on the *output_format*.
- **output_format**: deprecated from earlier versions. It is always json.
- **platform** is the name of your platform which is used in the report output.
- **hub\_api\_token**: set this value in a *secrets.yaml* file in the same directory as your config.yaml if you are committing your config.yaml to a public respository.  Be sure to exclude the secrets.yaml from being committed to a public place such as with a .gitignore file.
- **hub\_base\_url**: A value such as https://metrics.datacite.org that will be as the base to submit data to.
- **upload\_to\_hub**: True/False.  If True, it will attempt to POST the data you generate to the hub.  If False, the script will simply generate the output files and will not attempt uploading (could be useful for troubleshooting).
- **simulate_date**: put in a yyyy-mm-dd date to simulate running a report on that specified year month and day.  Normally the script will process logs and create data output through the previous day based on the system time.  A report run for a month after a reporting period is over will process things up to the end of that reporting month as specified by year_month.  Setting this allows simulating a run on a different day and is mostly for testing.  See information about how state is maintained in the section below to understand what happens when specifying a different date.  The processor expects an orderly processing of logs in chronological order such as running nightly or weekly.
- **maxmind\_geoip\_country\_path**: set the path to the GeoLite2-Country.mmdb binary geolocation database file.  You may need to periodically download updates to this file from MaxMind.
- **output\_volume**: set to True if you'd like volume (file size) information output in the report.  This option is currently not supported when submitting reports to the hub.

## Maintaining State Between Runs

If you process your logs in an orderly way by running the script in chronological order, such as each night, it should correctly maintain state about any previous identifiers used for report submission and also about the last log file that has been processed.

The state is maintained in the state/ directory.  You'll see some sqlite database files and a statefile.json file.

The script maintains a separate sqlite database file for each reporting month in here.  Deleting a month's file will delete any previously processed data in the database for that month.

The statefile.json contains simple json key/value pairs.  There is a section for each month that a report has been run for.  Under each month there is a "last\_processed\_day" key which has a value indicating the last day processing of logs has been completed for.

There is also an id key for each month which indicates the identifier returned by the server on an initial POST request. This id needs to be reused later for PUT requests to replace data (for example if the script for the month is run nightly to update statistics for the month each night).

The state allows data to be added to the database from the logs, for example each night, without reprocessing every log for the month every night.

For example, if the script is run on May 2nd, and for a May 2018 report, it woould process the log file for May 1st and put entries in the 2018-05 database for that log file (from which stats can be calculated).

If run again on May 3rd, it would only need to process the May 2nd log into the database because May 1st has already been processed.

If you don't process every night, the script will process every log file after the last processed log file for the reporting period up until the day before or to the end of the reporting period.

If you run the script multiple times in one day it will not reprocess log files that have already been processed, for example, if the previous day is already marked as processed.  It would simply calculate stats and submit them again from what is already in the database.

It might be important to understand how this works if there is an unusual situation such as an error while processing logs.

If you wish to completely reprocess and submit a month's data from log files you can:

1. Manually send a DELETE request to the hub for an id to remove a report.
2. Remove the state data from the json file for a particular year-month.
3. Remove the appropriate month's sqlite database from the file system
4. Reprocess the month.  If it's after the month, use *year_month* for the months report you'd like.

It might also be important to understand how state works if moving the script to a different system so that you maintain the state files as needed.


## Override selected options in environment variables when running the script
You will want to set the options in the *config.yaml* file that you use, but some options may change every time you run the script.

Most options listed above in the previous section can be overriden for each execution of the program by setting them in environment variables (but in all UPPERCASE letters).  The most likely things to be overridden when you are generating reports:

- **YEAR_MONTH** -- use when you want to change which month you're generating the report for.
- **SIMULATE_DATE** -- if you want to run a report through a different day than the day before what your computer's clock is set to.

An example of overriding:

```YEAR_MONTH="2018-05" LOG_NAME_PATTERN="/path/to/my/logs/counter_(yyyy-mm-dd).log" ./main.py```

## Example run

```
# note: "(yyyy-mm-dd)" is an literal in the string for running this.
# When run with this example, it will look for any daily log files such as "counter_2019-08-01.log",
# "counter_2019-08-02.log" and so on, up until the day before now (or if other options are specified).

$ YEAR_MONTH=2019-08 LOG_NAME_PATTERN="/path/to/my/daily/logs/counter_(yyyy-mm-dd).log" ./main.py
Running report for 2019-08-01T00:00:00 to 2019-09-01T00:00:00
1 daily log file(s) will be added to the database
Last processed date: 2019-08-08
processing /apps/dash2/apps/ui/current/log/counter_2019-08-09.log

Calculating stats for doi:10.7272/Q66Q1V54
Calculating stats for doi:10.6071/M39W8V
Calculating stats for doi:10.7272/Q6639MWG
Calculating stats for doi:10.7280/D1FT10
Calculating stats for doi:10.6078/D1KS3M
Calculating stats for doi:10.15146/R30K59
Calculating stats for doi:10.15146/R31P48
Calculating stats for doi:10.15146/R30P4Z
Calculating stats for doi:10.15146/R32G68
...
Calculating stats for doi:10.6078/D11S3N

Writing JSON report to tmp/test_out.json
submitted
```

## Submitting to the hub

To submit to the hub, set *upload\_to\_hub* to True in either the configuration or an environment variable.  You must also set *hub\_api\_token* and *hub\_base\_url* in the config.yaml or secrets.yaml.  It will then send reports to the hub for you.

If there are errors or problem submitting to the hub, check the tmp/datacite_response_body.txt file.  The first line in this file contains the HTTP response code from the server, the second line contains the response headers and the rest of the file contains the response body received from the server.

Some possible submission problems:
- Submitting to the server using a POST request for a month that has already had data submitted and has already been assigned an ID (where a PUT using that ID would be more appropriate).
- Missing or invalid data is contained in the report (or data for features not yet implemented in the hub such as country counts).
- Is the hub server up and functioning properly?

## Examples/notes

An example of processing only one day to test functioning, using the sample log in this repository.

```
YEAR_MONTH=2018-05 SIMULATE_DATE=2018-05-02 LOG_NAME_PATTERN=sample_logs/counter_2018-05-01.log UPLOAD_TO_HUB=False ./main.py
```

An example of processing an entire month at a time.  There is no literal string of "(yyyy-mm-dd)" in the filename so it will not be used to process daily logs and will take the filename completely literally.
```
YEAR_MONTH=2019-01 LOG_NAME_PATTERN="/path/to/my/log/counter_2019-01.log" UPLOAD_TO_HUB=False ./main.py
```

## Updated for Python 3.10 (2024)

I've updated dependencies to try and address older libraries and update them where
possible.

I installed version 3.10.13 of Python using the `pyenv` tool and was able to run
`pip install -r requirements.txt` to install the newer dependencies.

I was able to process the sample log files using the first example above after
downloading the GeoLite2-Country.mmdb file from the Internet Archive (see link above)
and placing it in the maxmind_geoip directory.

Some of the geolocation libraries were not updated due to licensing changes and
remain at older versions since updating would require additional work to comply
with the new licensing terms.

This is no longer a script in use by Dryad and they have moved on to using the
DataCite web tracker for the statistics they are tracking.
