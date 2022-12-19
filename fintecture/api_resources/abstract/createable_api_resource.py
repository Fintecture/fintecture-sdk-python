from __future__ import absolute_import, division, print_function

from fintecture.api_resources.abstract.api_resource import APIResource


class CreateableAPIResource(APIResource):
    @classmethod
    def create(
        cls,
        app_id=None,
        fintecture_version=None,
        **params
    ):
        return cls._static_request(
            "post",
            cls.class_url(),
            app_id,
            fintecture_version,
            params,
        )
