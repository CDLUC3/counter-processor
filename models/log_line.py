from models import *
from peewee import *
#import ipdb; ipdb.set_trace()

class LogLine():
    """A class to handle log lines"""

    def __init__(self, line):
        self.line = line.strip()

# Fields: event_time	client_ip	session_id	request_url	identifier	filename	size	user-agent[7]
# title[8]	publisher	publisher_id	authors	publication_date	version	other_ids	target_url	publication_year

    def populate(self):
                if self.line.startswith('#'): return
                fields = [( None if x == '' or x == '-' or x == '????' else x) for x in self.line.split("\t")]

                md_item = find_or_create_metadata(fields)

                log_item = LogItem.create(
                    event_time=fields[0],
                    client_ip=fields[1],
                    session_id=fields[2],
                    request_url=fields[3],
                    identifier=fields[4],
                    filename=fields[5],
                    size=fields[6],
                    user_agent=fields[7],
                    metadata_item_id=md_item.id) # TODO: fix this up.

# helper methods without object state
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
        return mi
    else:
        return mis[0]

def create_authors(md_item, auth_field):
    pass
