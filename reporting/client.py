import base64
import hashlib
import hmac
import json
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, TypeVar

import pydantic
import requests

from reporting import schema


class Channel(pydantic.BaseModel):
    name: str
    public_key: str
    private_key: str
    is_apm: bool = False

    class Config:
        fields = {"public_key": {"exclude": True},
                  "private_key": {"exclude": True}}


class DateRange(pydantic.BaseModel):
    date_from: datetime
    date_to: datetime


ReportPage = Dict[str, Any]
ReportPages = Iterable[ReportPage]
T = TypeVar("T")


class Client:
    DEFAULT_BASE_API_URL = "https://reports.solidgate.com/api/v1/"
    DEFAULT_ENCODING = "UTF-8"

    __DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, channel: Channel, base_api_url: str = DEFAULT_BASE_API_URL):
        self.channel = channel
        self.base_api_url = base_api_url

    def card_orders(self, date_range: DateRange) -> Iterable[schema.CardOrder]:
        return self.__process_report("card-orders", date_range, "orders", schema.CardOrder)

    def chargebacks(self, date_range: DateRange) -> Iterable[schema.ChargebackOrder]:
        return self.__process_report("card-orders/chargebacks", date_range, "orders",
                                     schema.ChargebackOrder)

    def apm_orders(self, date_range: DateRange) -> Iterable[schema.APMOrder]:
        return self.__process_report("apm-orders", date_range, "orders", schema.APMOrder)

    def fraud_alerts(self, date_range: DateRange) -> Iterable[schema.FraudAlert]:
        return self.__process_report("card-orders/fraud-alerts", date_range, "alerts",
                                     schema.FraudAlert)

    def subscriptions(self, date_range: DateRange) -> Iterable[schema.Subscription]:
        return self.__process_report("subscriptions", date_range, "subscriptions",
                                     schema.Subscription.from_kwargs)

    def paypal_disputes(self, date_range: DateRange) -> Iterable[schema.PayPalDispute]:
        return self.__process_report("apm-orders/paypal-disputes", date_range, "disputes",
                                     schema.PayPalDispute)

    def __process_report(self, path: str, date_range: DateRange, key: str,
                         record_factory: Callable[..., T]) -> Iterable[T]:
        report_items = self.__get_report_items(path, date_range, key)
        for report_item in report_items:
            yield record_factory(**report_item)

    def __get_report_items(self, path: str, date_range: DateRange, key: str) -> ReportPages:
        for report_page in self.__get_report_pages(path, date_range):
            if key not in report_page:
                raise ValueError(report_page)
            items = report_page[key]
            if isinstance(items, dict):
                yield from items.values()
            else:
                yield from items

    def __get_report_pages(self, path: str, date_range: DateRange) -> ReportPages:
        request_body = self.__request_body_from_date_range(date_range)
        while True:
            response = self.__send_request(path, request_body)
            if not response.ok:
                raise response.raise_for_status()
            report_page = response.json()

            yield report_page

            next_page_iterator = report_page["metadata"]["next_page_iterator"]
            if next_page_iterator is None:
                break
            request_body["next_page_iterator"] = next_page_iterator

    def __request_body_from_date_range(self, date_range: DateRange) -> Dict[str, str]:
        return {"date_from": date_range.date_from.strftime(self.__DATETIME_FORMAT),
                "date_to": date_range.date_to.strftime(self.__DATETIME_FORMAT)}

    def __send_request(self, path: str, request_body: Dict[str, str]) -> requests.Response:
        request_url = self.base_api_url + path
        headers = {"Merchant": self.channel.public_key,
                   "Signature": self.__sign_request_body(request_body)}

        return requests.post(request_url, headers=headers, json=request_body)

    def __sign_request_body(self, request_body: Dict[str, str]) -> str:
        json_request_body = json.dumps(request_body)
        data_to_sign = self.channel.public_key + json_request_body + self.channel.public_key
        signed_data = hmac.new(self.channel.private_key.encode(self.DEFAULT_ENCODING),
                               data_to_sign.encode(self.DEFAULT_ENCODING),
                               hashlib.sha512).hexdigest().encode(self.DEFAULT_ENCODING)

        return base64.b64encode(signed_data).decode(self.DEFAULT_ENCODING)
