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
from atlasapi.invoices import Invoice, InvoiceStatus
from json import dumps
from tests import BaseTests
import logging
from time import sleep

logger = logging.getLogger('test')


class InvoiceTests(BaseTests):

    def test_00_get_invoices_for_org(self):
        for each in self.a.Organizations.organizations:
            org_id = each.id
            expected_count = self.a.Invoices.count_for_org_id(org_id)
            invoices = 0
            for each_item in self.a.Invoices.get_all_for_org_id(org_id):
                invoices += 1
                self.assertIsInstance(each_item,Invoice)
                self.assertIsInstance(each_item.status, InvoiceStatus)
                self.assertIsInstance(each_item.updated_date, datetime.datetime)
                self.assertIsInstance(each_item.created_date, datetime.datetime)
                self.assertIsInstance(each_item.start_date, datetime.datetime)
                self.assertIsInstance(each_item.amount_paid_cents, int)
                print(f'Checked invoice # {invoices}')
            print(f'✅Checked {invoices} invoices for org {each.name}')
            print(f'💎Expected {expected_count} invoices!')
            self.assertEqual(expected_count,invoices,"The number of returned invoices should match the expencted number"
                                                     "of invoices sent in the totalCount response")
            break

