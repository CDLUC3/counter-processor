import config
from models import *
from peewee import *
from .report import Report
import csv
#import ipdb; ipdb.set_trace()

class TsvReport():
    """Make a TSV report from the generic data report object"""
    def __init__(self):
        self.my_report = Report()

    def output(self):
        for i in self.my_report.iterate_facet_stats():
            self.printrr(i)

    def printrr(self, f):
        """A dumb method to print out info so I can debug/see working output"""
        print('')
        print(f'id: {f.identifier}, country: {f.country_code}, method: {f.access_method}')
        print(f'  total_investigations: {f.total_investigations()}')
        print(f'  total_requests: {f.total_requests()}')
        print(f'  unique_investigations: {f.unique_investigations()}')
        print(f'  unique_requests: {f.unique_requests()}')
        print(f'  total_requests_size: {f.total_requests_size()}')
