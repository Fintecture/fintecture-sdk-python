# File generated from our OpenAPI spec
from __future__ import absolute_import, division, print_function

from fintecture import api_requestor
from fintecture import util
from fintecture.api_resources.abstract import DeletableAPIResource


class EphemeralKey(DeletableAPIResource):
    OBJECT_NAME = "ephemeral_key"

    @classmethod
    def create(
        cls,
        api_key=None,
        idempotency_key=None,
        fintecture_version=None,
        fintecture_account=None,
        **params
    ):
        if fintecture_version is None:
            raise ValueError(
                "fintecture_version must be specified to create an ephemeral "
                "key"
            )

        requestor = api_requestor.APIRequestor(
            api_key, api_version=fintecture_version, account=fintecture_account
        )

        url = cls.class_url()
        headers = util.populate_headers(idempotency_key)
        response, api_key = requestor.request("post", url, params, headers)
        return util.convert_to_fintecture_object(
            response, api_key, fintecture_version, fintecture_account
        )
