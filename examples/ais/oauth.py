from __future__ import absolute_import, division, print_function

import os

import fintecture


fintecture.app_id = os.environ.get("FINTECTURE_APP_ID")
fintecture.app_secret = os.environ.get("FINTECTURE_APP_SECRET")


print("After user connect him account you will receive in your webhook a code for authenticate")

code = '5ebc08acf13a866a0a97c2a37013cb28'
token_resp = fintecture.AIS.oauth(code=code)

fintecture.access_token = token_resp['access_token']

print("Success: %r" % (token_resp))
