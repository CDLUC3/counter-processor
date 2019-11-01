import config
import json
from models import *
from peewee import *
from .report import Report
from .id_stat import IdStat
from .json_metadata import JsonMetadata
import datetime
import dateutil.parser
import io
#import ipdb; ipdb.set_trace()

class JsonReport(Report):
    """Make a JSON report from the generic data report object this inherits from"""

    def output(self):
        with io.open(f"{config.output_file}.json", 'w', encoding='utf8') as jsonfile:
            head = self.header_dict()
            body = {'report-datasets': [self.dict_for_id(my_id) for my_id in self.ids_to_process ] }
            data = dict(list(head.items()) + list(body.items()))
            print('')
            print(f'Writing JSON report to {config.output_file}.json')
            json.dump(data, jsonfile, ensure_ascii=False)
            # the indent makes it much easier to read, but makes the file much bigger sending across the wire
            # the indent is good for troubleshooting and reading to find problems and line numbers are useful to communicate
            # json.dump(data, jsonfile, indent=2, ensure_ascii=False)

    def header_dict(self):
        if config.month_complete():
            exception_dict = {}
        else:
            exception_dict = {
                'code':         3040,
                'severity':     'warning',
                'message':      "partial data returned",
                'help-url':     "String",
                'data':         "usage data has not been processed for the entire reporting period"
            }

        head_dict = { 'report-header': {
                'report-name':          "dataset report",
                'report-id':            "DSR",
                'release':              "rd1",
                'created':              config.last_day(),
                # TODO: DataCite Sashimi doesn't handle reports correctly, so have to put in fake creation dates
                # 'created':              self.just_date(datetime.datetime.now()),
                'created-by':           config.platform,
                'report-attributes':    [],
                'reporting-period':
                    {
                        'begin-date':   config.start_date.strftime('%Y-%m-%d'),
                        'end-date':     config.last_day()
                    },
                'report-filters':       [],
                # any reporting period like in the CSV, or does filter also mean period?
                'exceptions': [ exception_dict ]
            }
        }
        return head_dict

    def dict_for_id(self, my_id):
        """Takes a IdStat object, which is at the level of identifier"""
        print(f'Calculating stats for {my_id}')
        id_stat = IdStat(my_id)
        meta = self.find_metadata_by_identifier(id_stat.identifier)
        js_meta = JsonMetadata(id_stat, meta)
        return js_meta.descriptive_dict()
