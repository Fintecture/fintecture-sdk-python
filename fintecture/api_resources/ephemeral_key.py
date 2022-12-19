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
        app_id=None,
        fintecture_version=None,
        **params
    ):
        if fintecture_version is None:
            raise ValueError(
                "fintecture_version must be specified to create an ephemeral "
                "key"
            )

        requestor = api_requestor.APIRequestor(
            app_id, api_version=fintecture_version
        )

        url = cls.class_url()
        response, my_app_id = requestor.request("post", url, params, {})
        return util.convert_to_fintecture_object(
            response, my_app_id, fintecture_version
        )
