from .base_model import BaseModel
from peewee import *

class MetadataItem(BaseModel):
    """These are the log metadata items in the sqlite database based on peewee ORM"""
    identifier = CharField(null=False, index=True)
    title = TextField(null=True)
    publisher = TextField(null=True)
    publisher_id = IntegerField(null=True)
    publication_date = DateField(null=True)
    version = IntegerField(null=True)
    other_ids = CharField(null=True)
    target_url = TextField(null=True)
    publication_year = IntegerField(null=True)

    def equals(self, other_metadata_item):
        pass
