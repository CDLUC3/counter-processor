from .base_model import BaseModel
from .person import Person
from .pet import Pet
from .metadata_item import MetadataItem
from .metadata_author import MetadataAuthor
from .log_item import LogItem
from peewee import *

class DbActions(BaseModel):

    @staticmethod
    def create_db():
        # import ipdb; ipdb.set_trace()
        db = DbActions._meta.database
        db.create_tables([Person, Pet, MetadataItem, MetadataAuthor, LogItem])
