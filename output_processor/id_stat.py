import config
from models import *
from peewee import *
from .faceted_stat import FacetedStat
#import ipdb; ipdb.set_trace()

class IdStat():
    """The stats for a DOI identifier"""

    def __init__(self, identifier):
        self.identifier = identifier
        self.countries = LogItem.select(LogItem.country) \
                .distinct() \
                .where((LogItem.is_robot == False) & (LogItem.identifier == self.identifier) &
                    LogItem.event_time.between(config.start_sql(), config.end_sql()))
        self.countries = [x.country for x in self.countries]

    def stats(self):
        all_faceted_stats = []
        for country in self.countries:
            for access_method in ('human', 'machine'):
                fs = FacetedStat(self.identifier, country, access_method)
                if fs.total_investigations() > 0 or fs.total_requests() > 0:
                    all_faceted_stats.append(fs)
        return all_faceted_stats
