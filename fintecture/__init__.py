from __future__ import absolute_import, division, print_function

import os

# Fintecture Python bindings
# API docs at https://docs.fintecture.com/

# API resources
from fintecture.environments import *  # noqa

# Configuration variables

app_id = None
app_secret = None
private_key = None
env = DEFAULT_ENV

access_token = None
api_key = None
client_id = None

production_api_base = "https://api.fintecture.com"
sandbox_api_base = "https://api-sandbox.fintecture.com"

api_version = None
verify_ssl_certs = True
proxy = None
default_http_client = None
app_info = None
enable_telemetry = True
max_network_retries = 0
ca_bundle_path = os.path.join(
    os.path.dirname(__file__), "data", "ca-certificates.crt"
)

# Set to either 'debug' or 'info', controls console logging
log = None

# API resources
from fintecture.api_resources import *  # noqa

# OAuth
from fintecture.oauth import OAuth  # noqa

# Webhooks
from fintecture.webhook import Webhook, WebhookSignature  # noqa


# Sets some basic information about the running application that's sent along
# with API requests. Useful for plugin authors to identify their plugin when
# communicating with fintecture.
#
# Takes a name and optional version and plugin URL.
def set_app_info(name, partner_id=None, url=None, version=None):
    global app_info
    app_info = {
        "name": name,
        "partner_id": partner_id,
        "url": url,
        "version": version,
    }
