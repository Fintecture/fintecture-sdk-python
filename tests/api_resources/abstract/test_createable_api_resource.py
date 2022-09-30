from __future__ import absolute_import, division, print_function

import fintecture


class TestCreateableAPIResource(object):
    class MyCreatable(fintecture.api_resources.abstract.CreateableAPIResource):
        OBJECT_NAME = "mycreatable"

    def test_create(self, request_mock):
        request_mock.stub_request(
            "post",
            "/v1/mycreatables",
            {"object": "charge", "foo": "bar"},
            rheaders={"x-request-id": "req_id"},
        )

        res = self.MyCreatable.create()

        request_mock.assert_requested("post", "/v1/mycreatables", {})
        assert isinstance(res, fintecture.Charge)
        assert res.foo == "bar"

        assert res.last_response is not None
        assert res.last_response.x_request_id == "req_id"

    def test_idempotent_create(self, request_mock):
        request_mock.stub_request(
            "post",
            "/v1/mycreatables",
            {"object": "charge", "foo": "bar"},
            rheaders={},
        )

        res = self.MyCreatable.create()

        request_mock.assert_requested(
            "post", "/v1/mycreatables", {}, {}
        )
        assert isinstance(res, fintecture.Charge)
        assert res.foo == "bar"
