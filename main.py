from datetime import datetime

import reporting
import reporting.schema

DATE_FROM = datetime(2022, 5, 1, 0, 0, 0, 0)
DATE_TO = datetime(2022, 5, 31, 23, 59, 59, 0)


class SubscriptionOut(reporting.schema.Subscription):
    channel: reporting.Channel


class CardOrderOut(reporting.schema.CardOrder):
    channel: reporting.Channel


class ChargebackOrderOut(reporting.schema.ChargebackOrder):
    channel: reporting.Channel


class APMOrderOut(reporting.schema.APMOrder):
    channel: reporting.Channel


class FraudAlertOut(reporting.schema.FraudAlert):
    channel: reporting.Channel


class PayPalDisputeOut(reporting.schema.PayPalDispute):
    channel: reporting.Channel


def main():
    channels = [
        reporting.Channel(name="foo",
                          public_key="bar",
                          private_key="baz",
                          is_apm=True),
    ]

    for channel in channels:
        if channel.is_apm:
            continue

        reporting_client = reporting.Client(channel)

        date_range = reporting.DateRange(date_from=DATE_FROM, date_to=DATE_TO)
        for subscription in reporting_client.subscriptions(date_range):
            subscription_out = SubscriptionOut(**subscription.dict(exclude_none=True),
                                               channel=channel)
            print(subscription_out.json())


if __name__ == '__main__':
    main()
