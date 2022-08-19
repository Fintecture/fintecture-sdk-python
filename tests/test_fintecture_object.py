from __future__ import absolute_import, division, print_function

import datetime
import json
import pickle
from copy import copy, deepcopy

import pytest

import fintecture
from fintecture import six


SAMPLE_INVOICE = json.loads(
    """
{
  "amount_due": 1305,
  "attempt_count": 0,
  "attempted": true,
  "charge": "ch_wajkQ5aDTzFs5v",
  "closed": true,
  "customer": "cus_osllUe2f1BzrRT",
  "date": 1338238728,
  "discount": null,
  "ending_balance": 0,
  "id": "in_t9mHb2hpK7mml1",
  "livemode": false,
  "next_payment_attempt": null,
  "object": "invoice",
  "paid": true,
  "period_end": 1338238728,
  "period_start": 1338238716,
  "starting_balance": -8695,
  "subtotal": 10000,
  "total": 10000,
  "lines": {
    "object": "list",
    "data": [
      {
        "id": "il_1LSiex2eZvKYlo2CZ5IspTNx",
        "object": "line_item",
        "amount": 2499,
        "amount_excluding_tax": 2499,
        "currency": "usd",
        "description": "My First Invoice Item (created for API docs)",
        "discount_amounts": [],
        "discountable": true,
        "discounts": [],
        "invoice_item": "ii_1LSiex2eZvKYlo2C0X4adTLR",
        "livemode": false,
        "metadata": {},
        "period": {
          "end": 1659537295,
          "start": 1659537295
        },
        "price": {
          "id": "price_1LSicu2eZvKYlo2C4WSIaXEp",
          "object": "price",
          "active": true,
          "billing_scheme": "per_unit",
          "created": 1659537168,
          "currency": "usd",
          "custom_unit_amount": null,
          "livemode": false,
          "lookup_key": null,
          "metadata": {},
          "nickname": null,
          "product": "prod_MB4mvosUV5tObf",
          "recurring": null,
          "tax_behavior": "unspecified",
          "tiers_mode": null,
          "transform_quantity": null,
          "type": "one_time",
          "unit_amount": 2499,
          "unit_amount_decimal": "2499"
        },
        "proration": false,
        "proration_details": {
          "credited_items": null
        },
        "quantity": 1,
        "subscription": null,
        "tax_amounts": [],
        "tax_rates": [],
        "type": "invoiceitem",
        "unit_amount_excluding_tax": "2499"
      }
    ],
    "has_more": false,
    "url": "/v1/invoices/in_t9mHb2hpK7mml1/lines"
  }
}
"""
)


