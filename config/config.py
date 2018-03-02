import yaml
import os
from models import *
import input_processor as ip
import output_processor as op
import sys
import requests
import re

robots_reg = None
machines_reg = None
hit_type_reg = None

thismodule = sys.modules[__name__]

#class Config():
#    def __init__(self):
# load in first level properties of yaml file as properties on this object
with open("config/config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)
for x in cfg:
    setattr(thismodule, x, cfg[x])

# if someone has set any of these environment variables, overide whatever loaded from yaml (but make them lowercase props)
for ev in ('LOG_GLOB', 'PROCESSING_DATABASE', 'ROBOTS_URL', 'OUTPUT_FILE'):
    if ev in os.environ:
        setattr(thismodule, ev.lower(), os.environ[ev])

# set up database, path types and the robots list URL
base_model.deferred_db.init(processing_database)
#ip.LogLine.setup_path_types(path_types)
#ip.LogLine.setup_robots_list(robots_url)
#op.Report.setup_report_range(start_time, end_time)

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
