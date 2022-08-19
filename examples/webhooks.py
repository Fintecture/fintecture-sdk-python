from __future__ import absolute_import, division, print_function

import os

import fintecture
from flask import Flask, request

fintecture.app_id = os.environ.get("FINTECTURE_APP_ID")
fintecture.app_secret = os.environ.get("FINTECTURE_APP_SECRET")
fintecture.access_token = os.environ.get("FINTECTURE_ACCESS_TOKEN")

webhook_secret = os.environ.get("WEBHOOK_SECRET")

app = Flask(__name__)

#TODO: Complete example

@app.route("/webhooks", methods=["POST"])
def webhooks():
    payload = request.data.decode("utf-8")
    received_sig = request.headers.get("Fintecture-Signature", None)

    try:
        event = fintecture.Webhook.construct_event(
            payload, received_sig, webhook_secret
        )
    except ValueError:
        print("Error while decoding event!")
        return "Bad payload", 400
    except fintecture.error.SignatureVerificationError:
        print("Invalid signature!")
        return "Bad signature", 400

    print(
        "Received event: id={id}, type={type}".format(
            id=event.id, type=event.type
        )
    )

    return "", 200


if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 5000)))
