from models import *
from peewee import *

class IdStat():
    """The stats for a DOI identifier"""

    def __init__(self, identifier, start_sql, end_sql):
        self.identifier = identifier
        self.start_sql = start_sql
        self.end_sql = end_sql
        self.countries = LogItem.select(LogItem.country) \
                .distinct() \
                .where((LogItem.is_robot == False) & (LogItem.identifier == self.identifier) &
                    LogItem.event_time.between(self.start_sql, self.end_sql))
        self.countries = [x.country for x in self.countries]

    def stats():
        pass
