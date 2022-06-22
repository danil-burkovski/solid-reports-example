from datetime import datetime
from typing import Optional

import pydantic


class Flow(pydantic.BaseModel):
    id: str
    amount: int
    dispute_amount: Optional[int]
    type: str
    status: str
    date: datetime
    settlement_date: datetime
    created_at: datetime
    updated_at: datetime
    deadline_date: Optional[datetime]
    arn_code: Optional[str]
    currency: str
    finance_fee_amount: Optional[int]
    finance_fee_currency: Optional[str]


class Chargeback(pydantic.BaseModel):
    id: str
    created_at: datetime
    dispute_date: datetime
    settlement_date: datetime
    status: str
    type: str
    amount: int
    currency: str
    reason_group: str
    reason_code: str
    reason_description: str
    finance_fee_amount: Optional[int]
    finance_fee_currency: Optional[str]
    flows: list[Flow]


class ChargebackOrder(pydantic.BaseModel):
    order_id: str
    status: str
    type: str
    amount: int
    currency: str
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
    chargebacks: list[Chargeback]
