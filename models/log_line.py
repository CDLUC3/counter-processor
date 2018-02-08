from models import *
from peewee import *
import dateutil.parser
import datetime
import requests
#import ipdb; ipdb.set_trace()

class LogLine():
    """A class to handle log line importing from log to database"""

    def __init__(self, line):
        self.line = line.strip()

# Fields: event_time	client_ip	session_id	request_url	identifier	filename	size	user-agent[7]
# title[8]	publisher	publisher_id	authors	publication_date	version	other_ids	target_url	publication_year

    def populate(self):
                if self.line.startswith('#'): return
                fields = [( None if x == '' or x == '-' or x == '????' else x) for x in self.line.split("\t")]

                md_item = find_or_create_metadata(fields)
                country = lookup_geoip(fields[1])

                l_item = LogItem.create(
                    event_time=fields[0],
                    client_ip=fields[1],
                    session_id=fields[2],
                    request_url=fields[3],
                    identifier=fields[4],
                    filename=fields[5],
                    size=fields[6],
                    user_agent=fields[7],
                    country=country,
                    metadata_item_id=md_item.id)
                deduplicate(l_item)

# helper methods without object state

def deduplicate(l_item):
    """Take the created log line and deduplicate any earlier from same person within 30 seconds before"""
    l_item_time = l_item.event_time_as_dt() # why is peewee so crappy? If it's a datetime it should be that, not string
    earlier_time = l_item_time - datetime.timedelta(seconds=30)

    # delete any duplicate requests within 30 seconds earlier by this person from the db
    # use parenthesis around your condition clauses, otherwise peewee will f*ck you up
    (LogItem
        .delete()
        .where(
            LogItem.event_time.between(earlier_time.isoformat(), l_item_time.isoformat()) &
            ((LogItem.session_id == l_item.session_id) | (LogItem.client_ip == l_item.client_ip)) &
            (LogItem.request_url == l_item.request_url) &
            (LogItem.id != l_item.id)
        )
        .execute())

def find_or_create_metadata(fields):
    query = (MetadataItem
                    .select()
                    .where(MetadataItem.identifier == fields[4])
                    .execute())
    mis = list(query)

    if len(mis) < 1:
        mi = MetadataItem.create(
            identifier=fields[4],
            title=fields[8],
            publisher=fields[9],
            publisher_id=fields[10],
            publication_date=fields[12],
            version=fields[13],
            other_ids=fields[14],
            target_url=fields[15],
            publication_year=fields[16]
        )
        create_authors(md_item=mi, author_field=fields[11])
    else:
        mi = mis[0]
    return mi

def create_authors(md_item, author_field):
    # delete previously created authors if we're updating them
    query = (MetadataAuthor
                .delete()
                .where(MetadataAuthor.metadata_item_id == md_item.id)
                .execute())

    for author in author_field.split("|"):
        MetadataAuthor.create(metadata_item_id=md_item.id, author_name=author)

def lookup_geoip(ip_address):
    """Lookup the geographical area from the IP address and return the 2 letter code"""
    # try to grab this IP location cached in our existing database when possible to cut down on API requests
    prev = LogItem.select().where(LogItem.client_ip == ip_address).limit(1)
    for l in prev:
        return l.country

    resp = requests.get(f'http://freegeoip.net/json/{ip_address}')
    if resp.status_code != 200:
        raise ApiError('GET /json/<ip_address> {}'.format(resp.status_code))
    return resp.json()['country_code']
