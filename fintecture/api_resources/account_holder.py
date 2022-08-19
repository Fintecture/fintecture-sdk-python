# File generated from our OpenAPI spec
from __future__ import absolute_import, division, print_function

from fintecture.api_resources.abstract import CreateableAPIResource
from fintecture.api_resources.abstract import DeletableAPIResource
from fintecture.api_resources.abstract import ListableAPIResource
from fintecture.api_resources.abstract import UpdateableAPIResource


class AccountHolder(
    CreateableAPIResource,
    DeletableAPIResource,
    ListableAPIResource,
    UpdateableAPIResource,
):
    OBJECT_NAME = "accountholder"

    @classmethod
    def search_by_customer(cls, customer_id, **params):
        return cls._static_request(
            "get",
            "/ais/v1/customer/{}/accountholders".format(
                customer_id
            ),
            params=params,
        )
