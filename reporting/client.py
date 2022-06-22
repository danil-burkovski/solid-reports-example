import base64
import hashlib
import hmac
import json
from datetime import datetime
from typing import Any, Dict, Iterable

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


class Client:
    DEFAULT_BASE_API_URL = "https://reports.solidgate.com/api/v1/"
    DEFAULT_ENCODING = "UTF-8"

    __DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, channel: Channel, base_api_url: str = DEFAULT_BASE_API_URL):
        self.channel = channel
        self.base_api_url = base_api_url

    def card_orders(self, date_range: DateRange) -> Iterable[schema.CardOrder]:
        path = "card-orders"
        key = "orders"
        report_items = self.__get_report_items(path, date_range, key)
        for report_item in report_items:
            yield schema.CardOrder(**report_item)

    def chargebacks(self, date_range: DateRange) -> Iterable[schema.ChargebackOrder]:
        path = "card-orders/chargebacks"
        key = "orders"
        report_items = self.__get_report_items(path, date_range, key)
        for report_item in report_items:
            yield schema.ChargebackOrder(**report_item)

    def apm_orders(self, date_range: DateRange) -> Iterable[schema.APMOrder]:
        path = "apm-orders"
        key = "orders"
        report_items = self.__get_report_items(path, date_range, key)
        for report_item in report_items:
            yield schema.APMOrder(**report_item)

    def fraud_alerts(self, date_range: DateRange) -> Iterable[schema.FraudAlert]:
        path = "card-orders/fraud-alerts"
        key = "alerts"
        report_items = self.__get_report_items(path, date_range, key)
        for report_item in report_items:
            yield schema.FraudAlert(**report_item)

    def subscriptions(self, date_range: DateRange) -> Iterable[schema.Subscription]:
        path = "subscriptions"
        key = "subscriptions"
        report_items = self.__get_report_items(path, date_range, key)
        for report_item in report_items:
            yield schema.Subscription.from_dict(report_item)

    def paypal_disputes(self, date_range: DateRange) -> Iterable[schema.PayPalDispute]:
        path = "apm-orders/paypal-disputes"
        key = "disputes"
        report_items = self.__get_report_items(path, date_range, key)
        for report_item in report_items:
            yield schema.PayPalDispute(**report_item)

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
