# File generated from our OpenAPI spec
from __future__ import absolute_import, division, print_function

from fintecture.api_resources.abstract import ListableAPIResource
from fintecture.api_resources.abstract import SearchableAPIResource


class TestAccount(
    ListableAPIResource,
    SearchableAPIResource,
):
    OBJECT_NAME = "testaccount"

    @classmethod
    def search(cls, *args, **kwargs):
        return cls._search(search_url="/res/v1/testaccounts", *args, **kwargs)
