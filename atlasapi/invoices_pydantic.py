from __future__ import annotations

from datetime import datetime
from enum import Enum
from ipaddress import IPv4Address
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, EmailStr, Extra, Field, confloat, conint, constr


class InvoiceStatus(Enum):
    INVOICED = "INVOICED"
    PAID = "PAID"
    PREPAID = "PREPAID"
    FREE = "FREE"
    PENDING = "PENDING"
    FORGIVEN = "FORGIVEN"
    FAILED = "FAILED"
    CLOSED = "CLOSED"




class Link(BaseModel):
    href: Optional[str] = Field(
        None,
        description='Uniform Resource Locator (URL) that points another API resource to which this response has some relationship. This URL often begins with `https://mms.mongodb.com`.',
        example='https://mms.mongodb.com/api/atlas/v1.0/groups/{groupId}/serverless/{instanceName1}/backup/snapshots',
    )
    rel: Optional[str] = Field(
        None,
        description='Uniform Resource Locator (URL) that defines the semantic relationship between this resource and another API resource. This URL often begins with `https://mms.mongodb.com`.',
        example='https://mms.mongodb.com/snapshots',
    )


class LinkAtlas(BaseModel):
    href: Optional[str] = Field(
        None,
        description='Uniform Resource Locator (URL) that points another API resource to which this response has some relationship. This URL often begins with `https://mms.mongodb.com`.',
        example='https://mms.mongodb.com/api/atlas/v1.0/groups/{groupId}/serverless/{instanceName1}/backup/snapshots',
    )
    rel: Optional[str] = Field(
        None,
        description='Uniform Resource Locator (URL) that defines the semantic relationship between this resource and another API resource. This URL often begins with `https://mms.mongodb.com`.',
        example='https://mms.mongodb.com/snapshots',
    )


class ApiPaymentView(BaseModel):
    """
    Funds transferred to MongoDB to cover the specified service in this invoice.
    """

    amount_billed_cents: Optional[int] = Field(
        None,
        alias='amountBilledCents',
        description='Sum of services that the specified organization consumed in the period covered in this invoice. This parameter expresses its value in cents (100ths of one US Dollar) and calculates its value as **subtotalCents** + **salesTaxCents** - **startingBalanceCents**.',
    )
    amount_paid_cents: Optional[int] = Field(
        None,
        alias='amountPaidCents',
        description='Sum that the specified organization paid toward the associated invoice. This parameter expresses its value in cents (100ths of one US Dollar).',
    )
    created: Optional[datetime] = Field(
        None,
        description='Date and time when the customer made this payment attempt. This parameter expresses its value in the ISO 8601 timestamp format in UTC.',
    )
    id: Optional[
        constr(regex=r'^([a-f0-9]{24})$', min_length=24, max_length=24)
    ] = Field(
        None,
        description='Unique 24-hexadecimal digit string that identifies this payment toward the associated invoice.',
        example='6fb669797183aa180bc5c09a',
    )
    sales_tax_cents: Optional[int] = Field(
        None,
        alias='salesTaxCents',
        description='Sum of sales tax applied to this invoice. This parameter expresses its value in cents (100ths of one US Dollar).',
    )
    status_name: Optional[str] = Field(
        None,
        alias='statusName',
        description="Phase of payment processing for the associated invoice when you made this request.\n\nThese phases include:\n\n| Phase Value | Reason |\n|---|---|\n| `CANCELLED` | Customer or MongoDB cancelled the payment. |\n| `ERROR` | Issue arose when attempting to complete payment. |\n| `FAILED` | MongoDB tried to charge the credit card without success. |\n| `FAILED_AUTHENTICATION` | Strong Customer Authentication has failed. Confirm that your payment method is authenticated. |\n| `FORGIVEN` | Customer initiated payment which MongoDB later forgave. |\n| `INVOICED` | MongoDB issued an invoice that included this line item. |\n| `NEW` | Customer provided a method of payment, but MongoDB hasn't tried to charge the credit card. |\n| `PAID` | Customer submitted a successful payment. |\n| `PARTIAL_PAID` | Customer paid for part of this line item. |\n",
    )
    subtotal_cents: Optional[int] = Field(
        None,
        alias='subtotalCents',
        description='Sum of all positive invoice line items contained in this invoice. This parameter expresses its value in cents (100ths of one US Dollar).',
    )
    updated: Optional[datetime] = Field(
        None,
        description='Date and time when the customer made an update to this payment attempt. This parameter expresses its value in the ISO 8601 timestamp format in UTC.',
    )


