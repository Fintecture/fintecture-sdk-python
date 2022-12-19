from __future__ import absolute_import, division, print_function

from fintecture.api_resources.abstract.api_resource import APIResource


class ListableAPIResource(APIResource):
    @classmethod
    def auto_paging_iter(cls, *args, **params):
        return cls.list(*args, **params).auto_paging_iter()

    @classmethod
    def list(
        cls, app_id=None, fintecture_version=None, **params
    ):
        return cls._static_request(
            "get",
            cls.class_url(),
            app_id=app_id,
            fintecture_version=fintecture_version,
            params=params,
        )
