from __future__ import absolute_import, division, print_function

import json

import pytest

import fintecture


class TestListObject(object):
    @pytest.fixture
    def list_object(self):
        return fintecture.ListObject.construct_from(
            {"object": "list", "url": "/my/path", "data": ["foo"]}, "myappid"
        )

    def test_list(self, request_mock, list_object):
        request_mock.stub_request(
            "get",
            "/my/path",
            {"object": "list", "data": [{"object": "charge", "foo": "bar"}]},
        )

        res = list_object.list(myparam="you")

        request_mock.assert_requested(
            "get", "/my/path", {"myparam": "you"}, None
        )
        assert isinstance(res, fintecture.ListObject)
        assert isinstance(res.data, list)
        assert isinstance(res.data[0], fintecture.Charge)
        assert res.data[0].foo == "bar"

    def test_create(self, request_mock, list_object):
        request_mock.stub_request(
            "post", "/my/path", {"object": "charge", "foo": "bar"}
        )

        res = list_object.create(myparam="eter")

        request_mock.assert_requested(
            "post", "/my/path", {"myparam": "eter"}, None
        )
        assert isinstance(res, fintecture.Charge)
        assert res.foo == "bar"

    def test_create_maintains_list_properties(self, request_mock, list_object):
        # Testing with real requests because our mock makes it impossible to
        # test otherwise
        charge = fintecture.Charge.retrieve("ch_123", app_id="test_custom")
        res = charge.refunds.create(amount=123)
        request_mock.assert_requested(
            "post", "/v1/charges/ch_123/refunds", {"amount": 123}, None
        )
        assert res.app_id == "test_custom"

    def test_retrieve(self, request_mock, list_object):
        request_mock.stub_request(
            "get", "/my/path/myid", {"object": "charge", "foo": "bar"}
        )

        res = list_object.retrieve(
            "myid", myparam="cow"
        )

        request_mock.assert_requested(
            "get", "/my/path/myid", {"myparam": "cow"}, None
        )
        assert isinstance(res, fintecture.Charge)
        assert res.foo == "bar"

    def test_is_empty(self):
        lo = fintecture.ListObject.construct_from({"data": []}, None)
        assert lo.is_empty is True

    def test_empty_list(self):
        lo = fintecture.ListObject.empty_list()
        assert lo.is_empty

    def test_iter(self):
        arr = [{"id": 1}, {"id": 2}, {"id": 3}]
        expected = fintecture.util.convert_to_fintecture_object(arr)
        lo = fintecture.ListObject.construct_from({"data": arr}, None)
        assert list(lo) == expected

    def test_iter_reversed(self):
        arr = [{"id": 1}, {"id": 2}, {"id": 3}]
        expected = fintecture.util.convert_to_fintecture_object(list(reversed(arr)))
        lo = fintecture.ListObject.construct_from({"data": arr}, None)
        assert list(reversed(lo)) == expected

    def test_len(self, list_object):
        assert len(list_object) == 1

    def test_bool(self, list_object):
        assert list_object

        empty = fintecture.ListObject.construct_from(
            {"object": "list", "url": "/my/path", "data": []}, "myappid"
        )
        assert bool(empty) is False

    def test_next_page(self, request_mock):
        lo = fintecture.ListObject.construct_from(
            {
                "object": "list",
                "data": [{"id": 1}],
                "has_more": True,
                "url": "/things",
            },
            None,
        )

        request_mock.stub_request(
            "get",
            "/things",
            {
                "object": "list",
                "data": [{"id": 2}],
                "has_more": False,
                "url": "/things",
            },
        )

        next_lo = lo.next_page()
        assert not next_lo.is_empty
        assert next_lo.data[0].id == 2

    def test_next_page_with_filters(self, request_mock):
        lo = fintecture.ListObject.construct_from(
            {
                "object": "list",
                "data": [{"id": 1}],
                "has_more": True,
                "url": "/things",
            },
            None,
        )
        lo._retrieve_params = {"expand": ["data.source"], "limit": 3}

        request_mock.stub_request(
            "get",
            "/things",
            {
                "object": "list",
                "data": [{"id": 2}],
                "has_more": False,
                "url": "/things",
            },
        )

        next_lo = lo.next_page()
        assert next_lo._retrieve_params == {
            "expand": ["data.source"],
            "limit": 3,
            "starting_after": 1,
        }

    def test_next_page_empty_list(self):
        lo = fintecture.ListObject.construct_from(
            {
                "object": "list",
                "data": [{"id": 1}],
                "has_more": False,
                "url": "/things",
            },
            None,
        )

        next_lo = lo.next_page()
        assert next_lo == fintecture.ListObject.empty_list()

    def test_prev_page(self, request_mock):
        lo = fintecture.ListObject.construct_from(
            {
                "object": "list",
                "data": [{"id": 2}],
                "has_more": True,
                "url": "/things",
            },
            None,
        )

        request_mock.stub_request(
            "get",
            "/things",
            {
                "object": "list",
                "data": [{"id": 1}],
                "has_more": False,
                "url": "/things",
            },
        )

        previous_lo = lo.previous_page()
        assert not previous_lo.is_empty
        assert previous_lo.data[0].id == 1

    def test_prev_page_with_filters(self, request_mock):
        lo = fintecture.ListObject.construct_from(
            {
                "object": "list",
                "data": [{"id": 2}],
                "has_more": True,
                "url": "/things",
            },
            None,
        )
        lo._retrieve_params = {"expand": ["data.source"], "limit": 3}

        request_mock.stub_request(
            "get",
            "/things",
            {
                "object": "list",
                "data": [{"id": 1}],
                "has_more": False,
                "url": "/things",
            },
        )

        previous_lo = lo.previous_page()
        assert previous_lo._retrieve_params == {
            "expand": ["data.source"],
            "limit": 3,
            "ending_before": 2,
        }

    def test_serialize_empty_list(self):
        empty = fintecture.ListObject.construct_from(
            {"object": "list", "data": []}, "myappid"
        )
        serialized = str(empty)
        deserialized = fintecture.ListObject.construct_from(
            json.loads(serialized), "myappid"
        )
        assert deserialized == empty

    def test_serialize_nested_empty_list(self):
        empty = fintecture.ListObject.construct_from(
            {"object": "list", "data": []}, "myappid"
        )
        obj = fintecture.fintecture_object.FintectureObject.construct_from(
            {"nested": empty}, "myappid"
        )
        serialized = str(obj)
        deserialized = fintecture.fintecture_object.FintectureObject.construct_from(
            json.loads(serialized), "myappid"
        )
        assert deserialized.nested == empty


