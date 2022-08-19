from __future__ import absolute_import, division, print_function

import os

import fintecture


fintecture.app_id = os.environ.get("FINTECTURE_APP_ID")
fintecture.app_secret = os.environ.get("FINTECTURE_APP_SECRET")
fintecture.private_key = os.environ.get("FINTECTURE_PRIVATE_KEY")
fintecture.access_token = os.environ.get("FINTECTURE_ACCESS_TOKEN")


print("Requesting to pay...")

if fintecture.access_token is None:
    print("Requesting an access token...")

    resp = fintecture.PIS.oauth()

    print("Success: %r" % (resp))

    fintecture.access_token = resp['access_token']
else:
    print("Using access token: %s" % fintecture.access_token)

redirect_uri = "https://domain.com"
print("Doing a request for payout call with redirection URL to %s..." % redirect_uri)

resp_request_for_payout = fintecture.PIS.request_to_payout(
    redirect_uri,
    language='es',
    state='85321',
    meta={
        'psu_name': 'Jean',
        'psu_email': 'jean@hooker.com',
        'psu_phone': '0232420304',
        'psu_phone_prefix': '+33',
        'psu_address': {
            'street_number': '8',
            'street': 'Alan Parvis Turing',
            'zip': '75013',
            'city': 'Paris',
            'country': 'FR',
        },
        'expire': 86400,
        'method': 'link',
    },
    data={
        'attributes': {
            'amount': '101.97',
            'currency': 'EUR',
            'communication': 'Reference 6469878'
        }
    }
)

print("Success: %r" % (resp_request_for_payout))

print("Doing a request to pay call with redirection URL to %s..." % redirect_uri)

resp_request_to_pay = fintecture.PIS.request_to_pay(
    redirect_uri,
    language='es',
    meta={
        'psu_name': 'M. John Doe',
        'psu_email': 'john@doe.com',
        'psu_phone': '0601020304',
        'psu_phone_prefix': '+33',
        'psu_address': {
            'street_number': '5',
            'street': 'Parvis Alan Turing',
            'zip': '75013',
            'city': 'Paris',
            'country': 'FR',
        },
        'expire': 86400,
        'due_date': 76400,
        'cc': 'copyc@mail.com',
        'bcc': 'tri_copyc@mail.com',
    },
    data={
        'type': 'request-to-pay',
        'attributes': {
            'amount': '230.79',
            'currency': 'EUR',
            'communication': 'Reference 8786469'
        }
    }
)

print("Success: %r" % (resp_request_to_pay))

# We are receiving an invalid response with HTTP with 500 of status code:
#
# fintecture.error.APIError: Invalid response object from API:
# '{
#   "status":"500",
#   "code":"internal_server_error",
#   "log_id":"b9bef7a8-0981-46da-8317-f0d1d2b7984b",
#   "errors":[
#       {
#           "code":"request_to_pay_unsuccessful",
#           "title":"Internal Error",
#           "detail":"The request to pay initiation has been unsuccessful"
#       }
#   ]
# }'
# (HTTP response code was 500)
