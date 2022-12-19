from __future__ import absolute_import, division, print_function

from fintecture.api_resources.abstract.api_resource import APIResource


class SearchableAPIResource(APIResource):
    @classmethod
    def _search(
        cls,
        search_url,
        app_id=None,
        fintecture_version=None,
        **params
    ):
        return cls._static_request(
            "get",
            search_url,
            app_id=app_id,
            fintecture_version=fintecture_version,
            params=params,
        )
