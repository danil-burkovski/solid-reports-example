from datetime import datetime
from typing import Optional

import pydantic


class Transaction(pydantic.BaseModel):
    status: str
    method: str
    amount: int
    currency: str
    type: str


class APMOrder(pydantic.BaseModel):
    order_id: str
    amount: int
    currency: str
    status: str
    method: str
    created_at: datetime
    updated_at: datetime
    customer_email: str
    ip_address: str
    transactions: list[Transaction]
    order_description: Optional[str]
    customer_account_id: str
    processing_amount: Optional[str]
    processing_currency: Optional[str]
