import config
import json
from models import *
from peewee import *
from .report import Report
from .id_stat import IdStat
from .faceted_stat import FacetedStat
import datetime
import dateutil.parser
#import ipdb; ipdb.set_trace()

# these are the terms (key) and their methods (values)
STAT_METHODS = {'total-dataset-requests': 'total_requests', 'unique-dataset-requests': 'unique_requests',
                'total-dataset-investigations': 'total_investigations', 'unique-dataset-investigations': 'unique_investigations'}

class JsonMetadata():
    """Structures JSON (dict-format) metadata for an id_stat object"""

    def __init__(self, id_stat, meta):
        self.id_stat = id_stat
        self.meta = meta

    def descriptive_dict(self):
        contribs = [ { 'type': "name", 'value': a.author_name } for a in self.meta.author ]
        return {
            'dataset-title': self.meta.title,
            'dataset-id': [ {'type': self.meta.identifier_type(), 'value': self.meta.identifier_bare()} ],
            'dataset-contributors': contribs,
            'dataset-dates': [ {'type': "pub-date", 'value': Report.just_date(self.meta.publication_date) } ],
            'platform': config.platform,
            'publisher': self.meta.publisher,
            'publisher-id': [ { 'type': self.meta.publisher_id_type(), 'value': self.meta.publisher_id_bare() } ],
            'data-type': "dataset",
            'yop': str(self.meta.publication_year),
            'uri': self.meta.target_url,
            'performance': [
                self.performance()
            ]
        }

    def performance(self):
        return {
            'period': { 'begin-date': Report.just_date(config.start_date), 'end-date': Report.just_date(config.end_date) },
            'instance': self.performance_facet_data()
        }

    def performance_facet_data(self):
        my_stats = []
        for f_stat in self.id_stat.stats():
            for name, meth in STAT_METHODS.items():
                stat = getattr(f_stat, meth)()
                if (stat is None) or FacetedStat.sum(stat, 'ct') == 0:
                    continue

                # setup country counts, volume
                country_counts = {}
                country_volume = {}
                for i in stat:
                    if i['country'] != 'unknown':
                        country_counts[i['country']] = i['ct']
                        if 'vol' in i:
                            country_volume[i['country']] = i['vol']

                # make base stats
                s = {
                        'access-method': Report.access_term(f_stat.access_method),
                        'metric-type': name,
                        'count': FacetedStat.sum(stat, 'ct')
                    }

                # only add volume for requests, nonsensical for investigations
                if meth.endswith('_requests'):
                    s['volume'] = FacetedStat.sum(stat, 'vol')
                s['country-counts'] = country_counts

                # only add volume for requests, nonsensical for investigations
                # right now they don't want country volume broken out
                # if meth.endswith('_requests'):
                #    s['country-volume'] = country_volume

                my_stats.append(s)
        return my_stats


# these are basic metadata issues
# TODO: version is left out for now, add it later.
# "Dataset-Attributes": [
#{
    # "Type": "Dataset-Version",
    # "Value": "VoR"
#}
#],
# TODO: Target URL is missing from this schema
# TODO: is URI correct for the target uri?, or leave it out?
