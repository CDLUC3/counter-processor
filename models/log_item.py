from .base_model import BaseModel
from .metadata_item import MetadataItem
from peewee import *
import dateutil.parser
import datetime
import re
import hashlib

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
    country = CharField(null=True, index=True)
    hit_type = CharField(null=True, index=True)
    is_robot = BooleanField(default=False, index=True)
    is_machine = BooleanField(default=False, index=True)
    metadata_item = ForeignKeyField(MetadataItem, backref='log_items')
    calc_doubleclick_id = BlobField(null=True, index=True)
    calc_session_id = BlobField(null=True, index=True)

    def event_time_as_dt(self):
        return dateutil.parser.parse(self.event_time)

    def event_time_as_timeslice(self):
        """This gives a timeslice of yyyymmddhh (year month day hour [in 24 hour clock])"""
        return self.event_time_as_dt().strftime('%Y%m%d%H')

    def bare_identifier(self):
        m = re.search('^([a-zA-Z]{2,4}\:)(.+)', self.identifier)
        if m is None:
            return self.identifier
        else:
            return m.group(2)

    def add_doubleclick_id(self):
        """Fills a unique identifier (but doesn't save it) after other fields have been filled
        for a user based on counter rules which are given priority from top to bottom:
            - By a unique username/id of a logged in user
            - By a "user cookie" or identifier (it doesn't expire when the browser is closed according to the Internets)
            - By a "session cookie" or identifier (ie it expires when the browser is closed)
            - By ip address + user-agent + hour slice (date and hour of day)"""
        if self.user_id is not None:
            self.calc_doubleclick_id = hashlib.md5(f'u_{self.user_id}'.encode()).digest()
        elif self.user_cookie_id is not None:
            self.calc_doubleclick_id = hashlib.md5(f'uc_{self.user_cookie_id}'.encode()).digest()
        elif self.session_cookie_id is not None:
            self.calc_doubleclick_id = hashlib.md5(f's_{self.session_cookie_id}'.encode()).digest()
        else:
            self.calc_doubleclick_id = hashlib.md5(f'ip_{self.client_ip}|{self.user_agent}|{self.event_time_as_timeslice()}'.encode()).digest()

    def add_session_id(self):
        """Create a unique session id based on COUNTER CoP rules with priority from top to bottom:
            - (username or user_id) + (date & hour)
            - (user cookie id) + (date & hour)
            - (session cookie id) + (date & hour)
            - (ip address) + (user-agent) + (date & hour)"""
        if self.user_id is not None:
            self.calc_session_id = hashlib.md5(f'u_{self.user_id}|{self.event_time_as_timeslice()}'.encode()).digest()
        elif self.user_cookie_id is not None:
            self.calc_session_id = hashlib.md5(f'uc_{self.user_cookie_id}|{self.event_time_as_timeslice()}'.encode()).digest()
        elif self.session_cookie_id is not None:
            self.calc_session_id = hashlib.md5(f's_{self.session_cookie_id}|{self.event_time_as_timeslice()}'.encode()).digest()
        else:
            self.calc_session_id = hashlib.md5(f'ip_{self.client_ip}|{self.user_agent}|{self.event_time_as_timeslice()}'.encode()).digest()

    def de_double_click(self):
        """Remove previous items the same as this one for this user according to COUNTER rules within 30 seconds previous"""
        earlier_time = self.event_time_as_dt() - datetime.timedelta(seconds=30)

        # delete any duplicate requests within 30 seconds earlier by this person from the db
        # use parenthesis around your condition clauses, otherwise peewee will mess you up
        (LogItem
            .delete()
            .where(
                LogItem.event_time.between(earlier_time.isoformat(), self.event_time_as_dt().isoformat()) &
                (LogItem.calc_doubleclick_id == self.calc_doubleclick_id ) &
                (LogItem.request_url == self.request_url) &
                (LogItem.id != self.id)
            )
            .execute())