class ApiRefundView(BaseModel):
    """
    One payment that MongoDB returned to the organization for this invoice.
    """

    amount_cents: Optional[int] = Field(
        None,
        alias='amountCents',
        description='Sum of the funds returned to the specified organization expressed in cents (100th of US Dollar).',
    )
    created: Optional[datetime] = Field(
        None,
        description='Date and time when MongoDB Cloud created this refund. This parameter expresses its value in the ISO 8601 timestamp format in UTC.',
    )
    payment_id: Optional[
        constr(regex=r'^([a-f0-9]{24})$', min_length=24, max_length=24)
    ] = Field(
        None,
        alias='paymentId',
        description='Unique 24-hexadecimal digit string that identifies the payment that the organization had made.',
    )
    reason: Optional[str] = Field(
        None,
        description='Justification that MongoDB accepted to return funds to the organization.',
    )


class ApiLineItemView(BaseModel):
    """
    One service included in this invoice.
    """

    cluster_name: Optional[
        constr(
            regex=r'^([a-zA-Z0-9]([a-zA-Z0-9-]){0,21}(?<!-)([\w]{0,42}))$',
            min_length=1,
            max_length=64,
        )
    ] = Field(
        None,
        alias='clusterName',
        description='Human-readable label that identifies the cluster that incurred the charge.',
    )
    created: Optional[datetime] = Field(
        None,
        description='Date and time when MongoDB Cloud created this line item. This parameter expresses its value in the ISO 8601 timestamp format in UTC.',
    )
    discount_cents: Optional[int] = Field(
        None,
        alias='discountCents',
        description='Sum by which MongoDB discounted this line item. MongoDB Cloud expresses this value in cents (100ths of one US Dollar). The resource returns this parameter when a discount applies.',
    )
    end_date: Optional[datetime] = Field(
        None,
        alias='endDate',
        description='Date and time when when MongoDB Cloud finished charging for this line item. This parameter expresses its value in the ISO 8601 timestamp format in UTC.',
    )
    group_id: Optional[
        constr(regex=r'^([a-f0-9]{24})$', min_length=24, max_length=24)
    ] = Field(
        None,
        alias='groupId',
        description='Unique 24-hexadecimal digit string that identifies the project associated to this line item.',
        example='32b6e34b3d91647abb20e7b8',
    )
    group_name: Optional[str] = Field(
        None,
        alias='groupName',
        description='Human-readable label that identifies the project.',
    )
    note: Optional[str] = Field(
        None, description='Comment that applies to this line item.'
    )
    percent_discount: Optional[float] = Field(
        None,
        alias='percentDiscount',
        description='Percentage by which MongoDB discounted this line item. The resource returns this parameter when a discount applies.',
    )
    quantity: Optional[float] = Field(
        None,
        description='Number of units included for the line item. These can be expressions of storage (GB), time (hours), or other units.',
    )
    sku: Optional[str] = Field(
        None,
        description='Human-readable description of the service that this line item provided. This Stock Keeping Unit (SKU) could be the instance type, a support charge, advanced security, or another service.',
    )
    start_date: Optional[datetime] = Field(
        None,
        alias='startDate',
        description='Date and time when MongoDB Cloud began charging for this line item. This parameter expresses its value in the ISO 8601 timestamp format in UTC.',
    )
    stitch_app_name: Optional[str] = Field(
        None,
        alias='stitchAppName',
        description='Human-readable label that identifies the Atlas App Service associated with this line item.',
    )
    tier_lower_bound: Optional[float] = Field(
        None,
        alias='tierLowerBound',
        description='Lower bound for usage amount range in current SKU tier. \n\n**NOTE**: **lineItems[n].tierLowerBound** appears only if your **lineItems[n].sku** is tiered.',
    )
    tier_upper_bound: Optional[float] = Field(
        None,
        alias='tierUpperBound',
        description='Upper bound for usage amount range in current SKU tier. \n\n**NOTE**: **lineItems[n].tierUpperBound** appears only if your **lineItems[n].sku** is tiered.',
    )
    total_price_cents: Optional[int] = Field(
        None,
        alias='totalPriceCents',
        description='Sum of the cost set for this line item. MongoDB Cloud expresses this value in cents (100ths of one US Dollar) and calculates this value as **unitPriceDollars** × **quantity** × 100.',
    )
    unit: Optional[str] = Field(
        None,
        description='Element used to express what **quantity** this line item measures. This value can be elements of time, storage capacity, and the like.',
    )
    unit_price_dollars: Optional[float] = Field(
        None,
        alias='unitPriceDollars',
        description='Value per **unit** for this line item expressed in US Dollars.',
    )


