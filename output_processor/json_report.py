import config
import json
from models import *
from peewee import *
from .report import Report
import datetime
import dateutil.parser

class JsonReport(Report):
    """Make a JSON report from the generic data report object this inherits from"""

    def output(self):
        with open(f"{config.output_file}.json", 'w') as jsonfile:
            data = {'dog': 'ruff', 'cat': 'meow'}
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)
