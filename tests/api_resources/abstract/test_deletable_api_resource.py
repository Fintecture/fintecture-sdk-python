from __future__ import absolute_import, division, print_function

import fintecture


class TestDeletableAPIResource(object):
    class MyDeletable(fintecture.api_resources.abstract.DeletableAPIResource):
        OBJECT_NAME = "mydeletable"

    def test_delete_class(self, request_mock):
        request_mock.stub_request(
            "delete",
            "/v1/mydeletables/mid",
            {"id": "mid", "deleted": True},
            rheaders={"x-request-id": "req_id"},
        )

        obj = self.MyDeletable.delete("mid")

        request_mock.assert_requested("delete", "/v1/mydeletables/mid", {})
        assert obj.deleted is True
        assert obj.id == "mid"

        assert obj.last_response is not None
        assert obj.last_response.x_request_id == "req_id"

    def test_delete_class_with_object(self, request_mock):
        request_mock.stub_request(
            "delete",
            "/v1/mydeletables/mid",
            {"id": "mid", "deleted": True},
            rheaders={"x-request-id": "req_id"},
        )

        obj = self.MyDeletable.construct_from({"id": "mid"}, "mykey")

        self.MyDeletable.delete(obj)

        request_mock.assert_requested("delete", "/v1/mydeletables/mid", {})
        assert obj.deleted is True
        assert obj.id == "mid"

        assert obj.last_response is not None
        assert obj.last_response.x_request_id == "req_id"

    def test_delete_instance(self, request_mock):
        request_mock.stub_request(
            "delete",
            "/v1/mydeletables/mid",
            {"id": "mid", "deleted": True},
            rheaders={"x-request-id": "req_id"},
        )

        obj = self.MyDeletable.construct_from({"id": "mid"}, "mykey")

        assert obj is obj.delete()
        request_mock.assert_requested("delete", "/v1/mydeletables/mid", {})
        assert obj.deleted is True
        assert obj.id == "mid"

        assert obj.last_response is not None
        assert obj.last_response.x_request_id == "req_id"

    def test_delete_with_all_special_fields(self, request_mock):
        request_mock.stub_request(
            "delete",
            "/v1/mydeletables/foo",
            {"id": "foo", "bobble": "new_scrobble"},
            {},
        )

        self.MyDeletable.delete(
            "foo",
            fintecture_version="2017-08-15",
            app_id="APP_ID",
            bobble="new_scrobble",
        )

        request_mock.assert_requested(
            "delete",
            "/v1/mydeletables/foo",
            {"bobble": "new_scrobble"},
        )
        request_mock.assert_api_version("2017-08-15")
