from __future__ import absolute_import, division, print_function

import os

import fintecture


fintecture.app_id = os.environ.get("FINTECTURE_APP_ID")
fintecture.app_secret = os.environ.get("FINTECTURE_APP_SECRET")
fintecture.private_key = os.environ.get("FINTECTURE_PRIVATE_KEY")


print("Looking for URL to authorize in bank with AIS...")

# provider_id = "bschesmm"  # Banco Santander
# provider_id = "bsabesbb"  # Banco Sabadell
provider_id = "cmcifrpp"  # CIC
redirect_uri = 'https://webhook.site/5940c656-7fd3-40a0-ad41-9cfba1e986f3'

resp_authorize = fintecture.AIS.authorize(
    provider_id=provider_id,
    redirect_uri=redirect_uri,
    state="1234",

    # model='redirect', # is optional

    # model='decoupled', # is required with follow parameters too
    # psu_id='9090901',
    # psu_ip_address='92.168.0.12',
)

provider_auth_url = resp_authorize['url']
print("Redirecting user to {} ...".format(
    provider_auth_url
))
print("Success: %r\n" % (resp_authorize))

print("Now you must request in your browser previous URL, login, and finish the process...")

# if we use any bank with a sandbox, you can use some test account as follows:
# example, some test account:
# username: 078000000P
# password: 123456

print("After login... the callback redirection is requested and finish with some query parameters in your browser...")

# in cases of "error" we get URL with follow parameters:
# https://webhook.site/5940c656-7fd3-40a0-ad41-9cfba1e986f3?error=provider_error&state=1234&provider_error=access_denied
# Query Strings:
#   error: provider_error
#   state: 1234
#   provider_error: access_denied

# in cases of "success" we get URL with follow parameters:
# https://webhook.site/5940c656-7fd3-40a0-ad41-9cfba1e986f3?customer_id=380202af6694dbd2d177c84028f1908b&code=8ecd9b1079a7e1f2e4efd0a100bd5521&provider=cmcifrpp&state=1234
# Query Strings:
#   customer_id: 380202af6694dbd2d177c84028f1908b
#   code: 8ecd9b1079a7e1f2e4efd0a100bd5521
#   provider: cmcifrpp
#   state: 1234

customer_id = '54d131651e54eb7b359489bb5fba6bbc'
code = '1926ad72adccf6d0a4aa5b9dc320cb9e'
state = 1234

print("We must validate received state with sent and the same provider...")

print('Received code "{0}" and customer_id "{1}" from webhook...'.format(code, customer_id))
print("Now login using an oAuth with a code")

resp_token = fintecture.AIS.oauth(code=code)

fintecture.access_token = resp_token['access_token']

print("Success: %r" % (resp_token))

accounts = fintecture.Account.search_by_customer(customer_id)

print("accounts: %r" % (accounts))
