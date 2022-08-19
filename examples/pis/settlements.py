from __future__ import absolute_import, division, print_function

import os

import fintecture


fintecture.app_id = os.environ.get("FINTECTURE_APP_ID")
fintecture.app_secret = os.environ.get("FINTECTURE_APP_SECRET")
fintecture.private_key = os.environ.get("FINTECTURE_PRIVATE_KEY")
fintecture.access_token = os.environ.get("FINTECTURE_ACCESS_TOKEN")


print("Retrieving all outgoing payments from your Local Acquiring account to your own bank account. ...")

if fintecture.access_token is None:
    print("Requesting an access token...")

    resp = fintecture.PIS.oauth()

    print("Success: %r" % (resp))

    fintecture.access_token = resp['access_token']
else:
    print("Using access token: %s" % fintecture.access_token)

print("Now retrieves payments...")

resp_settlements = fintecture.PIS.settlements()

print("Success: %r" % (resp_settlements))
