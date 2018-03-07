import yaml
import os
from models import *
import input_processor as ip
import output_processor as op
import sys
import requests
import re
import dateutil.parser

robots_reg = None
machines_reg = None
hit_type_reg = None

thismodule = sys.modules[__name__]

ALLOWED_ENV = ('LOG_GLOB', 'PROCESSING_DATABASE', 'ROBOTS_URL', 'MACHINES_URL', 'START_TIME', 'END_TIME',
    'OUTPUT_FILE', 'PLATFORM', 'ONLY_CALCULATE')

# this makes easy way to completely change the config file to a different one if needed by CONFIG_FILE ENV Variable
config_file = 'config/config.yaml'
if 'CONFIG_FILE' in os.environ:
    config_file = os.environ['CONFIG_FILE']

with open(config_file, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
for x in cfg:
    setattr(thismodule, x, cfg[x])

# if someone has set any of these environment variables, overide whatever loaded from yaml (but make them lowercase props)
for ev in ALLOWED_ENV:
    if ev in os.environ:
        setattr(thismodule, ev.lower(), os.environ[ev])

if isinstance(start_time, str):
    start_time = dateutil.parser.parse(start_time)

if isinstance(end_time, str):
    end_time = dateutil.parser.parse(end_time)

# set up database path
base_model.deferred_db.init(processing_database)


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
    return start_time.isoformat()

def end_sql():
    return end_time.isoformat()
