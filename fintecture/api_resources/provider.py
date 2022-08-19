# File generated from our OpenAPI spec
from __future__ import absolute_import, division, print_function

from fintecture.api_resources.abstract import ListableAPIResource
from fintecture.api_resources.abstract import SearchableAPIResource


class Provider(
    ListableAPIResource,
    SearchableAPIResource,
):
    OBJECT_NAME = "provider"

    @classmethod
    def search(cls, *args, **kwargs):
        return cls._search(search_url="/res/v1/providers", *args, **kwargs)

    @classmethod
    def search_auto_paging_iter(cls, *args, **kwargs):
        return cls.search(*args, **kwargs).auto_paging_iter()
