# Counter Processor

## Introduction

The Counter Processor is a Python 3 (written in 3.6.4) script for processing dataset access statistics from logs
using the COUNTER Code of Practice for Research Data.

The software assumes you area already logging your COUNTER dataset *investigations* and *requests* to a log file using a format somewhat similar to extended log format.  The COUNTER Code of Practice requires that descriptive metadata be submitted along with statistics--these items are included in logs to ease later processing.

Log items are separated by tabs (\t) and any missing values may be logged with a dash (-) or by a an empty string.

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
This product includes GeoLite2 data created by MaxMind, available from
<a href="http://www.maxmind.com">http://www.maxmind.com</a>.

GeoLite2 is a free IP geolocation database that must be installed in the product.  You can download the database from [https://dev.maxmind.com/geoip/geoip2/geolite2/](https://dev.maxmind.com/geoip/geoip2/geolite2/).  Choose the GeoLite2 Country database (binary, gzipped) and extract it to the maxmind_geoip directory inside the application to use with default configuration, or put it elsewhere and configure the path as mentioned below.

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
- **output_format**: Choose either *tsv* or *json* for this value.  Currently only json is fully functional.
- **platform** is the name of your platform which is used in the report output.
- **hub\_api\_token**: set this value in a *secrets.yaml* file in the same directory as your config.yaml if you are committing your config.yaml to a public respository.  Be sure to exclude the secrets.yaml from being committed to a public place such as with a .gitignore file.
- **hub\_base\_url**: A value such as https://metrics.datacite.org that will be as the base to submit data to.
- **upload\_to\_hub**: True/False.  If True, it will attempt to POST the data you generate to the hub.  If False, the script will simply generate the output files and will not attempt uploading (could be useful for troubleshooting).
- **simulate_date**: put in a yyyy-mm-dd date to simulate running a report on that specified year month and day.  Normally the script will process logs and create data output through the previous day based on the system time.  A report run for a month after a reporting period is over will process things up to the end of that reporting month as specified by year_month.  Setting this allows simulating a run on a different day and is mostly for testing.  See information about how state is maintained in the section below to understand what happens when specifying a different date.  The processor expects an orderly processing of logs in chronological order such as running nightly or weekly.
- **maxmind\_geoip\_country\_path**: set the path to the GeoLite2-Country.mmdb binary geolocation database file.  You may need to periodically download updates to this file from MaxMind.

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


## Override selected options in environment variables when running the script##
You will want to set the options in the *config.yaml* file that you use, but some options may change every time you run the script.

Most options listed above in the previous section can be overriden for each execution of the program by setting them in environment variables (but in all UPPERCASE letters).  The most likely things to be overridden when you are generating reports:

- **YEAR_MONTH** -- use when you want to change which month you're generating the report for.
- **SIMULATE_DATE** -- if you want to run a report through a different day than the day before what your computer's clock is set to.

An example of overriding:

```YEAR_MONTH="2018-05" LOG_NAME_PATTERN="/path/to/my/logs/counter_(yyyy-mm-dd).log" ./main.py```

## Example run

I'm sure this will change.

```
$ LOG_GLOB="sample_logs/counter_2018-03-*.log" START_DATE="2018-03-01" END_DATE="2018-03-31" ./main.py
Running report for 2018-03-01T00:00:00 to 2018-04-01T00:00:00

processing sample_logs/counter_2018-03-13.log
processing sample_logs/counter_2018-03-14.log

Calculating stats for doi:10.6071/Z7WC73
Calculating stats for doi:10.5060/D8H59D
Calculating stats for doi:10.7280/D1MW2M
...
Calculating stats for doi:10.6078/D11S3N

Writing JSON report to tmp/test.json
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

An example of processing only one day to test functioning (for January 1st, 2019 an using a log with a name pattern for that day)

```
YEAR_MONTH=2019-01 LOG_NAME_PATTERN="log/counter_(yyyy-mm-dd).log" UPLOAD_TO_HUB=False SIMULATE_DATE=2019-01-02 ./main.py
```
