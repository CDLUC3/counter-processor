import yaml
import os
from models import *
import input_processor as ip
import output_processor as op
import sys
import requests
import re
import dateutil.parser
import datetime
import json
import calendar
import exceptions
import geoip2.database

robots_reg = None
machines_reg = None
hit_type_reg = None
last_p_day = None

thismodule = sys.modules[__name__]

ALLOWED_ENV = ('LOG_NAME_PATTERN', 'ROBOTS_URL', 'MACHINES_URL', 'YEAR_MONTH',
    'OUTPUT_FILE', 'OUTPUT_FORMAT', 'PLATFORM', 'HUB_API_TOKEN', 'HUB_BASE_URL', 'UPLOAD_TO_HUB',
    'SIMULATE_DATE', 'MAXMIND_GEOIP_COUNTRY_PATH')

# --- methods used inside this file for processing ---
def read_state():
    """State is a json file that is a dictionary like {'2018-03': {'id': '2018-3-Dash', 'last_processed_day': 17}}"""
    my_dir = "state"
    if not os.path.exists(my_dir):
        os.makedirs(my_dir)

    my_file = f'{my_dir}/statefile.json'
    if not os.path.isfile(my_file):
        with open(my_file, 'w') as f:
            json.dump({}, f, sort_keys = True, indent = 4, ensure_ascii=False)

    with open(my_file) as f:
        return json.load(f)

def make_start_and_end(my_year_month):
    """Makes the start and end dates as yyyy-mm-dd strings for the full month reporting period"""
    yr, mnth = my_year_month.split('-')
    if len(yr) != 4 or len(mnth) != 2:
        raise ValueError('year and month must be YYYY-MM format')
    yr = int(yr)
    mnth = int(mnth)
    _, lastday = calendar.monthrange(yr,mnth)
    return (f'{yr}-{mnth}-01', f'{yr}-{mnth}-{lastday}')

# --- main setup and reading of all the config information ---

state_dict = read_state()

# this makes easy way to completely change the config file to a different one if needed by CONFIG_FILE ENV Variable
config_file = 'config/config.yaml'
if 'CONFIG_FILE' in os.environ:
    config_file = os.environ['CONFIG_FILE']

