# File generated from our OpenAPI spec
from __future__ import absolute_import, division, print_function

import base64
import fintecture

from fintecture import api_requestor, error
from fintecture.api_resources.abstract import APIResource
from fintecture.api_resources.payment import Payment


class PIS(APIResource):
    OBJECT_NAME = "pis"

    @classmethod
    def connect(cls, **params):
        return Payment.connect(**params)

    # noinspection PyPackageRequirements
    @classmethod
    def initiate(cls, provider_id, redirect_uri, **params):
        return Payment.initiate(provider_id, redirect_uri, **params)

    @classmethod
    def oauth(cls, app_id=None, app_secret=None, **params):
        app_id = app_id or fintecture.app_id
        app_secret = app_secret or fintecture.app_secret

        params.update({
            'app_id': app_id,
            'grant_type': 'client_credentials',
            'scope': 'PIS',
        })
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': "Basic {}".format(
                base64.b64encode("{}:{}".format(
                    app_id,
                    app_secret
                ).encode('utf-8')).decode('utf-8')
            )
        }

        requestor = api_requestor.APIRequestor(app_id, app_secret)
        response, _ = requestor.request("post", "/oauth/accesstoken", params, headers)

        return response.data

    @classmethod
    def initiate_refund(cls, **params):
        if not params.get('state', False):
            raise error.InvalidRequestError(
                message="state: A state parameter which will be provided back on redirection.",
                param='state',
            )
        state = params.get('state')
        del params['state']
        params.update({
            'headers': {
                'Content-Type': 'application/json'
            }
        })
        return cls._static_request(
            "post",
            "/pis/v2/refund?state={}".format(state),
            params=params,
        )

    @classmethod
    def request_to_pay(cls, redirect_uri, **params):
        language = params.get('language', '')
        if not language:
            raise error.InvalidRequestError(
                message="language: its a required parameter that is a code of two letters; ex: fr",
                param='language',
            )
        if len(language) != 2:
            raise error.InvalidRequestError(
                message="language parameter is of two characters of length; ex: fr",
                param='language',
            )
        params.update({
            'headers': {
                'Content-Type': 'application/json',
                'x-language': language,
            }
        })
        del params['language']

        with_virtualbeneficiary = params.get('with_virtualbeneficiary', False)
        if with_virtualbeneficiary:
            del params['with_virtualbeneficiary']

        state = params.get('state', False)
        if state:
            del params['state']

        url = "/pis/v2/request-to-pay?redirect_uri={url}{virtual}{state}".format(
            url=redirect_uri,
            virtual='&with_virtualbeneficiary=true' if with_virtualbeneficiary else '',
            state='&state={}'.format(state) if state else ''
        )

        return cls._static_request(
            "post",
            url,
            params=params,
        )

    @classmethod
    def request_for_payout(cls, redirect_uri, **params):
        if not params.get('state', False):
            raise error.InvalidRequestError(
                message="state: A state parameter which will be provided back on redirection.",
                param='state',
            )
        state = params.get('state')
        del params['state']

        language = params.get('language', '')
        if not language:
            raise error.InvalidRequestError(
                message="language: its a required parameter that is a code of two letters; ex: fr",
                param='language',
            )
        if len(language) != 2:
            raise error.InvalidRequestError(
                message="language parameter is of two characters of length; ex: fr",
                param='language',
            )
        params.update({
            'headers': {
                'Content-Type': 'application/json',
                'x-language': language,
            }
        })
        del params['language']
        return cls._static_request(
            "post",
            "/pis/v2/request-for-payout?redirect_uri={url}&state={state}".format(
                url=redirect_uri,
                state=state,
            ),
            params=params,
        )

    @classmethod
    def settlements(cls, **params):
        settlement_id = params.get('settlement_id', False)
        if settlement_id:
            del params['settlement_id']
            settlement_id = '/%s' % settlement_id
        else:
            settlement_id = ''

        params.update({
            'headers': {
                'Content-Type': 'application/json'
            }
        })
        return cls._static_request(
            "get",
            "/pis/v2/settlements{settlement}".format(settlement=settlement_id),
            params=params,
        )

    @classmethod
    def class_url(cls):
        return "/v1/pis"
