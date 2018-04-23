import config
import json
from models import *
from peewee import *
from .report import Report
from .id_stat import IdStat
import datetime
import dateutil.parser
#import ipdb; ipdb.set_trace()

# these are the terms (key) and their methods (values)
STAT_METHODS = {'total-dataset-requests': 'total_requests', 'unique-dataset-requests': 'unique_requests',
                'total-dataset-investigations': 'total_investigations', 'unique-dataset-investigations': 'unique_investigations'}
# These methods are not used for now because more ongoing discussion around them and unclear specification
# 'total-dataset-requests-size': 'total_requests_size', 'unique-dataset-requests-size': 'unique_requests_size',

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
            'yop': self.meta.publication_year,
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
        # import ipdb; ipdb.set_trace()
        for f_stat in self.id_stat.stats():
            for name, meth in STAT_METHODS.items():
                stat = getattr(f_stat, meth)()
                if stat == 0 or stat is None:
                    continue
                my_stats.append(
                    {
                        'country': f_stat.country_code,
                        'access-method': Report.access_term(f_stat.access_method),
                        'metric-type': name,
                        'count': stat
                    }
                )
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
