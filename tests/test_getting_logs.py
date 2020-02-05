"""
Unit tests for getting logs Windows


"""
from pprint import pprint
from os import environ, getenv
from atlasapi.atlas import Atlas
from json import dumps
from tests import BaseTests
import logging
from time import sleep
from atlasapi.lib import AtlasLogNames, LogLine
from atlasapi.specs import HostLogFile
from io import BytesIO
from datetime import datetime, timedelta

logger = logging.getLogger('test')


class LogsTests(BaseTests):

    def test_00_test_retrieve_log_lines(self):
        atlas: Atlas = self.a
        atlas.Hosts.fill_host_list()
        test_host = atlas.Hosts.host_list[0]
        print(f'Will get a mongod log for {test_host.hostname}')
        out = atlas.Hosts.get_loglines_for_host(host_obj=test_host, log_name=AtlasLogNames.MONGODB)
        counter = 0
        for each in out:
            if counter < 3:
                self.assertIsInstance(each, LogLine)
            else:
                break

    def test_01_test_retrieve_log(self):
        atlas: Atlas = self.a
        atlas.Hosts.fill_host_list()
        test_host = atlas.Hosts.host_list[0]
        print(f'Will get a mongod log for {test_host.hostname}')
        out = atlas.Hosts.get_log_for_host(host_obj=test_host, log_name=AtlasLogNames.MONGODB)
        self.assertIsInstance(out, BytesIO)
        self.assertGreater(out.tell(), 1000)

    def test_02_test_retrieve_log_to_date(self):
        atlas: Atlas = self.a
        start_date = datetime(year=2020, month=2, day=3)
        atlas.Hosts.fill_host_list()
        test_host = atlas.Hosts.host_list[0]
        print(f'Will get a mongod log for {test_host.hostname}')
        out = atlas.Hosts.get_log_for_host(host_obj=test_host, log_name=AtlasLogNames.MONGODB, date_from=start_date)
        self.assertIsInstance(out, BytesIO)
        self.assertGreater(out.tell(), 1000)

#    def test_03_test_retrieve_logs_for_project(self):
#        atlas: Atlas = self.a
#        atlas.Hosts.fill_host_list()
#        host_list = list(atlas.Hosts.host_list)
#
#        print(f'Will get a mongod logs for {len(host_list)} hosts.')
#        out = atlas.Hosts.get_logs_for_project(log_name=AtlasLogNames.MONGODB)
#        for each in out:
#            print(f'Received a log for {each.hostname}, of type {each.log_files[0].log_name}, lenght: {each.log_files[0].log_file_binary.tell()}')
#            self.assertIsInstance(each.log_files[0], HostLogFile)
#            self.assertGreater(each.log_files[0].log_file_binary.tell(), 1000)
