# File generated from our OpenAPI spec
from __future__ import absolute_import, division, print_function

from fintecture import api_requestor, util
from fintecture.api_resources.abstract import APIResource


class UsageRecord(APIResource):
    OBJECT_NAME = "usage_record"

    @classmethod
    def create(
        cls,
        api_key=None,
        idempotency_key=None,
        fintecture_version=None,
        fintecture_account=None,
        **params
    ):
        if "subscription_item" not in params:
            raise ValueError("Params must have a subscription_item key")

        subscription_item = params.pop("subscription_item")

        requestor = api_requestor.APIRequestor(
            api_key, api_version=fintecture_version, account=fintecture_account
        )
        url = "/v1/subscription_items/%s/usage_records" % subscription_item
        headers = util.populate_headers(idempotency_key)
        response, api_key = requestor.request("post", url, params, headers)

        return util.convert_to_fintecture_object(
            response, api_key, fintecture_version, fintecture_account
        )
