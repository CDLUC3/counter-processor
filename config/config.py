import yaml
import os
from models import *
import input_processor as ip

class Config():
    def __init__(self):
        # load in first level properties of yaml file as properties on this object
        with open("config/config.yaml", 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
        for x in cfg:
            setattr(self, x, cfg[x])

        # if someone has set any of these environment variables, overide whatever loaded from yaml (but make them lowercase props)
        for ev in ('LOG_GLOB', 'PROCESSING_DATABASE', 'ROBOTS_URL'):
            if ev in os.environ:
                setattr(self, ev.lower(), os.environ[ev])

        # set up database, path types and the robots list URL
        base_model.deferred_db.init(self.processing_database)
        ip.LogLine.setup_path_types(self.path_types)
        ip.LogLine.setup_robots_list(self.robots_url)
