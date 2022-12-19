# File generated from our OpenAPI spec
from __future__ import absolute_import, division, print_function

from fintecture.api_resources.abstract import CreateableAPIResource
from fintecture.api_resources.abstract import DeletableAPIResource
from fintecture.api_resources.abstract import ListableAPIResource
from fintecture.api_resources.abstract import SearchableAPIResource
from fintecture.api_resources.abstract import UpdateableAPIResource
from fintecture.api_resources.account import Account
from fintecture.api_resources.account_holder import AccountHolder


class Customer(
    CreateableAPIResource,
    DeletableAPIResource,
    ListableAPIResource,
    SearchableAPIResource,
    UpdateableAPIResource,
):
    OBJECT_NAME = "customer"

    @classmethod
    def get_accounts(cls, customer_id, **params):
        return Account.search_by_customer(customer_id)

    @classmethod
    def get_account_holders(cls, customer_id, **params):
        return AccountHolder.search_by_customer(customer_id)

    @classmethod
    def get_account_transactions(cls, customer_id, account_id, **params):
        return Account.search_transactions_by_customer_account(
            customer_id, account_id
        )

    @classmethod
    def delete(cls, customer_id, **params):
        return Account.delete(customer_id, params)

    @classmethod
    def class_url(cls):
        return "/ais/v1/customer"
