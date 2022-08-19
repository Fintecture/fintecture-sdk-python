from __future__ import absolute_import, division, print_function

import os

import fintecture


fintecture.app_id = os.environ.get("FINTECTURE_APP_ID")
fintecture.app_secret = os.environ.get("FINTECTURE_APP_SECRET")


try:
    print("Searching URL to connect with PIS...")

    resp = fintecture.PIS.oauth()

    print("Success: %r" % (resp))

    fintecture.access_token = resp['access_token']

    print("Initiating with PIS...")

    provider = "baskes2b"
    redirect_uri = "https://domain.com"

    resp_connect = fintecture.PIS.initiate(
        provider,
        redirect_uri,
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

    print("Success: %r" % (resp_connect))

except Exception as e:
    print("ERROR received: %r" % e)
