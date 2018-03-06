import config
from models import *
from peewee import *
from .report import Report
import csv
import datetime
import dateutil.parser
#import ipdb; ipdb.set_trace()

HEAD_ROW = ['Dataset_Title', 'Publisher', 'Publisher_ID', 'Platform', 'Creators',
    'Publication_Date', 'Dataset_Version', 'DOI', 'Other_ID', 'URI', 'YOP', 'Access_Method',
    'Metric_Type', 'Country', 'Reporting_Period_Total',	'Reporting_Period_Volume']

# these are the functions to use on the FacetStat class instances
CALCULATOR_FUNCTIONS = \
        {   'Total_Dataset_Investigations': ['total_investigations', ''],
            'Unique_Dataset_Investigations': ['unique_investigations', ''],
            'Total_Dataset_Requests': ['total_requests', 'total_requests_size'],
            'Unique_Dataset_Requests': ['unique_requests', 'unique_requests_size'] }

ACCESS_METHOD_TERMS = {'human': 'Regular', 'machine': 'Machine'}

class TsvReport(Report):
    """Make a TSV report from the generic data report object this inherits from"""

    def output(self):
        with open(config.output_file, 'w', newline='\n') as tsvfile:
            writer = csv.writer(tsvfile, delimiter='\t')

            self.output_header_section(writer)
            self.output_header_row(writer)

            # output table rows
            for i in self.iterate_facet_stats(): # from the parent report
                self.output_rows(i, writer)
                #self.printrr(i)

    def output_header_section(self, w):
        rows = \
            [   ['Report_Name',         'Dataset Master Report'],
                ['Report_ID',           'DSR' ],
                ['Release',             'RD1'],
                ['Exceptions',          ''],
                ['Reporting_Period',    f'{config.start_time.isoformat()} to {config.end_time.isoformat()}'],
                ['Created',             self.just_date(datetime.datetime.now())],
                ['Created_By',          'Dash'],
                ['']
            ]
        for row in rows:
            w.writerow(row)

    def output_header_row(self, w):
        w.writerow(HEAD_ROW)

    def output_rows(self, facet_stats, w):
        """ Output the related set of stats for this identifier and current facets """
        print( f'Writing stats for {facet_stats.identifier}')
        meta = self.find_metadata_by_identifier(facet_stats.identifier)
        creators = ';'.join([ a.author_name for a in meta.author ])
        base_meta = [meta.title, meta.publisher, 'TODO', config.platform, creators,
            self.just_date(meta.publication_date), '', meta.identifier, 'TODO', meta.target_url, meta.publication_year ]

        for name, funcs in CALCULATOR_FUNCTIONS.items():
            if getattr(facet_stats, funcs[0])() < 1: continue
            end_line = [self.access_term(facet_stats.access_method), name, facet_stats.country_code,
                getattr(facet_stats, funcs[0])(),
                ('' if funcs[1] == '' else getattr(facet_stats, funcs[1])())]
            w.writerow(base_meta + end_line)

    def just_date(self, dt):
        if isinstance(dt, ''.__class__): # if this is a string, make it into a datetime, sqlite is poo
            dt = dateutil.parser.parse(dt)
        return dt.strftime("%Y-%m-%d")

    def access_term(self, t):
        return ACCESS_METHOD_TERMS[t]
