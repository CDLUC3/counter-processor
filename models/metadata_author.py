from .base_model import BaseModel
from peewee import *
from .metadata_item import MetadataItem

class MetadataAuthor(BaseModel):
    metadata_item = ForeignKeyField(MetadataItem, backref='author')
    author_name = TextField()
