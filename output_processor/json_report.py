import config
import json
from models import *
from peewee import *
from .report import Report
from .id_stat import IdStat
from .json_metadata import JsonMetadata
import datetime
import dateutil.parser
#import ipdb; ipdb.set_trace()

class JsonReport(Report):
    """Make a JSON report from the generic data report object this inherits from"""

    def output(self):
        with open(f"{config.output_file}.json", 'w') as jsonfile:
            head = self.header_dict()
            body = {'report_datasets': [self.dict_for_id(my_id) for my_id in self.ids_to_process ] }
            data = dict(list(head.items()) + list(body.items()))
            json.dump(data, jsonfile, indent=2, ensure_ascii=False)

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

    def dict_for_id(self, my_id):
        """Takes a IdStat object, which is at the level of identifier"""
        print(f'Calculating {my_id} stats for json output')
        id_stat = IdStat(my_id)
        meta = self.find_metadata_by_identifier(id_stat.identifier)
        js_meta = JsonMetadata(id_stat, meta)
        return js_meta.descriptive_dict()
