import config
import json
from models import *
from peewee import *
from .report import Report
from .id_stat import IdStat
import datetime
import dateutil.parser
#import ipdb; ipdb.set_trace()

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
            'Instance': [ {'some': 'stuff'}]
        }

    def performance_facet_data(self):
        pass


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
