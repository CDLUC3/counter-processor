from .base_model import BaseModel
from .metadata_item import MetadataItem
from peewee import *
import dateutil.parser
import datetime

class LogItem(BaseModel):
    """These are the log items in the sqlite database based on peewee ORM"""
    event_time = DateTimeField(null=False, index=True)
    client_ip = CharField(null=False, index=True)
    session_cookie_id = CharField(null=True)
    user_cookie_id = CharField(null=True)
    user_id = CharField(null=True)
    request_url = TextField(null=False, index=True)
    identifier = CharField(null=False, index=True)
    filename = TextField(null=True)
    size = BigIntegerField(null=True)
    user_agent = TextField(null=True)
    country = CharField(null=True)
    metadata_item = ForeignKeyField(MetadataItem, backref='log_items')
    calc_doubleclick_id = TextField(null=True, index=True)
    calc_session_id = TextField(null=True, index=True)

    def event_time_as_dt(self):
        return dateutil.parser.parse(self.event_time)
