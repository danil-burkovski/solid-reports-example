from datetime import datetime

import pydantic


class PayPalDispute(pydantic.BaseModel):
    dispute_id: str
    order_id: str
    dispute_amount: int
    dispute_currency: str
    reason: str
    status: str
    dispute_life_cycle_stage: str
    dispute_channel: str
    dispute_create_time: datetime
    dispute_update_time: datetime
    customer_account_id: str
    customer_email: str
    seller_response_due_date: str
    created_at: datetime
