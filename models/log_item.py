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

    def event_time_as_timeslice(self):
        """This gives a timeslice of yyyymmddhh (year month day hour [in 24 hour clock])"""
        return self.event_time_as_dt().strftime('%Y%m%d%H')

    def add_doubleclick_id(self):
        """Fills a unique identifier (but doesn't save it) after other fields have been filled
        for a user based on counter rules which are given priority from top to bottom:
            - By a unique username/id of a logged in user
            - By a "user cookie" or identifier (it doesn't expire when the browser is closed according to the Internets)
            - By a "session cookie" or identifier (ie it expires when the browser is closed)
            - By ip address + user-agent + hour slice (date and hour of day)"""
        if self.user_id is not None:
            self.calc_doubleclick_id = f'u_{self.user_id}'
        elif self.user_cookie_id is not None:
            self.calc_doubleclick_id = f'uc_{self.user_cookie_id}'
        elif self.session_cookie_id is not None:
            self.calc_doubleclick_id = f's_{self.session_cookie_id}'
        else:
            self.calc_doubleclick_id = f'ip_{self.client_ip}|{self.user_agent}|{self.event_time_as_timeslice()}'

    def add_session_id(self):
        """Create a unique session id based on COUNTER CoP rules with priority from top to bottom:
            - (username or user_id) + (date & hour)
            - (user cookie id) + (date & hour)
            - (session cookie id) + (date & hour)
            - (ip address) + (user-agent) + (date & hour)"""
        import ipdb; ipdb.set_trace()
