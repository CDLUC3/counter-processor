from models import *
from peewee import *
import dateutil.parser
import datetime
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

                l_item = LogItem.create(
                    event_time=fields[0],
                    client_ip=fields[1],
                    session_id=fields[2],
                    request_url=fields[3],
                    identifier=fields[4],
                    filename=fields[5],
                    size=fields[6],
                    user_agent=fields[7],
                    metadata_item_id=md_item.id)
                deduplicate(l_item)

# helper methods without object state

def deduplicate(l_item):
    """Take the created log line and deduplicate any earlier from same person within 30 seconds before"""
    l_item_time = dateutil.parser.parse(l_item.event_time) # why is peewee so crappy? If it's a datetime it should be that type, not a string
    earlier_time = l_item_time - datetime.timedelta(seconds=30)
    if l_item.request_url == 'http://dash-dev.ucop.edu/stash/downloads/file_download/575':
        duptimes = LogItem.select().where(LogItem.event_time.between(earlier_time.isoformat(), l_item_time.isoformat())).execute()
        print(list(duptimes))
        import ipdb; ipdb.set_trace()


    # delete any duplicate requests within 30 seconds earlier by this person from the db
    #(LogItem
    #    .delete()
    #    .where(
    #        LogItem.event_time.between(earlier_time, l_item_time) &
    #        ( LogItem.session_id == l_item.session_id | LogItem.client_ip == l_item.client_ip) &
    #        LogItem.request_url == l_item.request_url)
    #    .execute())





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