class ApiInvoiceView(BaseModel):
    amount_billed_cents: Optional[int] = Field(
        None,
        alias='amountBilledCents',
        description='Sum of services that the specified organization consumed in the period covered in this invoice. This parameter expresses its value in cents (100ths of one US Dollar) and calculates its value as **subtotalCents** + **salesTaxCents** - **startingBalanceCents**.',
    )
    amount_paid_cents: Optional[int] = Field(
        None,
        alias='amountPaidCents',
        description='Sum that the specified organization paid toward this invoice. This parameter expresses its value in cents (100ths of one US Dollar).',
    )
    created: Optional[datetime] = Field(
        None,
        description='Date and time when MongoDB Cloud created this invoice. This parameter expresses its value in the ISO 8601 timestamp format in UTC.',
    )
    credits_cents: Optional[int] = Field(
        None,
        alias='creditsCents',
        description='Sum that MongoDB credited the specified organization toward this invoice. This parameter expresses its value in cents (100ths of one US Dollar).',
    )
    end_date: Optional[datetime] = Field(
        None,
        alias='endDate',
        description='Date and time when MongoDB Cloud finished the billing period that this invoice covers. This parameter expresses its value in the ISO 8601 timestamp format in UTC.',
    )
    group_id: Optional[
        constr(regex=r'^([a-f0-9]{24})$', min_length=24, max_length=24)
    ] = Field(
        None,
        alias='groupId',
        description="Unique 24-hexadecimal digit string that identifies the project associated to this invoice. This identifying string doesn't appear on all invoices.",
        example='32b6e34b3d91647abb20e7b8',
    )
    id: Optional[
        constr(regex=r'^([a-f0-9]{24})$', min_length=24, max_length=24)
    ] = Field(
        None,
        description='Unique 24-hexadecimal digit string that identifies the invoice submitted to the specified organization. Charges typically post the next day.',
        example='217a865625b2bad3b9a1e93d',
    )
    line_items: Optional[List[ApiLineItemView]] = Field(
        None,
        alias='lineItems',
        description='List that contains individual services included in this invoice.',
    )
    links: List[Link] = Field(
        ...,
        description='List of one or more Uniform Resource Locators (URLs) that point to API sub-resources, related API resources, or both. RFC 5988 outlines these relationships.',
    )
    org_id: Optional[
        constr(regex=r'^([a-f0-9]{24})$', min_length=24, max_length=24)
    ] = Field(
        None,
        alias='orgId',
        description='Unique 24-hexadecimal digit string that identifies the organization charged for services consumed from MongoDB Cloud.',
        example='4888442a3354817a7320eb61',
    )
    payments: Optional[List[ApiPaymentView]] = Field(
        None,
        description='List that contains funds transferred to MongoDB to cover the specified service noted in this invoice.',
    )
    refunds: Optional[List[ApiRefundView]] = Field(
        None,
        description='List that contains payments that MongoDB returned to the organization for this invoice.',
    )
    sales_tax_cents: Optional[int] = Field(
        None,
        alias='salesTaxCents',
        description='Sum of sales tax applied to this invoice. This parameter expresses its value in cents (100ths of one US Dollar).',
    )
    start_date: Optional[datetime] = Field(
        None,
        alias='startDate',
        description='Date and time when MongoDB Cloud began the billing period that this invoice covers. This parameter expresses its value in the ISO 8601 timestamp format in UTC.',
    )
    starting_balance_cents: Optional[int] = Field(
        None,
        alias='startingBalanceCents',
        description='Sum that the specified organization owed to MongoDB when MongoDB issued this invoice. This parameter expresses its value in US Dollars.',
    )
    status_name: Optional[InvoiceStatus] = Field(
        None,
        alias='statusName',
        description="Phase of payment processing in which this invoice exists when you made this request. Accepted phases include:\n\n| Phase Value | Reason |\n|---|---|\n| CLOSED | MongoDB finalized all charges in the billing cycle but has yet to charge the customer. |\n| FAILED | MongoDB attempted to charge the provided credit card but charge for that amount failed. |\n| FORGIVEN | Customer initiated payment which MongoDB later forgave. |\n| FREE | All charges totalled zero so the customer won't be charged. |\n| INVOICED | MongoDB handled these charges using elastic invoicing. |\n| PAID | MongoDB succeeded in charging the provided credit card. |\n| PENDING | Invoice includes charges for the current billing cycle. |\n| PREPAID | Customer has a pre-paid plan so they won't be charged. |\n",
    )
    subtotal_cents: Optional[int] = Field(
        None,
        alias='subtotalCents',
        description='Sum of all positive invoice line items contained in this invoice. This parameter expresses its value in cents (100ths of one US Dollar).',
    )
    updated: Optional[datetime] = Field(
        None,
        description='Date and time when MongoDB Cloud last updated the value of this payment. This parameter expresses its value in the ISO 8601 timestamp format in UTC.',
    )
