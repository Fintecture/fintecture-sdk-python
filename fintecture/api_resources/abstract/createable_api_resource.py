from __future__ import absolute_import, division, print_function

from fintecture.api_resources.abstract.api_resource import APIResource


class CreateableAPIResource(APIResource):
    @classmethod
    def create(
        cls,
        api_key=None,
        idempotency_key=None,
        fintecture_version=None,
        fintecture_account=None,
        **params
    ):
        return cls._static_request(
            "post",
            cls.class_url(),
            api_key,
            idempotency_key,
            fintecture_version,
            fintecture_account,
            params,
        )
