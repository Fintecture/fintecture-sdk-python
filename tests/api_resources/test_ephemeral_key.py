from __future__ import absolute_import, division, print_function

import pytest

import fintecture


class TestEphemeralKey(object):
    def test_is_creatable(self, request_mock):
        resource = fintecture.EphemeralKey.create(
            customer="cus_123", fintecture_version="2017-05-25"
        )
        request_mock.assert_api_version("2017-05-25")
        request_mock.assert_requested(
            "post", "/v1/ephemeral_keys", {"customer": "cus_123"}
        )
        assert isinstance(resource, fintecture.EphemeralKey)

    def test_is_not_creatable_without_an_explicit_api_version(self):
        with pytest.raises(
            ValueError, match="fintecture_version must be specified"
        ):
            fintecture.EphemeralKey.create(customer="cus_123")

    def test_is_deletable(self, request_mock):
        resource = fintecture.EphemeralKey.create(
            customer="cus_123", fintecture_version="2017-05-25"
        )
        resource.delete()
        request_mock.assert_requested(
            "delete", "/v1/ephemeral_keys/%s" % resource.id
        )
        assert isinstance(resource, fintecture.EphemeralKey)

    def test_can_delete(self, request_mock):
        resource = fintecture.EphemeralKey.delete("ephkey_123")
        request_mock.assert_requested(
            "delete", "/v1/ephemeral_keys/ephkey_123"
        )
        assert isinstance(resource, fintecture.EphemeralKey)
