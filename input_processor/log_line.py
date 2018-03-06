import config
from models import *
from peewee import *
import dateutil.parser
import datetime
import requests
from urllib.parse import urlparse
#import ipdb; ipdb.set_trace()

class LogLine():
    """A class to handle log line importing from log to database"""

    # the columns from the report in this order
    COLUMNS = ('event_time', 'client_ip', 'session_cookie_id', 'user_cookie_id', 'user_id', 'request_url', 'identifier',
        'filename', 'size', 'user_agent', 'title', 'publisher', 'publisher_id', 'authors', 'publication_date', 'version',
        'other_ids', 'target_url', 'publication_year')

    def __init__(self, line):
        line = line.strip()
        if line.startswith('#'):
            self.event_time = None
            return
        split_line = line.split("\t")
        # import the COLUMNS above
        for idx, my_field in enumerate(self.COLUMNS):
            tempval = split_line[idx]
            if tempval == '' or tempval == '-' or tempval == '????':
                tempval = None
            setattr(self, my_field, tempval)

    def populate(self):
        if self.event_time == None:
            return

        # create descriptive metadata
        md_item = self.find_or_create_metadata()

        # add base logging data
        l_item = LogItem()
        for my_field in self.COLUMNS[0:10]:
            setattr(l_item, my_field, getattr(self, my_field))

        l_item.country = self.lookup_geoip()
        l_item.hit_type = self.get_hit_type()
        l_item.is_machine = self.is_machine()
        l_item.is_robot = self.is_robot()

        # link-in desriptive metadata
        l_item.metadata_item = md_item.id

        # add COUNTER style user-session identification for double-click detection
        l_item.add_doubleclick_id()

        # add COUNTER style session tracking with timeslices and different types of tracking
        l_item.add_session_id()

        # save the basic log record
        l_item.save()

        # remove previous duplicates within 30 seconds
        l_item.de_double_click()


    def find_or_create_metadata(self):
        query = (MetadataItem
                        .select()
                        .where(MetadataItem.identifier == self.identifier)
                        .execute())
        mis = list(query)

        if len(mis) < 1:
            mi = MetadataItem.create(
                identifier=self.identifier,
                title=self.title,
                publisher=self.publisher,
                publisher_id=self.publisher_id,
                publication_date=self.publication_date,
                version=self.version,
                other_ids=self.other_ids,
                target_url=self.target_url,
                publication_year=self.publication_year
            )
            self.create_authors(md_item=mi)
        else:
            mi = mis[0]
        return mi

    def create_authors(self, md_item):
        # delete previously created authors if we're updating them
        query = (MetadataAuthor
                    .delete()
                    .where(MetadataAuthor.metadata_item_id == md_item.id)
                    .execute())

        for au in self.authors.split("|"):
            MetadataAuthor.create(metadata_item_id=md_item.id, author_name=au)

    def lookup_geoip(self):
        """Lookup the geographical area from the IP address and return the 2 letter code"""
        # try to grab this IP location cached in our existing database when possible to cut down on API requests
        prev = LogItem.select().where(LogItem.client_ip == self.client_ip).limit(1)
        for l in prev:
            return l.country

        resp = requests.get(f'http://freegeoip.net/json/{self.client_ip}')
        if resp.status_code != 200:
            raise ApiError('GET /json/<ip_address> {}'.format(resp.status_code))
        return resp.json()['country_code']

    def get_hit_type(self):
        o = urlparse(self.request_url)
        for k,v in config.hit_type_regexp().items():
            if v.search(o.path):
                return k
        return None

    def is_robot(self):
        return bool(config.robots_regexp().search(self.user_agent))

    def is_machine(self):
        return bool(config.machines_regexp().search(self.user_agent))
