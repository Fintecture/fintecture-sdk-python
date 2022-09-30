from __future__ import absolute_import, division, print_function

import os

import fintecture


fintecture.app_id = os.environ.get("FINTECTURE_APP_ID")
fintecture.app_secret = os.environ.get("FINTECTURE_APP_SECRET")
fintecture.access_token = os.environ.get("FINTECTURE_ACCESS_TOKEN")


print("Searching customer accounts...")

customer_id = 'a95784c3ddfed8f3f20790c4ad338569'

resp = fintecture.Customer.get_accounts(customer_id)

print("Success: %r" % (resp))

print("Searching customer transactions of the first result...")

transactions_resp = fintecture.Customer.get_account_transactions(customer_id, resp['data'][0]['id'])

print("Success: %r" % (transactions_resp))

print("Searching customer account holders...")

accountholders_resp = fintecture.Customer.get_account_holders(customer_id)

print("Success: %r" % (accountholders_resp))
