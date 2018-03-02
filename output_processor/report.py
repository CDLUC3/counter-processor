import config
from models import *
from peewee import *
from .id_stat import IdStat
import csv
#import ipdb; ipdb.set_trace()

class Report():
    """A class to generate data for a report, that a specific kind of report can take and iterate/output from"""

    def __init__(self):
        self.ids_to_process = LogItem.select(LogItem.identifier) \
                .distinct() \
                .where((LogItem.is_robot == False) &
                    LogItem.event_time.between(config.start_sql(), config.end_sql()))
        self.ids_to_process = [x.identifier for x in self.ids_to_process]

    def iterate_facet_stats(self):
        for my_id in self.ids_to_process:
            # print(my_id.identifier)
            id_stat = IdStat(my_id)
            for facet_stat in id_stat.stats():
                yield facet_stat

    def find_metadata_by_identifier(self, doi):
        return MetadataItem.select().where(MetadataItem.identifier==doi).order_by(MetadataItem.id.desc()).get()

    def printrr(self, f):
        """A dumb method to print out info so I can debug/see working output"""
        print('')
        print(f'id: {f.identifier}, country: {f.country_code}, method: {f.access_method}')
        print(f'  total_investigations: {f.total_investigations()}')
        print(f'  total_requests: {f.total_requests()}')
        print(f'  unique_investigations: {f.unique_investigations()}')
        print(f'  unique_requests: {f.unique_requests()}')
        print(f'  total_requests_size: {f.total_requests_size()}')
        print(f'  unique_requests_size: {f.unique_requests_size()}')