class TestAutoPaging:
    @staticmethod
    def pageable_model_response(ids, has_more):
        return {
            "object": "list",
            "url": "/v1/pageablemodels",
            "data": [{"id": id, "object": "pageablemodel"} for id in ids],
            "has_more": has_more,
        }

    def test_iter_one_page(self, request_mock):
        lo = fintecture.ListObject.construct_from(
            self.pageable_model_response(["pm_123", "pm_124"], False), "myappid"
        )

        request_mock.assert_no_request()

        seen = [item["id"] for item in lo.auto_paging_iter()]

        assert seen == ["pm_123", "pm_124"]

    def test_iter_two_pages(self, request_mock):
        lo = fintecture.ListObject.construct_from(
            self.pageable_model_response(["pm_123", "pm_124"], True), "myappid"
        )
        lo._retrieve_params = {"foo": "bar"}

        request_mock.stub_request(
            "get",
            "/v1/pageablemodels",
            self.pageable_model_response(["pm_125", "pm_126"], False),
        )

        seen = [item["id"] for item in lo.auto_paging_iter()]

        request_mock.assert_requested(
            "get",
            "/v1/pageablemodels",
            {"starting_after": "pm_124", "foo": "bar"},
            None,
        )

        assert seen == ["pm_123", "pm_124", "pm_125", "pm_126"]

    def test_iter_reverse(self, request_mock):
        lo = fintecture.ListObject.construct_from(
            self.pageable_model_response(["pm_125", "pm_126"], True), "myappid"
        )
        lo._retrieve_params = {"foo": "bar", "ending_before": "pm_127"}

        request_mock.stub_request(
            "get",
            "/v1/pageablemodels",
            self.pageable_model_response(["pm_123", "pm_124"], False),
        )

        seen = [item["id"] for item in lo.auto_paging_iter()]

        request_mock.assert_requested(
            "get",
            "/v1/pageablemodels",
            {"ending_before": "pm_125", "foo": "bar"},
            None,
        )

        assert seen == ["pm_126", "pm_125", "pm_124", "pm_123"]

    def test_class_method_two_pages(self, request_mock):
        request_mock.stub_request(
            "get",
            "/v1/charges",
            {
                "object": "list",
                "data": [{"id": "ch_001"}],
                "url": "/v1/charges",
                "has_more": False,
            },
        )

        seen = [
            item["id"]
            for item in fintecture.Charge.auto_paging_iter(limit=25, foo="bar")
        ]

        request_mock.assert_requested(
            "get", "/v1/charges", {"limit": 25, "foo": "bar"}
        )
        assert seen == ["ch_001"]
