# File generated from our OpenAPI spec
from __future__ import absolute_import, division, print_function

import base64
import fintecture

from fintecture import error

from fintecture.api_resources.abstract import APIResource


class AIS(APIResource):
    OBJECT_NAME = "ais"

    @classmethod
    def connect(cls, **params):
        if not params.get('redirect_uri', False):
            raise error.InvalidRequestError(
                "redirect_uri: must correspond to one of the URLs provided when creating an application on the console."
            )
        if not params.get('state', False):
            raise error.InvalidRequestError(
                "state: an mandatory state parameter which will be provided back on redirection	."
            )
        return cls._static_request(
            "get",
            "/ais/v2/connect",
            params=params,
        )

    @classmethod
    def authorize(cls, provider_id, **params):
        if not params.get('redirect_uri', False):
            raise error.InvalidRequestError(
                "redirect_uri: must correspond to one of the URLs provided when creating an application on the console."
            )
        if not params.get('state', False):
            raise error.InvalidRequestError(
                "state: an mandatory state parameter which will be provided back on redirection	."
            )
        return cls._static_request(
            "get",
            "/ais/v2/connect",
            params=params,
        )

    @classmethod
    def oauth(cls, **params):
        params.update({
            'app_id': fintecture.app_id,
            'grant_type': 'authorization_code',
            'scope': 'AIS',
            'headers': {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': "Basic {}".format(
                    base64.b64encode("{}:{}".format(
                        fintecture.app_id,
                        fintecture.app_secret
                    ).encode('utf-8')).decode('utf-8')
                )
            }
        })
        return cls._static_request(
            "post",
            "/oauth/accesstoken",
            params=params,
        )

    @classmethod
    def class_url(cls):
        return "/v1/ais"
