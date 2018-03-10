import config
import json
from models import *
from peewee import *
from .report import Report
from .id_stat import IdStat
import datetime
import dateutil.parser
#import ipdb; ipdb.set_trace()

STAT_METHODS = {'Total-Dataset-Requests': 'total_requests', 'Unique-Dataset-Requests': 'unique_requests',
                'Total-Dataset-Requests-Size': 'total_requests_size', 'Unique-Dataset-Requests-Size': 'unique_requests_size',
                'Total-Dataset-Investigations': 'total_investigations', 'Unique-Dataset-Investigations': 'unique_investigations'}

class JsonMetadata():
    """Structures JSON (dict-format) metadata for an id_stat object"""

    def __init__(self, id_stat, meta):
        self.id_stat = id_stat
        self.meta = meta

    def descriptive_dict(self):
        contribs = [ { 'Type': "Name", 'Value': a.author_name } for a in self.meta.author ]
        return {
            'Dataset-Title': self.meta.title,
            'Dataset-ID': [ {'Type': self.meta.identifier_type(), 'Value': self.meta.identifier_bare()} ],
            'Dataset-Contributors': contribs,
            'Dataset-Dates': [ {'Type': "Pub-Date", 'Value': Report.just_date(self.meta.publication_date) } ],
            'Platform': config.platform,
            'Publisher': self.meta.publisher,
            'Publisher-ID': [ { 'Type': self.meta.publisher_id_type(), 'Value': self.meta.publisher_id_bare() } ],
            'Data-Type': "Dataset",
            'YOP': self.meta.publication_year,
            'URI': self.meta.target_url,
            'Performance': [
                self.performance()
            ]
        }

    def performance(self):
        return {
            'Period': { 'Begin-Date': Report.just_date(config.start_date), 'End-Date': Report.just_date(config.end_date) },
            'Instance': self.performance_facet_data()
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
                        'Country': f_stat.country_code,
                        'Access-Method': Report.access_term(f_stat.access_method),
                        'Metric-Type': name,
                        'Count': stat
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
