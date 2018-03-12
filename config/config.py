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

robots_reg = None
machines_reg = None
hit_type_reg = None

thismodule = sys.modules[__name__]

ALLOWED_ENV = ('LOG_GLOB', 'PROCESSING_DATABASE', 'ROBOTS_URL', 'MACHINES_URL', 'START_DATE', 'END_DATE',
    'OUTPUT_FILE', 'OUTPUT_FORMAT', 'PLATFORM', 'ONLY_CALCULATE', 'PARTIAL_DATA', 'HUB_API_TOKEN', 'HUB_BASE_URL', 'UPLOAD_TO_HUB')

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

for item in ('only_calculate', 'partial_data', 'upload_to_hub'):
    my_val = getattr(thismodule, item)
    if isinstance(my_val, str):
        setattr(thismodule, item, (my_val == 'True' or my_val == 'true'))

if isinstance(start_date, str):
    start_date = dateutil.parser.parse(start_date)

if isinstance(end_date, str):
    end_date = dateutil.parser.parse(end_date)

# set up database path
base_model.deferred_db.init(processing_database)

dsr_release = 'RD1'

def start_time():
    return datetime.datetime.combine(start_date, datetime.datetime.min.time())

def end_time():
    return datetime.datetime.combine(end_date, datetime.datetime.min.time()) + datetime.timedelta(days=1)

def robots_regexp():
    """Get the list of robots/crawlers from a list that is one per line
    from the URL and make a regular expression for the detection"""
    global robots_reg
    if robots_reg is not None:
        return robots_reg
    resp = requests.get(robots_url)
    if resp.status_code != 200:
        raise ApiError(f'GET {url} failed.')
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
        raise ApiError(f'GET {url} failed.')
    lines = resp.text.splitlines()
    lines = [s for s in lines if not s.startswith('#')]
    machines_reg = re.compile('|'.join(lines))
    return machines_reg

def hit_type_regexp():
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
