from __future__ import absolute_import, division, print_function

import os

import fintecture

fintecture.app_id = os.environ.get("FINTECTURE_APP_ID")
fintecture.app_secret = os.environ.get("FINTECTURE_APP_SECRET")

print("Attempting charge...")

proxy = {
    "http": "http://<user>:<pass>@<proxy>:<port>",
    "https": "http://<user>:<pass>@<proxy>:<port>",
}

clients = (
    fintecture.http_client.RequestsClient(
        verify_ssl_certs=fintecture.verify_ssl_certs, proxy=proxy
    ),
    fintecture.http_client.PycurlClient(
        verify_ssl_certs=fintecture.verify_ssl_certs, proxy=proxy
    ),
    fintecture.http_client.Urllib2Client(
        verify_ssl_certs=fintecture.verify_ssl_certs, proxy=proxy
    ),
)

for c in clients:
    fintecture.default_http_client = c
    resp = fintecture.PIS.connect(
        state="1234",
        meta={
            'psu_name': 'M. John Doe',
            'psu_email': 'john@doe.com',
            'psu_phone': '0601020304',
            'psu_ip': '127.0.0.1',
            'psu_address': {
                'street': '5 Void Street',
                'complement': 'RDC',
                'zip': '12345',
                'city': 'Gotham',
                'country': 'FR',
            },
        },
        data={
            'type': 'SEPA',
            'attributes': {
                'amount': '550.60',
                'currency': 'EUR',
                'communication': 'Order 15654'
            }
        }
    )
    print("Success: %s, %r" % (c.name, resp))
