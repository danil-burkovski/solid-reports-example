from datetime import datetime
from typing import Optional

import pydantic


class Card(pydantic.BaseModel):
    bank: Optional[str]
    bin: str
    card_holder: Optional[str]
    brand: Optional[str]
    country: Optional[str]
    number: str
    card_exp_year: int
    card_exp_month: str
    card_type: Optional[str]


class BillingDetails(pydantic.BaseModel):
    address: str
    zip: str
    country: str
    city: str
    state: str


class Transaction(pydantic.BaseModel):
    id: str
    operation: str
    status: str
    descriptor: Optional[str]
    amount: int
    currency: str
    refund_reason: Optional[str]
    refund_reason_code: Optional[str]
    created_at: datetime
    updated_at: datetime
    finance_fee_amount: int
    finance_fee_currency: str
    card: Optional[Card]
    billing_details: Optional[BillingDetails]


class CardOrder(pydantic.BaseModel):
    order_id: str
    status: str
    type: str
    amount: int
    currency: str
    processing_amount: Optional[int]
    processing_currency: Optional[str]
    traffic_source: Optional[str]
    order_description: str
    customer_account_id: str
    customer_email: str
    customer_first_name: Optional[str]
    customer_last_name: Optional[str]
    geo_country: str
    ip_address: str
    error_code: Optional[str]
    platform: str
    fraudulent: bool
    is_secured: bool
    created_at: datetime
    updated_at: datetime
    transactions: list[Transaction]
