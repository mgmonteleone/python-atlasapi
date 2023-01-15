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
from atlasapi.invoices_pydantic import ApiInvoiceView, ApiRefundView, ApiPaymentView, ApiLineItemView, InvoiceStatus
from json import dumps
from tests import BaseTests
import logging
from time import sleep

logger = logging.getLogger('test')


class InvoiceTests(BaseTests):

    def test_01_get_invoices_for_org(self):
        for each in self.a.Organizations.organizations:
            org_id = each.id
            expected_count = self.a.Invoices.count_for_org_id(org_id)
            invoices = 0
            for each_item in self.a.Invoices.get_all_for_org_id(org_id):
                invoices += 1
                self.assertIsInstance(each_item, ApiInvoiceView)
                self.assertIsInstance(each_item.status_name, InvoiceStatus)
                print(f'Checked invoice # {invoices}')
            print(f'✅Checked {invoices} invoices for org {each.name}')
            print(f'💎Expected {expected_count} invoices!')
            self.assertEqual(expected_count, invoices,
                             "The number of returned invoices should match the expencted number"
                             "of invoices sent in the totalCount response")
            break
    test_01_get_invoices_for_org.basic = True

    def test_02_get_one_invoice_for_org(self):
        for each in self.a.Organizations.organizations:
            org_id = each.id
            for each_item in self.a.Invoices.get_all_for_org_id(org_id):
                invoice_id = each_item.id
                detail_invoice: ApiInvoiceView = self.a.Invoices.get_single_invoice_for_org(org_id=org_id,
                                                                                            invoice_id=invoice_id)
                pprint(detail_invoice)
                break
            break
    test_02_get_one_invoice_for_org.basic = True

    def test_03_get_pending_invoice_for_org(self):
        for each in self.a.Organizations.organizations:
            org_id = each.id
            invoices = 0
            pending_invoice = self.a.Invoices.get_pending_for_org_id(org_id)
            pprint(pending_invoice)
            self.assertIsInstance(pending_invoice, ApiInvoiceView)
            self.assertIsInstance(pending_invoice.status_name, InvoiceStatus)
            for each_line in pending_invoice.line_items:
                self.assertIsInstance(each_line, ApiLineItemView)

            break
    test_03_get_pending_invoice_for_org.basic = True