# load the config file
with open(config_file, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
for x in cfg:
    setattr(thismodule, x, cfg[x])

# load the secrets file if you want to separate any sensitive information from the config in secrets.yaml
# which is .gitignored.  Anything set in secrets will override that top-level key from the config if it's set.
secret = os.path.join(os.path.dirname(config_file), 'secrets.yaml')
if os.path.isfile(secret) == True:
    with open(secret, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
        for x in cfg:
            setattr(thismodule, x, cfg[x])


# if someone has set any of these environment variables, overide whatever loaded from yaml (but make them lowercase props)
for ev in ALLOWED_ENV:
    if ev in os.environ:
        setattr(thismodule, ev.lower(), os.environ[ev])

# we used to have more than one boolean value
#for item in ('upload_to_hub'):
#    my_val = getattr(thismodule, item)
#    if isinstance(my_val, str):
#        setattr(thismodule, item, (my_val == 'True' or my_val == 'true'))

if isinstance(upload_to_hub, str):
    upload_to_hub = (upload_to_hub == 'True' or upload_to_hub == 'true')

# similate date, in case someone wants to simulate running on a day besides now
if 'simulate_date' in vars():
    if isinstance(simulate_date, str):
        run_date = datetime.datetime.strptime(simulate_date, '%Y-%m-%d')
    else:
        run_date = datetime.datetime.combine(simulate_date, datetime.datetime.min.time())
else:
    run_date = datetime.datetime.now()

# parse in the start and end days now
sd, ed = make_start_and_end(year_month)
start_date = dateutil.parser.parse(sd)
end_date = dateutil.parser.parse(ed)

# set up database path
processing_database = f'state/counter_db_{year_month}.sqlite3'
base_model.deferred_db.init(processing_database)

# set up MaxMind geoip database path.  We use binary one downloaded from https://dev.maxmind.com/geoip/geoip2/geolite2/
geoip_reader = geoip2.database.Reader(maxmind_geoip_country_path)

dsr_release = 'RD1'

def start_time():
    return datetime.datetime.combine(start_date, datetime.datetime.min.time())

def end_time():
    return datetime.datetime.combine(end_date, datetime.datetime.min.time()) + datetime.timedelta(days=1)

def last_day():
    """The last day available in the period, either yesterday if in same month, or else last day of month if it has passed"""
    global last_p_day
    if last_p_day is not None:
        return last_p_day
    if end_time() < run_date:
        last_p_day = (end_time() - datetime.timedelta(days=1)).strftime('%Y-%m-%d') # go 1 day back because it's at 00:00 hours the first day of the next month
    else:
        last_p_day = (run_date - datetime.timedelta(days=1)).strftime('%Y-%m-%d') # a day ago from the run date
    return last_p_day

def month_complete():
    return (run_date > end_time())

def robots_regexp():
    """Get the list of robots/crawlers from a list that is one per line
    from the URL and make a regular expression for the detection"""
    global robots_reg
    if robots_reg is not None:
        return robots_reg
    resp = requests.get(robots_url)
    if resp.status_code != 200:
        raise exceptions.ApiError(f'GET {url} failed.')
    lines = resp.text.splitlines()
    lines = [s for s in lines if not s.startswith('#')]
    robots_reg = re.compile('|'.join(lines))
    return robots_reg

def machines_regexp():
    """Get the list of machines from a list that is one per line
    from the URL and make a regular expression for the detection"""
    global machines_reg
    if machines_reg is not None:
        return machines_reg
    resp = requests.get(machines_url)
    if resp.status_code != 200:
        raise exceptions.ApiError(f'GET {url} failed.')
    lines = resp.text.splitlines()
    lines = [s for s in lines if not s.startswith('#')]
    machines_reg = re.compile('|'.join(lines))
    return machines_reg

def hit_type_regexp():
    """Make hit type regular expressions for investigation vs request"""
    global hit_type_reg
    if hit_type_reg is not None:
        return hit_type_reg
    hit_type_reg = { 'investigation': re.compile( '|'.join( path_types['investigations']) ),
        'request': re.compile( '|'.join(path_types['requests']))}
    return hit_type_reg

def start_sql():
    return start_time().isoformat()

def end_sql():
    return end_time().isoformat()

def last_processed_on():
    """gives string for last day it was processed for this month"""
    if year_month in state_dict and 'last_processed_day' in state_dict[year_month]:
        return f'{year_month}-{ "%02d" % state_dict[year_month]["last_processed_day"] }'
    else:
        return f'not processed yet for {year_month}'

def filenames_to_process():
    """Create list of filenames to process that haven't been done yet.
    They may be from 1st of month until yesterday (or last day of month).
    Or could start from the file after last we processed until yesterday
    (or the last day of the month)."""
    ld = int(last_day().split('-')[2]) # last day to process, yesterday (if in period) or end of month

    # last (previously) processed day
    if year_month in state_dict:
        to_process_from = state_dict[year_month]['last_processed_day'] + 1
    else:
        to_process_from = 1

    to_process_from_str = year_month + '-' + ("%02d" % to_process_from)
    if to_process_from > ld:
        return []

    return [ log_name_pattern.replace('(yyyy-mm-dd)', year_month + '-' + ("%02d" % x))
        for x in range(to_process_from, ld + 1) ]

def update_log_processed_date():
    if year_month in state_dict:
        state_dict[year_month]['last_processed_day'] = int(last_day().split('-')[2])
    else:
        state_dict[year_month] = {'last_processed_day': int(last_day().split('-')[2])}
    with open('state/statefile.json', 'w') as f:
        json.dump(state_dict, f, sort_keys = True, indent = 4, ensure_ascii=False)

def current_id():
    if 'id' in state_dict[year_month]:
        return state_dict[year_month]['id']
    else:
        return None

def write_id(the_id):
    state_dict[year_month]['id'] = the_id
    with open('state/statefile.json', 'w') as f:
        json.dump(state_dict, f, sort_keys = True, indent = 4, ensure_ascii=False)
