from datetime import datetime

import pydantic


class FraudAlert(pydantic.BaseModel):
    order_id: str
    created_at: datetime
    fraud_amount: int
    fraud_currency: str
    fraud_amount_usd: int
    fraud_type: str
    card_scheme: str
    fraud_report_date: datetime
    reason_code_description: str
