# YEAR_MONTH="2018-05" LOG_NAME_PATTERN="test/fixtures/counter_(yyyy-mm-dd).log"
# UPLOAD_TO_HUB=False SIMULATE_DATE="2018-05-02" ./main.py

import os
import json
# import sys
# these two are a hack to get config to import right when run from the __name__ == '__main__' hack
# cwd = os.getcwd()
# sys.path.insert(0, cwd)

# override some stuff in environment variables to test
# os.environ["CONFIG_FILE"] = "test/config/config.yaml"
# os.environ["PROCESSING_DATABASE"] = 'db/test_only_db.sqlite3'
# os.environ["END_TIME"] = '2018-03-14 00:00:00'

import unittest
# from unittest.mock import patch
import main

class TestMain(unittest.TestCase):
    def setUp(self):
        os.environ["YEAR_MONTH"] = "2018-05"
        os.environ["LOG_NAME_PATTERN"] = 'test/fixtures/counter_(yyyy-mm-dd).log'
        os.environ["UPLOAD_TO_HUB"] = 'False'
        os.environ["SIMULATE_DATE"] = "2018-05-02"
        if os.path.exists('state/statefile.json'):
            os.rename('state/statefile.json', 'state/saved_state.json')
        if os.path.exists('state/counter_db_2018-05.sqlite3'):
            os.rename('state/counter_db_2018-05.sqlite3', 'state/moved_db.sqlite3')
        main.test_mode = True

    def tearDown(self):
        del os.environ['YEAR_MONTH']
        del os.environ['LOG_NAME_PATTERN']
        del os.environ['UPLOAD_TO_HUB']
        del os.environ['SIMULATE_DATE']
        if os.path.exists('state/statefile.json'):
            os.remove('state/statefile.json')
        if os.path.exists('state/counter_db_2018-05.sqlite3'):
            os.remove('state/counter_db_2018-05.sqlite3')
        if os.path.exists('state/saved_state.json'):
            os.rename('state/saved_state.json', 'state/statefile.json')
        if os.path.exists('state/moved_db.sqlite3'):
            os.rename('state/moved_db.sqlite3', 'state/counter_db_2018-05.sqlite3')
        main.test_mode = False

    def test_main(self):
        main.main()
        with open('tmp/test_out.json') as f:
            data = json.load(f)
            self.assertEqual(data['report-header']['report-name'], 'dataset report')
            self.assertEqual(data['report-header']['release'], 'rd1')
            self.assertEqual(data['report-header']['created-by'], 'Dryad')
            self.assertEqual(data['report-header']['reporting-period']['begin-date'], '2018-05-01')
            self.assertEqual(data['report-header']['reporting-period']['end-date'], '2018-05-01')
            self.assertEqual(len(data['report-datasets']), 1)
            self.assertIn('Toward learned chemical perception', data['report-datasets'][0]['dataset-title'])
            self.assertEqual(len(data['report-datasets'][0]['dataset-contributors']), 8)
            self.assertEqual(data['report-datasets'][0]['dataset-id'][0]['value'], '10.7280/D1CD4C')
            self.assertEqual(data['report-datasets'][0]['data-type'], 'dataset')
            self.assertEqual(data['report-datasets'][0]['yop'], '2018')
            perf = data['report-datasets'][0]['performance']
            self.assertEqual(perf[0]['period']['begin-date'], '2018-05-01')
            self.assertEqual(perf[0]['period']['end-date'], '2018-05-31')
            item = perf[0]['instance']
            self.assertEqual(item[0]['access-method'], 'regular')
            self.assertEqual(item[0]['metric-type'], 'total-dataset-investigations')
            self.assertEqual(item[0]['count'], 2)
            self.assertEqual(item[0]['country-counts'], {'us': 2})
            self.assertEqual(len(item), 2)
        print('hi')


if __name__ == '__main__':
    unittest.main()