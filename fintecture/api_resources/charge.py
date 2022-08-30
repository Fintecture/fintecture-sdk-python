# File generated from our OpenAPI spec
from __future__ import absolute_import, division, print_function

from fintecture import util
from fintecture.api_resources.abstract import CreateableAPIResource
from fintecture.api_resources.abstract import ListableAPIResource
from fintecture.api_resources.abstract import SearchableAPIResource
from fintecture.api_resources.abstract import UpdateableAPIResource


class Charge(
    CreateableAPIResource,
    ListableAPIResource,
    SearchableAPIResource,
    UpdateableAPIResource,
):
    OBJECT_NAME = "charge"

    @classmethod
    def _cls_capture(
        cls,
        charge,
        app_id=None,
        fintecture_version=None,
        **params
    ):
        return cls._static_request(
            "post",
            "/v1/charges/{charge}/capture".format(
                charge=util.sanitize_id(charge)
            ),
            app_id=app_id,
            fintecture_version=fintecture_version,
            params=params,
        )

    @util.class_method_variant("_cls_capture")
    def capture(self, **params):
        return self._request(
            "post",
            "/v1/charges/{charge}/capture".format(
                charge=util.sanitize_id(self.get("id"))
            ),
            params=params,
        )

    @classmethod
    def search(cls, *args, **kwargs):
        return cls._search(search_url="/v1/charges/search", *args, **kwargs)

    @classmethod
    def search_auto_paging_iter(cls, *args, **kwargs):
        return cls.search(*args, **kwargs).auto_paging_iter()

    def mark_as_fraudulent(self):
        params = {"fraud_details": {"user_report": "fraudulent"}}
        url = self.instance_url()
        headers = {}
        self.refresh_from(self.request("post", url, params, headers))
        return self

    def mark_as_safe(self):
        params = {"fraud_details": {"user_report": "safe"}}
        url = self.instance_url()
        headers = {}
        self.refresh_from(self.request("post", url, params, headers))
        return self
