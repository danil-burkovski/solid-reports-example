import base64
import hashlib
import hmac
import json
import operator
from datetime import datetime
from typing import Callable, Dict, Iterable

import requests


class Client:
    DEFAULT_BASE_API_URL = "https://reports.solidgate.com/api/v1/"
    DEFAULT_ENCODING = "UTF-8"

    __DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, public_key: str, private_key: str, base_api_url: str = DEFAULT_BASE_API_URL):
        self.__public_key = public_key
        self.__private_key = private_key
        self.__base_api_url = base_api_url

    def card_orders(self, date_from: datetime, date_to: datetime) -> Iterable[Dict]:
        path = "card-orders"
        key = "orders"
        return self.__get_report(path, date_from, date_to, key)

    def chargebacks(self, date_from: datetime, date_to: datetime) -> Iterable[Dict]:
        path = "card-orders/chargebacks"
        key = "orders"
        return self.__get_report(path, date_from, date_to, key)

    def apm_orders(self, date_from: datetime, date_to: datetime) -> Iterable[Dict]:
        path = "apm-orders"
        key = "orders"
        return self.__get_report(path, date_from, date_to, key)

    def fraud_alerts(self, date_from: datetime, date_to: datetime) -> Iterable[Dict]:
        path = "card-orders/fraud-alerts"
        key = "alerts"
        return self.__get_report(path, date_from, date_to, key)

    def subscriptions(self, date_from: datetime, date_to: datetime) -> Iterable[Dict]:
        path = "subscriptions"
        key = "subscriptions"
        extractor = operator.methodcaller("values")
        return self.__get_report(path, date_from, date_to, key, extractor)

    def paypal_disputes(self, date_from: datetime, date_to: datetime) -> Iterable[Dict]:
        path = "apm-orders/paypal-disputes"
        key = "disputes"
        return self.__get_report(path, date_from, date_to, key)

    def __get_report(self, path: str,
                     date_from: datetime, date_to: datetime,
                     key: str,
                     items_extractor: Callable = lambda items: items) -> Iterable[Dict]:
        report_pages = self.__send_pagination_request(path, date_from, date_to)
        for items in map(operator.itemgetter(key), report_pages):
            yield from items_extractor(items)

    def __send_pagination_request(self, path: str,
                                  date_from: datetime, date_to: datetime) -> Iterable[Dict]:
        request_body = {"date_from": date_from.strftime(self.__DATETIME_FORMAT),
                        "date_to": date_to.strftime(self.__DATETIME_FORMAT)}

        while True:
            response = self.__send_request(path, request_body)
            if not response.ok:
                raise response.raise_for_status()
            response_body = response.json()

            yield response_body

            next_page_iterator = response_body["metadata"]["next_page_iterator"]
            if next_page_iterator is None:
                break
            request_body["next_page_iterator"] = next_page_iterator

    def __send_request(self, path: str, request_body: Dict[str, str]) -> requests.Response:
        request_url = self.__base_api_url + path
        headers = {"Merchant": self.__public_key,
                   "Signature": self.__sign_request_body(request_body)}

        return requests.post(request_url, headers=headers, json=request_body)

    def __sign_request_body(self, request_body: Dict[str, str]) -> str:
        json_request_body = json.dumps(request_body)
        data_to_sign = self.__public_key + json_request_body + self.__public_key
        signed_data = hmac.new(self.__private_key.encode(self.DEFAULT_ENCODING),
                               data_to_sign.encode(self.DEFAULT_ENCODING),
                               hashlib.sha512).hexdigest().encode(self.DEFAULT_ENCODING)

        return base64.b64encode(signed_data).decode(self.DEFAULT_ENCODING)
