from __future__ import absolute_import, division, print_function

import os

import fintecture


fintecture.app_id = os.environ.get("FINTECTURE_APP_ID")
fintecture.app_secret = os.environ.get("FINTECTURE_APP_SECRET")


print("After user connect him account you will receive in your webhook a code for authenticate")

code = 'ec2c1ee4d1f40f4db60ea30f4ea4769d'
token_resp = fintecture.AIS.oauth(code=code)

fintecture.access_token = token_resp['access_token']

print("Success: %r" % (token_resp))
