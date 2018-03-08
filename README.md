# Counter Processor

## Introduction

The Counter Processor is a Python script for processing dataset access statistics from logs
according to the COUNTER Code of Practice for Research Data.

The software assumes you area already logging your COUNTER dataset *investigations* and *requests* to a log file using a format somewhat similar to extended log format.  The COUNTER Code of Practice requires that descriptive metadata be submitted along with statistics so, these items are included in logs to ease later processing.

Log items are separated by tabs (\t) and missing values may be logged with a dash (-).

## Items to log per line for processing
- Event datetime in ISO8601 format
- Client IP address
- Session cookie id (if available, otherwise blank)
- User cookie id (if available, otherwise blank)
- User identifier (if available, otherwise blank)
- Requested URL
- Identifier of requested item (probably a DOI)
- Filename (optional)
- Size of request (required for requests)
- User-agent sent in the request.
- Title
- Publisher
- Publisher ID (such as GRID or ISNI)
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
  - Submission of statistics (TODO)

##Make logs available  
You will either need to run the script on a computer where the log files you're trying to process are available on the file system.

##Set up the configuration file
The script takes a number of different configuration parameters in order to run correctly.  See **config/config.yaml** for an example.  To change the configuration, either edit this file or copy it and specify your configuration file location with an environment variable on the startup line such as:

```CONFIG_FILE=path/to/my/config.yaml ./main.py```

If you don't set a CONFIG_FILE it will use the one at *config/config.yaml*.

###The options###
- **log_glob** is a glob that indicates what files the processor should load into its sqlite database for processing.
- **processing_database**: the path where you'd like the sqlite database to be written (default is probably OK).
- **path_types** have two sub-keys, *investigations* and *requests*. Each sub-key has an array of regular expressions for classifying the path portion of URLs for requests as either an *investigation* or a *request* for your system.
- **robots_url** is a url to download a list of regular expressions (one per line in a text file) that ths cript uses to classify a user-agent as a robot/crawler.
- **machines_url** is a url to download a list of regular expressions (one per line in a text file) that the script uses to classify a user-agent as a machine (rather than human) access.
- **start_time**: for items included in this report output (like 2018-03-01 00:00:00)
- **end_time**: for items included in this report output (like 2018-04-01 00:00:00)
- **output_file**: the file to write the tab-delimited (TSV) report to.  Other formats coming soon (probably changing).
- **platform** is the name of your platform which is used in the report output.
- **only_calculate**: True/False. If True, it tells the script not to re-process the log files (which might take a while) but to use the already existing database and generate statistics from it.
- **partial_data**: if set to *True*, it adds an exception to the report which indicates that the reporting period you specified does not have complete data available yet.

##Override selected options in environment variables when running the script##
You will want to set the options in the *config.yaml* file that you use, but some options may change every time you run the script. 

Most options listed above in the previous section can be overriden for each execution of the program by setting them in environment variables (but in all UPPERCASE letters).  The most likely things to be overridden when you are generating reports each month are these items:

- **LOG_GLOB**
- **START_TIME**
- **END_TIME**

An example of overriding them:

```LOG_GLOB="log/counter_2018-03-*.log" START_TIME="2018-03-01 00:00:00" END_TIME="2018-04-01 00:00:00" ./main.py```

##Example run##

I'm sure this will change.

```
LOG_GLOB="log/counter_2018-03-*.log" START_TIME="2018-03-01 00:00:00" END_TIME="2018-04-01 00:00:00" ./main.py
Running report for 2018-03-01T00:00:00 to 2018-04-01T00:00:00
processing log/counter_2018-03-06.log
processing log/counter_2018-03-07.log
Writing stats for doi:10.5072/FK2XP72W9B
Writing stats for doi:10.5072/FK2T151W7S
Writing stats for doi:10.5072/FK2J966H3B
Writing stats for doi:10.5072/FK2TX3CS28
Writing stats for doi:10.5072/FK24T6N929
Writing stats for doi:10.5072/FK2CF9RZ9X
Writing stats for doi:10.5072/FK2474DX0J
Writing stats for doi:10.5072/FK2H41S68W
```

##Submitting to the hub##

Who knows? Something magic happens and unicorns and elves dance in the streets.
