from __future__ import absolute_import, division, print_function

import os

import fintecture
from flask import Flask, request


fintecture.app_id = os.environ.get("FINTECTURE_APP_ID")
fintecture.app_secret = os.environ.get("FINTECTURE_APP_SECRET")
fintecture.access_token = os.environ.get("FINTECTURE_ACCESS_TOKEN")
fintecture.private_key = os.environ.get("FINTECTURE_PRIVATE_KEY")

app = Flask(__name__)


@app.route("/webhooks", methods=["POST"])
def webhooks():
    payload = request.form
    received_digest = request.headers.get("Digest", None)
    received_signature = request.headers.get("Signature", None)
    received_request_id = request.headers.get("X-Request-ID", None)

    try:
        event = fintecture.Webhook.construct_event(
            payload, received_digest, received_signature, received_request_id
        )
    except ValueError:
        print("Error while decoding event!")
        return "Bad payload", 400
    except fintecture.error.SignatureVerificationError as e:
        print("Invalid signature!")
        print("ERROR: %r" % e)
        return "Bad signature", 400

    print(
        "Received event: session_id={session_id}, status={status}, type={type}".format(
            session_id=event.get('session_id'),
            status=event.get('status'),
            type=event.get('type')
        )
    )

    return "", 200


if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)))
