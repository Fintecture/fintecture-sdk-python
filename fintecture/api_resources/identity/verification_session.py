# File generated from our OpenAPI spec
from __future__ import absolute_import, division, print_function

from fintecture import util
from fintecture.api_resources.abstract import CreateableAPIResource
from fintecture.api_resources.abstract import ListableAPIResource
from fintecture.api_resources.abstract import UpdateableAPIResource


class VerificationSession(
    CreateableAPIResource,
    ListableAPIResource,
    UpdateableAPIResource,
):
    OBJECT_NAME = "identity.verification_session"

    @classmethod
    def _cls_cancel(
        cls,
        session,
        api_key=None,
        fintecture_version=None,
        fintecture_account=None,
        **params
    ):
        return cls._static_request(
            "post",
            "/v1/identity/verification_sessions/{session}/cancel".format(
                session=util.sanitize_id(session)
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
            "/v1/identity/verification_sessions/{session}/cancel".format(
                session=util.sanitize_id(self.get("id"))
            ),
            idempotency_key=idempotency_key,
            params=params,
        )

    @classmethod
    def _cls_redact(
        cls,
        session,
        api_key=None,
        fintecture_version=None,
        fintecture_account=None,
        **params
    ):
        return cls._static_request(
            "post",
            "/v1/identity/verification_sessions/{session}/redact".format(
                session=util.sanitize_id(session)
            ),
            api_key=api_key,
            fintecture_version=fintecture_version,
            fintecture_account=fintecture_account,
            params=params,
        )

    @util.class_method_variant("_cls_redact")
    def redact(self, idempotency_key=None, **params):
        return self._request(
            "post",
            "/v1/identity/verification_sessions/{session}/redact".format(
                session=util.sanitize_id(self.get("id"))
            ),
            idempotency_key=idempotency_key,
            params=params,
        )
