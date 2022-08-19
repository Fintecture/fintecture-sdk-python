from __future__ import absolute_import, division, print_function

import os

import fintecture


fintecture.app_id = os.environ.get("FINTECTURE_APP_ID")


print("Searching test accounts...")

resp = fintecture.TestAccount.search()

print("Success: %r" % (resp))
