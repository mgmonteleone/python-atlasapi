from enum import Enum
from isodate import isodatetime
from datetime import datetime
from typing import Optional, List
from humps import camelize
import logging

logger = logging.getLogger(__file__)

class InvoiceStatus(Enum):
    INVOICED = "Invoiced"
    PAID = "Paid"
    PREPAID = "Prepaid"
    FREE = "Free"
    PENDING = "Pending"
    FORGIVEN = "Forgiven"
    FAILED = "Failed"
    CLOSED = "Closed"


class Invoice(object):
    def __init__(self, amount_billed_cents: int, amount_paid_cents: int, created_date: datetime, end_date: datetime,
                id: str, links: List[dict], org_id: str, sales_tax_cents: int, start_date: datetime, starting_balance_cents: int,
                status_name: str, subtotal_cents: int, updated_date: datetime):
        self.id: str = id
        self.amount_billed_cents: int = amount_billed_cents
        self.amount_paid_cents: int = amount_paid_cents
        self.links: List[dict] = links
        self.sales_tax_cents: int = sales_tax_cents
        self.starting_balance_cents: int = starting_balance_cents
        self.status: InvoiceStatus = InvoiceStatus[status_name]
        self.subtotal_cents: int = subtotal_cents
        self.org_id = org_id
        self.created_date: datetime = created_date
        self.end_date: datetime = end_date
        self.start_date: datetime = start_date
        self.updated_date: datetime = updated_date

    @classmethod
    def from_dict(cls, data_dict):
        """
        Creates a Invoice object from a passed dict, in the format of the Atlas API.

        Args:
            data_dict (dict): A dictionary in the format of the Atlas API.

        Returns: None


        """
        try:
            created_date = isodatetime.parse_datetime(data_dict.get('created', None))
        except AttributeError as e:
            logger.error(f"Invalid created date, error was {e}")
            created_date = None

        end_date = isodatetime.parse_datetime(data_dict.get(camelize('end_date'), None))
        start_date = isodatetime.parse_datetime(data_dict.get(camelize('start_date')))
        updated_date = isodatetime.parse_datetime(data_dict.get('updated'))
        amount_billing_cents = data_dict.get(camelize('amount_billing_cents'))
        amount_paid_cents = data_dict.get(camelize('amount_paid_cents'))
        sales_tax_cents = data_dict.get(camelize('sales_tax_cents'))
        starting_balance_cents = data_dict.get(camelize('starting_balance_cents'))
        subtotal_cents = data_dict.get(camelize('subtotal_cents'))
        status_name = data_dict.get('statusName')
        org_id = data_dict.get(camelize('org_id'))
        id = data_dict.get('id')
        links = data_dict.get('links')
        return cls(amount_billing_cents, amount_paid_cents, created_date,end_date,id,links,org_id,sales_tax_cents,start_date,
                   starting_balance_cents,status_name,subtotal_cents,updated_date)




