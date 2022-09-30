from __future__ import absolute_import, division, print_function

import os

import fintecture


print("Searching URL to connect with AIS...")

redirect_uri = 'https://webhook.site/4ff3f300-c82c-4b4f-b92e-d0691656a663'

resp = fintecture.AIS.connect(
    app_id=os.environ.get("FINTECTURE_APP_ID"),
    redirect_uri=redirect_uri,
    state="1234"
)

print("Redirecting user to {} ...".format(
    resp['meta']['url']
))
print("Success: %r" % (resp))


# after connecting with above URL we receive data from webhook as bellow
# customer_id	    1bfca013fedeb208080c5bead11df5ca
# code	            56f0533637c1aa1eff0fd2bf5d6f9fce
# provider	        cmcifrpp
# state	            1234
