# File generated from our OpenAPI spec
from __future__ import absolute_import, division, print_function

from fintecture import util
from fintecture import error

from fintecture.api_resources.abstract import SearchableAPIResource
from fintecture.api_resources.abstract import CreateableAPIResource
from fintecture.api_resources.abstract import DeletableAPIResource
from fintecture.api_resources.abstract import ListableAPIResource
from fintecture.api_resources.abstract import UpdateableAPIResource


class Payment(
    SearchableAPIResource,
    CreateableAPIResource,
    DeletableAPIResource,
    ListableAPIResource,
    UpdateableAPIResource,
):
    OBJECT_NAME = "payment"

    @classmethod
    def search(cls, *args, **kwargs):
        return cls._search(search_url="/pis/v2/payments", *args, **kwargs)

    @classmethod
    def search_auto_paging_iter(cls, *args, **kwargs):
        return cls.search(*args, **kwargs).auto_paging_iter()

    @classmethod
    def connect(cls, **params):
        if not params.get('state', False):
            raise error.InvalidRequestError(
                "state: A state parameter which will be provided back on redirection."
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
            "/pis/v2/connect?state={}".format(state),
            params=params,
        )

    @classmethod
    def initiate(cls, provider_id, redirect_uri, **params):
        if not params.get('state', False):
            raise error.InvalidRequestError(
                "state: A state parameter which will be provided back on redirection."
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
            "/pis/v2/provider/{provider}/initiate?redirect_uri={url}&state={state}".format(
                provider=provider_id,
                state=state,
                url=redirect_uri
            ),
            params=params,
        )

    def refund(self, **params):
        params.update({
            "meta": {
                "session_id": self.get('data', {}).get('id', {})
            },
            'headers': {
                'Content-Type': 'application/json'
            }
        })
        return self._request(
            "post",
            "/pis/v2/refund",
            params=params,
        )

    def update(self, **params):
        session_id = self.get('data', {}).get('id', {})
        if not params.get('status', False):
            raise error.InvalidRequestError(
                "status: is a parameter for update payment attributes and only accepts 'payment_cancelled' value"
            )
        status = params.get('status')
        del params['status']

        params.update({
            "meta": {
                "status": status
            },
            'headers': {
                'Content-Type': 'application/json'
            }
        })
        return self._request(
            "patch",
            "/pis/v2/payments/{}".format(session_id),
            params=params,
        )

    @classmethod
    def class_url(cls):
        return "/pis/v2/payments"
