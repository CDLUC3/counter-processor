import config
from models import *
from peewee import *
#import ipdb; ipdb.set_trace()

class FacetedStat():
    """The stats for a combination of facets for a DOI identifier
    access_method is either 'human' or 'machine' """

    def __init__(self, identifier, access_method = 'human'):
        self.identifier = identifier
        self.access_method = access_method
        self.__total_investigations = None
        self.__unique_investigations = None
        self.__total_requests = None
        self.__unique_requests = None
        self.__total_requests_size = None
        self.__unique_requests_size = None


    def total_investigations(self):
        if self.__total_investigations is None:
            self.__total_investigations = self.total(['investigation', 'request'])
        return self.__total_investigations

    def unique_investigations(self):
        if self.__unique_investigations is None:
            self.__unique_investigations = self.unique(['investigation', 'request'])
        return self.__unique_investigations

    def total_requests(self):
        if self.__total_requests is None:
            self.__total_requests = self.total(['request'])
        return self.__total_requests

    def unique_requests(self):
        if self.__unique_requests is None:
            self.__unique_requests = self.unique(['request'])
        return self.__unique_requests

    """This will total the numbers for a stat across all countries in array like
    [{'country': 'US', 'ct': 3}, {'country': 'UK', 'ct': 2}] and return 5 for this example"""
    @staticmethod
    def sum(arr, field):
        my_total = 0
        for i in arr:
            my_total += i[field]
        return my_total

    """ This gives a grouped count and volume by country.  example: item[0]['country'], item[0]['ct'],  item[0]['vol'],
    item[1]['country'], etc"""
    def total(self, hit_type):
        my_items =  LogItem.select(LogItem.country, fn.COUNT().alias('ct'), fn.SUM(LogItem.size).alias('vol')) \
                .where((LogItem.is_robot == False) & (LogItem.identifier == self.identifier) &
                    LogItem.event_time.between(config.Config().start_sql(), config.Config().end_sql()) &
                    (LogItem.is_machine == self.is_machine()) &
                    (LogItem.hit_type << hit_type) ) \
                .group_by(LogItem.country)
        return self.fix_countries([ {'country': x.country, 'ct': x.ct, 'vol': x.vol} for x in my_items ])

    """ This gives a grouped count by country.  example: item[0]['country'], item[0]['ct'],  item[0]['vol'],
    item[1]['country'], etc"""
    def unique(self, hit_type):
        # this is extra complicated because we have to eliminate duplicates with distinct and then can't
        # group by country which is a different column.  Maybe could do with some kind of subquery, but
        # it's not obvious exactly how except by the calc_session_id which isn't really appropriate id.

        # get the total hits, which groups by country
        country_dicts = self.total(hit_type)

        # now do another query distinct session_ids for each country
        #  - robots: false, identifier: current, between_dates,  country: current_country:, machine: machine_status, hit_type:
        for i in country_dicts:
            i['ct'] = LogItem.select(LogItem.calc_session_id).distinct() \
                .where((LogItem.is_robot == False) & (LogItem.identifier == self.identifier) &
                    LogItem.event_time.between(config.Config().start_sql(), config.Config().end_sql()) &
                    (LogItem.country == i['country'].upper()) &
                    (LogItem.is_machine == self.is_machine()) &
                    (LogItem.hit_type << hit_type) ) \
                .count()

            # this feels weird, because I'm including size, but the size for the same url and same dataset should stay the same if it hasn't changed
            # don't need identifier in there because it's only for one identifier
            # this is a working subquery as an example in sqlite
            # SELECT SUM(subquery.size) as my_total
            # FROM (SELECT request_url, size FROM logitem WHERE request_url = 'http://dash.ucop.edu/stash/downloads/file_download/16783') subquery

            # select (session_id, request, size).distinct
            # robot: false, identifier: id, event time, country, machine_type, hit_type:
            subquery = ( LogItem.select(LogItem.calc_session_id, LogItem.request_url, LogItem.size).distinct() \
                .where((LogItem.is_robot == False) & (LogItem.identifier == self.identifier) &
                    LogItem.event_time.between(config.Config().start_sql(), config.Config().end_sql()) &
                    (LogItem.country == i['country'].upper()) &
                    (LogItem.is_machine == self.is_machine()) &
                    (LogItem.hit_type << hit_type) ) )
                    # .alias('subquery')

            # Can't seem to get PoS Peewee ORM to allow a select based on a subquery in the from clause like
            # my_ct = ( subquery.select( fn.SUM(subquery.size)).alias('total_size') )
            my_volume = 0
            for row in subquery:
                if row.size is not None:
                    my_volume += row.size
            i['vol'] = my_volume

        return self.fix_countries(country_dicts)

    # These are helper functions
    def is_machine(self):
        if self.access_method == 'human':
            return False
        else:
            return True

    # DCS requested country codes in lowercase
    def fix_countries(self, my_array):
        for item in my_array:
            if not item['country']:
                item['country'] = 'unknown'
            else:
                item['country'] = item['country'].lower()
        return my_array
