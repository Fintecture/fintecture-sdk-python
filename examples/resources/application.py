from __future__ import absolute_import, division, print_function

import os

import fintecture


fintecture.app_id = os.environ.get("FINTECTURE_APP_ID")


print("Searching application info...")

resp = fintecture.Application.retrieve()

print("Success: %r" % (resp))
