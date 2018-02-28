from models import *
from peewee import *
#import dateutil.parser
#import datetime
#import re
#import ipdb; ipdb.set_trace()

class Report():
    """A class to make a report based on information already populated into the database"""

    def __init__(self):
        self.ids_to_process = LogItem.select(LogItem.identifier) \
                .distinct() \
                .where((LogItem.is_robot == False) &
                    LogItem.event_time.between(self.start_sql(), self.end_sql()))

    @classmethod
    def setup_report_range(self, my_start, my_end):
        """Set the start and end datetimes for this report scope"""
        # these seem to already be parsed as datetimes by the yaml library
        self.start_time = my_start
        self.end_time = my_end

    @classmethod
    def start_sql(self):
        return self.start_time.isoformat()

    @classmethod
    def end_sql(self):
        return self.end_time.isoformat()

    def iterate_stats(self):
        for my_id in self.ids_to_process:
            print(my_id.identifier)
