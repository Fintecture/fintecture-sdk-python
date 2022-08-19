from __future__ import absolute_import, division, print_function

import os

import fintecture


fintecture.app_id = os.environ.get("FINTECTURE_APP_ID")
fintecture.app_secret = os.environ.get("FINTECTURE_APP_SECRET")
fintecture.private_key = os.environ.get("FINTECTURE_PRIVATE_KEY")
fintecture.access_token = os.environ.get("FINTECTURE_ACCESS_TOKEN")


print("Refunding an initiate payment...")

if fintecture.access_token is None:
    print("Requesting an access token...")

    resp = fintecture.PIS.oauth()

    print("Success: %r" % (resp))

    fintecture.access_token = resp['access_token']
else:
    print("Using access token: %s" % fintecture.access_token)

session_id = '88a6c01995a642a1924c465503f33cc4'

payment = fintecture.Payment.retrieve(session_id)

print("Retrieving refund for selected session...")

resp_session_payments_refund = payment.refund(data={
    'attributes': {
        "amount": "15.2",
        "communication": "REFUND ORDER-123"
    }
})

print("Success: %r" % (resp_session_payments_refund))

resp_initiate_refund = fintecture.PIS.initiate_refund(
    state='5678',
    meta={
        'session_id': session_id
    },
    data={
        'attributes': {
            'amount': '1.99',
            'communication': 'REFUND ORDER-123'
        }
    })

print("Success: %r" % (resp_initiate_refund))
