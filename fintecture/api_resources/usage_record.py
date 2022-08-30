# File generated from our OpenAPI spec
from __future__ import absolute_import, division, print_function

from fintecture import api_requestor, util
from fintecture.api_resources.abstract import APIResource


class UsageRecord(APIResource):
    OBJECT_NAME = "usage_record"

    @classmethod
    def create(
        cls,
        app_id=None,
        fintecture_version=None,
        **params
    ):
        if "subscription_item" not in params:
            raise ValueError("Params must have a subscription_item key")

        subscription_item = params.pop("subscription_item")

        requestor = api_requestor.APIRequestor(
            app_id, api_version=fintecture_version
        )
        url = "/v1/subscription_items/%s/usage_records" % subscription_item
        response, my_app_id = requestor.request("post", url, params, {})

        return util.convert_to_fintecture_object(
            response, my_app_id, fintecture_version
        )
