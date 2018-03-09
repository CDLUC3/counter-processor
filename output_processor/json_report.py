import config
import json
from models import *
from peewee import *
from .report import Report
import datetime
import dateutil.parser
#import ipdb; ipdb.set_trace()

class JsonReport(Report):
    """Make a JSON report from the generic data report object this inherits from"""

    def output(self):
        with open(f"{config.output_file}.json", 'w') as jsonfile:
            data = self.header_dict()
            json.dump(data, jsonfile, indent=4, ensure_ascii=False)

    def header_dict(self):
        if config.partial_data:
            exception_dict = {
                'code':         3040,
                'Severity':     'Warning',
                'Message':      "Partial Data Returned",
                'Help-URL':     "String",
                'Data':         "Usage data has not been processed for the entire reporting period"
            }
        else:
            exception_dict = {}

        head_dict = { 'report_header': {
                'report-name':      "Dataset Report",
                'report-id':        "DSR",
                'release':          "RD1",
                'created':          self.just_date(datetime.datetime.now()),
                'created-by':       config.platform,
                'report-filters':   [
                    {
                        'Name':     "Begin-Date",
                        'Value':    config.start_date.isoformat()
                    },
                    {
                        'Name':     "End-Date",
                        'Value':    config.end_date.isoformat()
                    }
                ],
                # any reporting period like in the CSV, or does filter also mean period?
                'Exceptions': [ exception_dict ]
            }
        }
        return head_dict
