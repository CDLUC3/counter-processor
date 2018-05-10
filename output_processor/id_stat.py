import config
from models import *
from peewee import *
from .faceted_stat import FacetedStat
#import ipdb; ipdb.set_trace()

class IdStat():
    """The stats for a DOI identifier"""

    def __init__(self, identifier):
        self.identifier = identifier
        # TODO: DataCite doesn't want countries now so removing until they do
        # self.countries = LogItem.select(LogItem.country) \
        #        .distinct() \
        #        .where((LogItem.is_robot == False) & (LogItem.identifier == self.identifier) &
        #            LogItem.event_time.between(config.start_sql(), config.end_sql()))
        # self.countries = [x.country for x in self.countries]

    def stats(self):
        all_faceted_stats = []
        # TODO: DataCite hates countries even though they said they wanted them
        # for country in self.countries:
        for access_method in ('human', 'machine'):
            # TODO: change None back to country
            fs = FacetedStat(self.identifier, None, access_method)
            if FacetedStat.size_of(fs.total_investigations()) > 0 or FacetedStat.size_of(fs.total_requests()) > 0:
                all_faceted_stats.append(fs)
        return all_faceted_stats
