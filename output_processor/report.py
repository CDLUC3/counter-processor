import config
from models import *
from peewee import *
from .id_stat import IdStat
import datetime
import dateutil.parser
#import ipdb; ipdb.set_trace()

ACCESS_METHOD_TERMS = {'human': 'regular', 'machine': 'machine'}

class Report():
    """A class to generate data for a report, that a specific kind of report can take and iterate/output from"""

    def __init__(self):
        self.ids_to_process = LogItem.select(LogItem.identifier) \
                .distinct() \
                .where((LogItem.is_robot == False) &
                    LogItem.event_time.between(config.Config().start_sql(), config.Config().end_sql()))
        self.ids_to_process = [x.identifier for x in self.ids_to_process]

    def iterate_facet_stats(self):
        for my_id in self.ids_to_process:
            # print(my_id.identifier)
            id_stat = IdStat(my_id)
            for facet_stat in id_stat.stats():
                yield facet_stat

    def find_metadata_by_identifier(self, doi):
        return MetadataItem.select().where(MetadataItem.identifier==doi).order_by(MetadataItem.id.desc()).get()

    @staticmethod
    def just_date(dt):
        if isinstance(dt, ''.__class__): # if this is a string, make it into a datetime, sqlite is poo
            dt = dateutil.parser.parse(dt)
        return dt.strftime("%Y-%m-%d")

    @staticmethod
    def access_term(t):
        return ACCESS_METHOD_TERMS[t]
