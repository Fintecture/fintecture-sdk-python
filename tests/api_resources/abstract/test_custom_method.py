from __future__ import absolute_import, division, print_function

import fintecture
from fintecture import util


class TestCustomMethod(object):
    @fintecture.api_resources.abstract.custom_method(
        "do_stuff", http_verb="post", http_path="do_the_thing"
    )
    @fintecture.api_resources.abstract.custom_method(
        "do_list_stuff", http_verb="get", http_path="do_the_list_thing"
    )
    class MyResource(fintecture.api_resources.abstract.APIResource):
        OBJECT_NAME = "myresource"

        def do_stuff(self, **params):
            url = self.instance_url() + "/do_the_thing"
            self.refresh_from(self.request("post", url, params, {}))
            return self

        @classmethod
        def _cls_do_stuff_new_codegen(
            cls,
            id,
            app_id=None,
            fintecture_version=None,
            **params
        ):
            return cls._static_request(
                "post",
                "/v1/myresources/{id}/do_the_thing".format(
                    id=util.sanitize_id(id)
                ),
                app_id=app_id,
                fintecture_version=fintecture_version,
                params=params,
            )

        @util.class_method_variant("_cls_do_stuff_new_codegen")
        def do_stuff_new_codegen(self, **params):
            return self._request(
                "post",
                "/v1/myresources/{id}/do_the_thing".format(
                    id=util.sanitize_id(self.get("id"))
                ),
                params=params,
            )

    def test_call_custom_method_class(self, request_mock):
        request_mock.stub_request(
            "post",
            "/v1/myresources/mid/do_the_thing",
            {"id": "mid", "thing_done": True},
            rheaders={"x-request-id": "req_id"},
        )

        obj = self.MyResource.do_stuff("mid", foo="bar")

        request_mock.assert_requested(
            "post", "/v1/myresources/mid/do_the_thing", {"foo": "bar"}
        )
        assert obj.thing_done is True

    def test_call_custom_list_method_class_paginates(self, request_mock):
        request_mock.stub_request(
            "get",
            "/v1/myresources/mid/do_the_list_thing",
            {
                "object": "list",
                "url": "/v1/myresources/mid/do_the_list_thing",
                "has_more": True,
                "data": [
                    {"id": "cus_1", "object": "customer"},
                    {"id": "cus_2", "object": "customer"},
                ],
            },
            rheaders={"x-request-id": "req_123"},
        )

        resp = self.MyResource.do_list_stuff("mid", param1="abc", param2="def")

        request_mock.assert_requested(
            "get",
            "/v1/myresources/mid/do_the_list_thing",
            {"param1": "abc", "param2": "def"},
        )

        # Stub out the second request which will happen automatically.
        request_mock.stub_request(
            "get",
            "/v1/myresources/mid/do_the_list_thing",
            {
                "object": "list",
                "url": "/v1/myresources/mid/do_the_list_thing",
                "has_more": False,
                "data": [
                    {"id": "cus_3", "object": "customer"},
                ],
            },
            rheaders={"x-request-id": "req_123"},
        )

        # Iterate through entire content
        ids = []
        for i in resp.auto_paging_iter():
            ids.append(i.id)

        # Explicitly assert that the pagination parameter were kept for the
        # second request along with the starting_after param.
        request_mock.assert_requested(
            "get",
            "/v1/myresources/mid/do_the_list_thing",
            {"starting_after": "cus_2", "param1": "abc", "param2": "def"},
        )

        assert ids == ["cus_1", "cus_2", "cus_3"]

    def test_call_custom_method_class_with_object(self, request_mock):
        request_mock.stub_request(
            "post",
            "/v1/myresources/mid/do_the_thing",
            {"id": "mid", "thing_done": True},
            rheaders={"x-request-id": "req_id"},
        )

        obj = self.MyResource.construct_from({"id": "mid"}, "mykey")
        self.MyResource.do_stuff(obj, foo="bar")

        request_mock.assert_requested(
            "post", "/v1/myresources/mid/do_the_thing", {"foo": "bar"}
        )
        assert obj.thing_done is True

    def test_call_custom_method_instance(self, request_mock):
        request_mock.stub_request(
            "post",
            "/v1/myresources/mid/do_the_thing",
            {"id": "mid", "thing_done": True},
            rheaders={"x-request-id": "req_id"},
        )

        obj = self.MyResource.construct_from({"id": "mid"}, "mykey")
        obj.do_stuff(foo="bar")

        request_mock.assert_requested(
            "post", "/v1/myresources/mid/do_the_thing", {"foo": "bar"}
        )
        assert obj.thing_done is True

    def test_call_custom_method_class_special_fields(self, request_mock):
        request_mock.stub_request(
            "post",
            "/v1/myresources/mid/do_the_thing",
            {"id": "mid", "thing_done": True},
            rheaders={"x-request-id": "req_id"},
        )

        self.MyResource.do_stuff(
            "mid",
            foo="bar",
            fintecture_version="2017-08-15",
            app_id="APP_ID",
        )

        request_mock.assert_requested(
            "post",
            "/v1/myresources/mid/do_the_thing",
            {"foo": "bar"},
        )
        request_mock.assert_api_version("2017-08-15")

    def test_call_custom_method_class_newcodegen_special_fields(
        self, request_mock
    ):
        request_mock.stub_request(
            "post",
            "/v1/myresources/mid/do_the_thing",
            {"id": "mid", "thing_done": True},
            rheaders={"x-request-id": "req_id"},
        )

        self.MyResource.do_stuff_new_codegen(
            "mid",
            foo="bar",
            fintecture_version="2017-08-15",
            app_id="APP_ID",
        )

        request_mock.assert_requested(
            "post",
            "/v1/myresources/mid/do_the_thing",
            {"foo": "bar"},
        )
        request_mock.assert_api_version("2017-08-15")

    def test_call_custom_method_instance_newcodegen_special_fields(
        self, request_mock
    ):
        request_mock.stub_request(
            "post",
            "/v1/myresources/mid/do_the_thing",
            {"id": "mid", "thing_done": True},
            rheaders={"x-request-id": "req_id"},
        )

        obj = self.MyResource.construct_from({"id": "mid"}, "mykey")
        obj.do_stuff_new_codegen(
            foo="bar",
            fintecture_version="2017-08-15",
            app_id="APP_ID",
            headers={"extra_header": "val"},
        )

        request_mock.assert_requested(
            "post",
            "/v1/myresources/mid/do_the_thing",
            {"foo": "bar"},
            {"extra_header": "val"},
        )
        request_mock.assert_api_version("2017-08-15")
