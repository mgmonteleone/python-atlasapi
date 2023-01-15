"""
Nose2 Unit Tests for the clusters module.


"""
import datetime
from pprint import pprint
from os import environ, getenv
from atlasapi.atlas import Atlas
from atlasapi.projects import Project, ProjectSettings
from atlasapi.teams import TeamRoles
from atlasapi.atlas_users import AtlasUser
from atlasapi.serverless_pydantic import ServerlessCluster
from json import dumps
from tests import BaseTests
import logging
from time import sleep

logger = logging.getLogger('test')


class InvoiceTests(BaseTests):

    def test_00_get_count_for_group(self):
        count = self.a.Serverless.count_for_group_id(group_id=self.GROUP_ID)
        print(f'✅ There are {count} serverless instances in the project/group.')
        self.assertIsInstance(count,int, "Instance count must be a non-negative int.")

    def test_01_get_instances_for_project(self):
        for each_item in self.a.Serverless.get_all_for_project(group_id=self.GROUP_ID):
            pprint(each_item)
            # self.assertIsInstance(each_item, ApiInvoiceView)
            # self.assertIsInstance(each_item.status_name, InvoiceStatus)
            # print(f'Checked invoice # {invoices}')
        # print(f'✅Checked {invoices} invoices for org {each.name}')
        # print(f'💎Expected {expected_count} invoices!')

    test_01_get_instances_for_project.basic = True

