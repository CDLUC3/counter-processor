from .base_model import BaseModel
from peewee import *
import re

class MetadataItem(BaseModel):
    """These are the log metadata items in the sqlite database based on peewee ORM"""
    identifier = CharField(null=False, index=True)
    title = TextField(null=True)
    publisher = TextField(null=True)
    publisher_id = CharField(null=True)
    publication_date = DateField(null=True)
    version = IntegerField(null=True, index=True)
    other_id = CharField(null=True)
    target_url = TextField(null=True)
    publication_year = IntegerField(null=True)

    def identifier_bare(self):
        m = re.search('^([a-zA-Z]{2,4}\:)(.+)', self.identifier)
        if m is None:
            return self.identifier
        else:
            return m.group(2)

    def identifier_type(self):
        m = re.search('^([a-zA-Z]{2,5})\:(.+)', self.identifier)
        return m.group(1).upper()

    def publisher_id_bare(self):
        m = re.search('^[a-zA-Z]{2,10}[\:\.\=](.+)', self.publisher_id)
        if m is None: return ''
        return m.group(1)

    def publisher_id_type(self):
        m = re.search('^([a-zA-Z]{2,10})[\:\.\=].+', self.publisher_id)
        if m is None: return ''
        return m.group(1).upper()
