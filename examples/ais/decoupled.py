from __future__ import absolute_import, division, print_function

import os

import fintecture

from fintecture.constants import DECOUPLED_MODEL_TYPE
from fintecture.six.moves.urllib.parse import urlparse, urlsplit


fintecture.app_id = os.environ.get("FINTECTURE_APP_ID")
fintecture.app_secret = os.environ.get("FINTECTURE_APP_SECRET")
fintecture.private_key = os.environ.get("FINTECTURE_PRIVATE_KEY")


try:
    print("Do operations using a decoupled model with AIS...")

    # 1. select a Bank (provider)
    # provider_id = "bschesmm"  # Banco Santander
    # provider_id = "bsabesbb"  # Banco Sabadell
    # provider_id = "cmcifrpp"  # CIC
    provider_id = "handse"  # Handelsbanken | This is an only one provider that support decoupled model
    redirect_uri = 'https://webhook.site/5940c656-7fd3-40a0-ad41-9cfba1e986f3'


    # 2. get the provider's decoupled auth polling URL
    resp_authorize = fintecture.AIS.authorize(
        provider_id=provider_id,
        redirect_uri=redirect_uri,
        state="1234",
        model=DECOUPLED_MODEL_TYPE,
        psu_id='9090901',
        psu_ip_address='92.168.0.12',
    )

    provider_auth_url = resp_authorize['url']
    print("Redirecting user to {} ...".format(
        provider_auth_url
    ))
    # provider_auth_polling_id = resp_authorize['polling_id']
    # print("Polling identifier is {} ...".format(
    #     provider_auth_polling_id
    # ))

    parsed_url = urlparse(provider_auth_url)
    path = parsed_url.path
    provider_auth_polling_id = path.rsplit('/', 1)[-1]
    # provider_auth_polling_id = 'aee32ed6-73fc-4154-9f18-149169b0bc6f'
    print("polling auth identifier: %s\n" % (provider_auth_polling_id))
    print("Success: %r\n" % (resp_authorize))


    # 3. keep polling the provider's decoupled auth polling URL until authentication either COMPLETED or FAILED
    customer_id = None
    code = None

    # for now, we use a simple request for check status of decoupled authentication,
    # but you must do a keep polling requests for check status until it is COMPLETED or FAILED
    resp_decoupled = fintecture.AIS.decoupled(
        provider_id=provider_id,
        polling_id=provider_auth_polling_id,
        redirect_uri=redirect_uri,
        state="1234",
        psu_id='9090901',
        psu_ip_address='92.168.0.12',
    )
    print("Decoupled response: %r\n" % (resp_decoupled))

    decoupled_auth_status = resp_decoupled['status']
    if decoupled_auth_status == 'COMPLETED':
        # IMPORTANT: we are replacing expected property 'customer_id' and received 'connection_id'
        # customer_id = resp_decoupled['customer_id']
        customer_id = resp_decoupled['connection_id']
        code = resp_decoupled['code']
    elif decoupled_auth_status == 'FAILED':
        raise ValueError("Decoupled authentication fails for an unknown reason. Try later!")
    else:
        raise ValueError("Decoupled authentication is yet pending. Keep polling for check status!")


    # 4. authenticate your app to Fintecture and get your "access_token" and "refresh_token"
    resp_token = fintecture.AIS.oauth(code=code)

    fintecture.access_token = resp_token['access_token']
    refresh_token = resp_token['refresh_token']
    expires_in = int(resp_token['expires_in'])
    print("Access token is: %s" % (fintecture.access_token))
    print("Refresh token is: %s" % (refresh_token))

    print("Success: %r\n" % (resp_token))


    # 5. request any AIS API
    accounts = fintecture.Account.search_by_customer(customer_id)

    print("accounts: %r" % (accounts))


    # 6. request a refresh token
    refresh_token_resp = fintecture.OAuth.refresh_token(
        refresh_token=refresh_token
    )
    fintecture.access_token = refresh_token_resp['access_token']
    print("Access token was refreshed with the new value: %s" % (fintecture.access_token))

    print("Success: %r\n" % (refresh_token_resp))

except Exception as e:
    print("ERROR received: %r" % e)