class TestFintectureObject(object):
    def test_initializes_with_parameters(self):
        obj = fintecture.fintecture_object.FintectureObject(
            "foo", "bar", myparam=5, yourparam="boo"
        )

        assert obj.id == "foo"
        assert obj.api_key == "bar"

    def test_access(self):
        obj = fintecture.fintecture_object.FintectureObject("myid", "mykey", myparam=5)

        # Empty
        with pytest.raises(AttributeError):
            obj.myattr
        with pytest.raises(KeyError):
            obj["myattr"]
        assert obj.get("myattr", "def") == "def"
        assert obj.get("myattr") is None

        # Setters
        obj.myattr = "myval"
        obj["myitem"] = "itval"
        assert obj.setdefault("mydef", "sdef") == "sdef"

        # Getters
        assert obj.setdefault("myattr", "sdef") == "myval"
        assert obj.myattr == "myval"
        assert obj["myattr"] == "myval"
        assert obj.get("myattr") == "myval"

        assert sorted(obj.keys()) == ["id", "myattr", "mydef", "myitem"]

        assert sorted(obj.values()) == ["itval", "myid", "myval", "sdef"]

        # Illegal operations
        with pytest.raises(ValueError):
            obj.foo = ""

    def test_refresh_from(self, mocker):
        obj = fintecture.fintecture_object.FintectureObject.construct_from(
            {"foo": "bar", "trans": "me"}, "myappid"
        )

        assert obj.api_key == "mykey"
        assert obj.foo == "bar"
        assert obj["trans"] == "me"
        assert obj.fintecture_version is None
        assert obj.fintecture_account is None
        assert obj.last_response is None

        last_response = mocker.Mock()
        obj.refresh_from(
            {"foo": "baz", "johnny": 5},
            "key2",
            fintecture_version="2017-08-15",
            fintecture_account="acct_foo",
            last_response=last_response,
        )

        assert obj.johnny == 5
        assert obj.foo == "baz"
        with pytest.raises(AttributeError):
            obj.trans
        assert obj.api_key == "key2"
        assert obj.fintecture_version == "2017-08-15"
        assert obj.fintecture_account == "acct_foo"
        assert obj.last_response == last_response

        obj.refresh_from(
            {"trans": 4, "metadata": {"amount": 42}}, "key2", True
        )

        assert obj.foo == "baz"
        assert obj.trans == 4

    def test_passing_nested_refresh(self):
        obj = fintecture.fintecture_object.FintectureObject.construct_from(
            {"foos": {"type": "list", "data": [{"id": "nested"}]}},
            "app_id",
            fintecture_account="acct_foo",
        )

        nested = obj.foos.data[0]

        assert obj.api_key == "key"
        assert nested.id == "nested"
        assert nested.api_key == "key"
        assert nested.fintecture_account == "acct_foo"

    def test_refresh_from_nested_object(self):
        obj = fintecture.fintecture_object.FintectureObject.construct_from(
            SAMPLE_INVOICE, "app_id"
        )

        assert len(obj.lines) == 1
        assert isinstance(obj.lines, fintecture.ListObject)
        assert isinstance(obj.lines.data[0], fintecture.InvoiceLineItem)
        assert isinstance(
            obj.lines.data[0].price, fintecture.fintecture_object.FintectureObject
        )
        assert isinstance(obj.lines.data[0].price, fintecture.Price)
        assert obj.lines.data[0].price.billing_scheme == "per_unit"

    def test_refresh_from_nested_object_can_be_paged(self):
        obj = fintecture.fintecture_object.FintectureObject.construct_from(
            SAMPLE_INVOICE, "app_id"
        )

        assert len(obj.lines) == 1
        assert isinstance(obj.lines, fintecture.ListObject)
        seen = [item["id"] for item in obj.lines.auto_paging_iter()]

        assert seen == ["il_1LSiex2eZvKYlo2CZ5IspTNx"]

        assert isinstance(obj.lines.data[0], fintecture.InvoiceLineItem)
        assert isinstance(
            obj.lines.data[0].price, fintecture.fintecture_object.FintectureObject
        )
        assert isinstance(obj.lines.data[0].price, fintecture.Price)
        assert obj.lines.data[0].price.billing_scheme == "per_unit"

    def test_to_json(self):
        obj = fintecture.fintecture_object.FintectureObject.construct_from(
            SAMPLE_INVOICE, "app_id"
        )

        self.check_invoice_data(json.loads(str(obj)))

    def check_invoice_data(self, data):
        # Check rough structure
        assert len(list(data.keys())) == 20
        assert len(list(data["lines"]["data"][0].keys())) == 22
        assert len(data["lines"]["data"]) == 1

        # Check various data types
        assert data["date"] == 1338238728
        assert data["next_payment_attempt"] is None
        assert data["livemode"] is False
        assert (
            data["lines"]["data"][0]["price"]["billing_scheme"] == "per_unit"
        )

    def test_repr(self):
        obj = fintecture.fintecture_object.FintectureObject("foo", "bar", myparam=5)

        obj["object"] = u"\u4e00boo\u1f00"
        obj.date = datetime.datetime.fromtimestamp(1511136000)

        res = repr(obj)

        if six.PY2:
            res = six.text_type(repr(obj), "utf-8")

        assert u"<FintectureObject \u4e00boo\u1f00" in res
        assert u"id=foo" in res
        assert u'"date": 1511136000' in res

    def test_pickling(self):
        obj = fintecture.fintecture_object.FintectureObject("foo", "bar", myparam=5)

        obj["object"] = "boo"
        obj.refresh_from(
            {
                "fala": "lalala",
                # ensures that empty strings are correctly unpickled in Py3
                "emptystring": "",
            },
            api_key="bar",
            partial=True,
        )

        assert obj.fala == "lalala"

        pickled = pickle.dumps(obj)
        newobj = pickle.loads(pickled)

        assert newobj.id == "foo"
        assert newobj.api_key == "bar"
        assert newobj["object"] == "boo"
        assert newobj.fala == "lalala"
        assert newobj.emptystring == ""

    def test_deletion(self):
        obj = fintecture.fintecture_object.FintectureObject("id", "key")

        obj.coupon = "foo"
        assert obj.coupon == "foo"

        del obj.coupon
        with pytest.raises(AttributeError):
            obj.coupon

        obj.refresh_from({"coupon": "foo"}, api_key="bar", partial=True)
        assert obj.coupon == "foo"

    def test_deletion_metadata(self):
        obj = fintecture.fintecture_object.FintectureObject.construct_from(
            {"metadata": {"key": "value"}}, "myappid"
        )

        assert obj.metadata["key"] == "value"

        del obj.metadata["key"]
        with pytest.raises(KeyError):
            obj.metadata["key"]

    def test_copy(self):
        nested = fintecture.fintecture_object.FintectureObject.construct_from(
            {"value": "bar"}, "myappid"
        )
        obj = fintecture.fintecture_object.FintectureObject.construct_from(
            {"empty": "", "value": "foo", "nested": nested},
            "myappid",
            fintecture_account="myaccount",
        )

        copied = copy(obj)

        assert copied.empty == ""
        assert copied.value == "foo"
        assert copied.nested.value == "bar"

        assert copied.api_key == "mykey"
        assert copied.fintecture_account == "myaccount"

        # Verify that we're not deep copying nested values.
        assert id(nested) == id(copied.nested)

    def test_deepcopy(self):
        nested = fintecture.fintecture_object.FintectureObject.construct_from(
            {"value": "bar"}, "myappid"
        )
        obj = fintecture.fintecture_object.FintectureObject.construct_from(
            {"empty": "", "value": "foo", "nested": nested},
            "myappid",
            fintecture_account="myaccount",
        )

        copied = deepcopy(obj)

        assert copied.empty == ""
        assert copied.value == "foo"
        assert copied.nested.value == "bar"

        assert copied.api_key == "mykey"
        assert copied.fintecture_account == "myaccount"

        # Verify that we're actually deep copying nested values.
        assert id(nested) != id(copied.nested)

    def test_to_dict_recursive(self):
        foo = fintecture.fintecture_object.FintectureObject.construct_from(
            {"value": "foo"}, "myappid"
        )
        bar = fintecture.fintecture_object.FintectureObject.construct_from(
            {"value": "bar"}, "myappid"
        )
        obj = fintecture.fintecture_object.FintectureObject.construct_from(
            {"empty": "", "value": "foobar", "nested": [foo, bar]}, "myappid"
        )

        d = obj.to_dict_recursive()
        assert d == {
            "empty": "",
            "value": "foobar",
            "nested": [{"value": "foo"}, {"value": "bar"}],
        }
        assert not isinstance(
            d["nested"][0], fintecture.fintecture_object.FintectureObject
        )
        assert not isinstance(
            d["nested"][1], fintecture.fintecture_object.FintectureObject
        )

    def test_serialize_empty_string_unsets(self):
        class SerializeToEmptyString(fintecture.fintecture_object.FintectureObject):
            def serialize(self, previous):
                return ""

        nested = SerializeToEmptyString.construct_from(
            {"value": "bar"}, "mykey"
        )
        obj = fintecture.fintecture_object.FintectureObject.construct_from(
            {"nested": nested}, "myappid"
        )

        assert obj.serialize(None) == {"nested": ""}
