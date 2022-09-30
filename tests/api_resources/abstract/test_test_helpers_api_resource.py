from __future__ import absolute_import, division, print_function

import fintecture
import pytest
from fintecture import util
from fintecture.api_resources.abstract import APIResourceTestHelpers


class TestTestHelperAPIResource(object):
    @fintecture.api_resources.abstract.test_helpers
    class MyTestHelpersResource(fintecture.api_resources.abstract.APIResource):
        OBJECT_NAME = "myresource"

        @fintecture.api_resources.abstract.custom_method(
            "do_stuff", http_verb="post", http_path="do_the_thing"
        )
        class TestHelpers(APIResourceTestHelpers):
            def __init__(self, resource):
                self.resource = resource

            def do_stuff(self, **params):
                url = self.instance_url() + "/do_the_thing"
                self.resource.refresh_from(
                    self.resource.request("post", url, params, {})
                )
                return self.resource

    def test_call_custom_method_class(self, request_mock):
        request_mock.stub_request(
            "post",
            "/v1/test_helpers/myresources/mid/do_the_thing",
            {"id": "mid", "thing_done": True},
            rheaders={"x-request-id": "req_id"},
        )

        obj = self.MyTestHelpersResource.TestHelpers.do_stuff("mid", foo="bar")

        request_mock.assert_requested(
            "post",
            "/v1/test_helpers/myresources/mid/do_the_thing",
            {"foo": "bar"},
        )
        assert obj.thing_done is True

    def test_call_custom_method_instance_via_property(self, request_mock):
        request_mock.stub_request(
            "post",
            "/v1/test_helpers/myresources/mid/do_the_thing",
            {"id": "mid", "thing_done": True},
            rheaders={"x-request-id": "req_id"},
        )

        obj = self.MyTestHelpersResource.construct_from({"id": "mid"}, "mykey")
        obj.test_helpers.do_stuff(foo="bar")

        request_mock.assert_requested(
            "post",
            "/v1/test_helpers/myresources/mid/do_the_thing",
            {"foo": "bar"},
        )
        assert obj.thing_done is True

    def test_helper_decorator_raises_for_non_resource(self):
        with pytest.raises(ValueError):
            fintecture.api_resources.abstract.test_helpers(str)
