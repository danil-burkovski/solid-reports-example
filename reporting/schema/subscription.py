from datetime import datetime, timedelta
from typing import Any, Optional

import pydantic
from pydantic import validator


class Customer(pydantic.BaseModel):
    customer_account_id: str
    customer_email: str


class Product(pydantic.BaseModel):
    id: str
    name: str
    amount: int
    currency: str
    trial: bool
    payment_action: Optional[str]
    trial_period: Optional[timedelta]

    @validator("trial_period")
    def parse_timedelta(cls, v: timedelta) -> timedelta:
        # raw trial_period is in minutes but pydantic parses them as seconds
        return timedelta(minutes=v.seconds)


class Order(pydantic.BaseModel):
    id: str
    status: str
    amount: int
    created_at: datetime
    processed_at: datetime
    failed_reason: Optional[str]
    operation: str
    retry_attempt: Optional[str]


class Invoice(pydantic.BaseModel):
    id: str
    amount: int
    status: str
    created_at: datetime
    updated_at: datetime
    billing_period_started_at: Optional[datetime]
    billing_period_ended_at: Optional[datetime]
    subscription_term_number: int
    orders: list[Order]

    @classmethod
    def from_dict(cls, raw_invoice: dict[str, Any]):
        raw_orders = raw_invoice.pop("orders").values()
        orders = [Order(**raw_order) for raw_order in raw_orders]
        return cls(**raw_invoice, orders=orders)


class Subscription(pydantic.BaseModel):
    id: str
    status: str
    started_at: datetime
    expired_at: datetime
    next_charge_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    trial: bool
    cancel_code: Optional[str]
    cancel_message: Optional[str]
    payment_type: str
    customer: Customer
    product: Product
    invoices: list[Invoice]

    @classmethod
    def from_dict(cls, raw_subscription: dict[str, Any]):
        raw_invoices = raw_subscription.pop("invoices").values()
        invoices = [Invoice.from_dict(raw_invoice) for raw_invoice in raw_invoices]
        return cls(**raw_subscription, invoices=invoices)

    @classmethod
    def from_kwargs(cls, **kwargs: dict[str, Any]):
        return cls.from_dict(kwargs)
