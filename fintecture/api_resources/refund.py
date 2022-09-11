# File generated from our OpenAPI spec
from __future__ import absolute_import, division, print_function

from fintecture import util
from fintecture.api_resources.abstract import APIResourceTestHelpers
from fintecture.api_resources.abstract import CreateableAPIResource
from fintecture.api_resources.abstract import ListableAPIResource
from fintecture.api_resources.abstract import UpdateableAPIResource
from fintecture.api_resources.abstract import test_helpers


@test_helpers
class Refund(
    CreateableAPIResource, ListableAPIResource, UpdateableAPIResource
):
    OBJECT_NAME = "refund"

    @classmethod
    def _cls_cancel(
        cls,
        refund,
        api_key=None,
        fintecture_version=None,
        fintecture_account=None,
        **params
    ):
        return cls._static_request(
            "post",
            "/v1/refunds/{refund}/cancel".format(
                refund=util.sanitize_id(refund)
            ),
            api_key=api_key,
            fintecture_version=fintecture_version,
            fintecture_account=fintecture_account,
            params=params,
        )

    @util.class_method_variant("_cls_cancel")
    def cancel(self, idempotency_key=None, **params):
        return self._request(
            "post",
            "/v1/refunds/{refund}/cancel".format(
                refund=util.sanitize_id(self.get("id"))
            ),
            idempotency_key=idempotency_key,
            params=params,
        )

    class TestHelpers(APIResourceTestHelpers):
        @classmethod
        def _cls_expire(
            cls,
            refund,
            api_key=None,
            fintecture_version=None,
            fintecture_account=None,
            **params
        ):
            return cls._static_request(
                "post",
                "/v1/test_helpers/refunds/{refund}/expire".format(
                    refund=util.sanitize_id(refund)
                ),
                api_key=api_key,
                fintecture_version=fintecture_version,
                fintecture_account=fintecture_account,
                params=params,
            )

        @util.class_method_variant("_cls_expire")
        def expire(self, idempotency_key=None, **params):
            return self.resource._request(
                "post",
                "/v1/test_helpers/refunds/{refund}/expire".format(
                    refund=util.sanitize_id(self.resource.get("id"))
                ),
                idempotency_key=idempotency_key,
                params=params,
            )
