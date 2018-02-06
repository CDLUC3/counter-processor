from .base_model import BaseModel
from peewee import *

class MetadataItem(BaseModel):
    title = TextField()
    publisher = TextField()
    publisher_id = IntegerField()
    publication_date = DateField()
    version = IntegerField()
    other_ids = CharField()
    target_url = TextField()
    publication_year = IntegerField()
