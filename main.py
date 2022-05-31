from datetime import datetime

from reporting import Client

PUBLIC_KEY = "PUBLIC KEY HERE"
PRIVATE_KEY = "PRIVATE KEY HERE"

DATE_FROM = datetime(2022, 4, 1, 0, 0, 0, 0)
DATE_TO = datetime(2022, 5, 1, 0, 0, 0, 0)


def main():
    client = Client(PUBLIC_KEY, PRIVATE_KEY)
    subscriptions = client.subscriptions(date_from=DATE_FROM, date_to=DATE_TO)

    for subscription in subscriptions:
        print(subscription)


if __name__ == '__main__':
    main()
