from .base_model import BaseModel
from .metadata_item import MetadataItem
from peewee import *

class LogItem(BaseModel):
    event_time = DateTimeField(null=False, index=True)
    client_ip = CharField(null=False, index=True)
    session_id = CharField(null=True, index=True)
    request_url = TextField(null=False, index=True)
    identifier = CharField(null=False, index=True)
    filename = TextField(null=True)
    size = BigIntegerField(null=True)
    user_agent = TextField(null=True)
    country = CharField(null=True)
    metadata_item = ForeignKeyField(MetadataItem, backref='log_items')
