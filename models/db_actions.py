from .base_model import BaseModel
from .metadata_item import MetadataItem
from .metadata_author import MetadataAuthor
from .log_item import LogItem
from peewee import *

class DbActions(BaseModel):

    @staticmethod
    def create_db():
        db = DbActions._meta.database
        db.create_tables([MetadataItem, MetadataAuthor, LogItem])
