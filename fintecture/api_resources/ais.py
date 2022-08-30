# File generated from our OpenAPI spec
from __future__ import absolute_import, division, print_function

import base64
import fintecture

from fintecture import error

from fintecture.api_resources.abstract import APIResource
from fintecture.constants import DECOUPLED_MODEL_TYPE


class AIS(APIResource):
    OBJECT_NAME = "ais"

    @classmethod
    def oauth(cls, **params):
        if not params.get('code', False):
            raise error.InvalidRequestError(
                message="code parameter is required for authenticate with oAuth through AIS application",
                param='code',
            )

        params.update({
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
    def connect(cls, **params):
        if not params.get('redirect_uri', False):
            raise error.InvalidRequestError(
                message="redirect_uri: must correspond to one of the URLs provided when creating an "
                        "application on the console.",
                param='redirect_uri',
            )
        if not params.get('state', False):
            raise error.InvalidRequestError(
                message="state: a mandatory state parameter which will be provided back on redirection.",
                param='state',
            )
        return cls._static_request(
            "get",
            "/ais/v2/connect",
            params=params,
        )

    @classmethod
    def authorize(cls, provider_id, redirect_uri, **params):

        if not params.get('state', False):
            raise error.InvalidRequestError(
                message="state: a mandatory state parameter which will be provided back on redirection.",
                param='state'
            )

        model = params.get('model', False)
        # access_token = params.get('access_token', False)

        headers = {}

        if model == DECOUPLED_MODEL_TYPE:
            psu_id = params.get('psu_id', False)
            psu_ip_address = params.get('psu_ip_address', False)
            if not psu_id or not psu_ip_address:
                raise error.InvalidRequestError(
                    message="when model is 'decoupled' the 'x-psu-id' and 'x-psu-ip-address' parameters are required.",
                    param='x-psu-id,x-psu-ip-address'
                )
            headers['x-psu-id'] = psu_id
            headers['x-psu-ip-address'] = psu_ip_address

        params.update({
            'response_type': 'code',
            'redirect_uri': redirect_uri,
            # 'access_token': access_token,
            'headers': headers
        })

        return cls._static_request(
            "get",
            "/ais/v1/provider/{provider}/authorize".format(provider=provider_id),
            params=params,
        )

    @classmethod
    def decoupled(cls, provider_id, polling_id, **params):
        headers = {}
        psu_id = params.get('psu_id', False)
        psu_ip_address = params.get('psu_ip_address', False)
        if not psu_id or not psu_ip_address:
            raise error.InvalidRequestError(
                message="when model is 'decoupled' the 'x-psu-id' and 'x-psu-ip-address' parameters are required.",
                param='x-psu-id,x-psu-ip-address',
            )
        headers['x-psu-id'] = psu_id
        headers['x-psu-ip-address'] = psu_ip_address

        params.update({
            'response_type': 'code',
            'headers': headers
        })

        return cls._static_request(
            "get",
            "/ais/v1/provider/{provider}/authorize/decoupled/{polling}".format(
                provider=provider_id,
                polling=polling_id,
            ),
            params=params,
        )

    @classmethod
    def class_url(cls):
        return "/v1/ais"
