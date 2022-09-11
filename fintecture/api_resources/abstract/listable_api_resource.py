from __future__ import absolute_import, division, print_function

from fintecture.api_resources.abstract.api_resource import APIResource


class ListableAPIResource(APIResource):
    @classmethod
    def auto_paging_iter(cls, *args, **params):
        return cls.list(*args, **params).auto_paging_iter()

    @classmethod
    def list(
        cls, api_key=None, fintecture_version=None, fintecture_account=None, **params
    ):
        return cls._static_request(
            "get",
            cls.class_url(),
            api_key=api_key,
            fintecture_version=fintecture_version,
            fintecture_account=fintecture_account,
            params=params,
        )
