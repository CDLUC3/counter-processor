import os
import sys
# these two are a hack to get config to import right when run from the __name__ == '__main__' hack
cwd = os.getcwd()
sys.path.insert(0, cwd)

# override some stuff in environment variables to test
os.environ["CONFIG_FILE"] = "test/config/config.yaml"
os.environ["PROCESSING_DATABASE"] = 'db/test_only_db.sqlite3'
os.environ["END_TIME"] = '2018-03-14 00:00:00'

import unittest
# from unittest.mock import patch
import config
import re

class TestConfig(unittest.TestCase):

    def test_yaml_set(self):
        self.assertEqual(config.platform, 'Dashlet')
        self.assertEqual(config.output_file, 'tmp/test_run.tsv')

    def test_env_set(self):
        self.assertEqual(config.processing_database, 'db/test_only_db.sqlite3')

    def test_dates_transformed_from_string(self):
        self.assertEqual(config.end_sql(), '2018-03-14T00:00:00')

    def test_start_time(self):
        self.assertEqual(config.start_sql(), '2018-02-01T00:00:00')

    def test_regex_for_type(self):
        self.assertEqual(config.hit_type_regexp()['investigation'], re.compile('investo|inclumpto'))

if __name__ == '__main__':
    unittest.main()
