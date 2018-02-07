from .base_model import BaseModel
from peewee import *
from .metadata_item import MetadataItem

class MetadataAuthor(BaseModel):
    """These are the authors in the sqlite database based on peewee ORM"""
    metadata_item = ForeignKeyField(MetadataItem, backref='author')
    author_name = TextField()
