# from config import Config as cf
# config = cf()

from models import *
from peewee import *
from .faceted_stat import FacetedStat
#import ipdb; ipdb.set_trace()

class IdStat():
    """The stats for a DOI identifier"""

    def __init__(self, identifier):
        self.identifier = identifier

    def stats(self):
        all_faceted_stats = []
        for access_method in ('human', 'machine'):
            fs = FacetedStat(self.identifier, access_method)
            if FacetedStat.sum(fs.total_investigations(), 'ct') > 0 or FacetedStat.sum(fs.total_requests(), 'ct') > 0:
                all_faceted_stats.append(fs)
        return all_faceted_stats
