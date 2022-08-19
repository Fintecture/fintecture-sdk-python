from __future__ import absolute_import, division, print_function

import os

import fintecture


fintecture.app_id = os.environ.get("FINTECTURE_APP_ID")
fintecture.app_secret = os.environ.get("FINTECTURE_APP_SECRET")
fintecture.private_key = os.environ.get("FINTECTURE_PRIVATE_KEY")
fintecture.access_token = os.environ.get("FINTECTURE_ACCESS_TOKEN")


print("Retrieving all payments...")

if fintecture.access_token is None:
    print("Requesting an access token...")

    resp = fintecture.PIS.oauth()

    print("Success: %r" % (resp))

    fintecture.access_token = resp['access_token']
else:
    print("Using access token: %s" % fintecture.access_token)

print("Now retrieves payments...")

resp_payments = fintecture.Payment.search()

print("Success: %r" % (resp_payments))

print("Select one session identifier to filter payments by session...")
session_id = resp_payments.get('data', [])[0].get('id', False)

payment = fintecture.Payment.retrieve(session_id)

print("Success: %r" % (payment))


print("Canceling payment...")

resp_payment_cancellation = payment.update(status='payment_cancelled')

print("Success: %r" % (resp_payment_cancellation))
