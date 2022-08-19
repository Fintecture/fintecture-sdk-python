# File generated from our OpenAPI spec
from __future__ import absolute_import, division, print_function

from fintecture.api_resources.abstract import CreateableAPIResource
from fintecture.api_resources.abstract import DeletableAPIResource
from fintecture.api_resources.abstract import ListableAPIResource
from fintecture.api_resources.abstract import UpdateableAPIResource


class Account(
    CreateableAPIResource,
    DeletableAPIResource,
    ListableAPIResource,
    UpdateableAPIResource,
):
    OBJECT_NAME = "account"

    @classmethod
    def search_by_customer(cls, customer_id, **params):
        return cls._static_request(
            "get",
            "/ais/v1/customer/{}/accounts".format(
                customer_id
            ),
            params=params,
        )

    @classmethod
    def search_transactions_by_customer_account(cls, customer_id, account_id, **params):
        return cls._static_request(
            "get",
            "/ais/v1/customer/{}/accounts/{}/transactions".format(
                customer_id,
                account_id
            ),
            params=params,
        )

    @classmethod
    def delete(cls, customer_id, **params):
        return cls._cls_delete(customer_id, **params)

    @classmethod
    def search(cls, *args, **kwargs):
        return cls._search(search_url="/res/v1/providers", *args, **kwargs)

    @classmethod
    def search_auto_paging_iter(cls, *args, **kwargs):
        return cls.search(*args, **kwargs).auto_paging_iter()
