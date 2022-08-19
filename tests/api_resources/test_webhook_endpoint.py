from __future__ import absolute_import, division, print_function

import fintecture


TEST_RESOURCE_ID = "we_123"


class TestWebhookEndpoint(object):
    def test_is_listable(self, request_mock):
        resources = fintecture.WebhookEndpoint.list()
        request_mock.assert_requested("get", "/v1/webhook_endpoints")
        assert isinstance(resources.data, list)
        assert isinstance(resources.data[0], fintecture.WebhookEndpoint)

    def test_is_retrievable(self, request_mock):
        resource = fintecture.WebhookEndpoint.retrieve(TEST_RESOURCE_ID)
        request_mock.assert_requested(
            "get", "/v1/webhook_endpoints/%s" % TEST_RESOURCE_ID
        )
        assert isinstance(resource, fintecture.WebhookEndpoint)

    def test_is_creatable(self, request_mock):
        resource = fintecture.WebhookEndpoint.create(
            enabled_events=["charge.succeeded"], url="https://fintecture.com"
        )
        request_mock.assert_requested("post", "/v1/webhook_endpoints")
        assert isinstance(resource, fintecture.WebhookEndpoint)

    def test_is_saveable(self, request_mock):
        resource = fintecture.WebhookEndpoint.retrieve(TEST_RESOURCE_ID)
        resource.enabled_events = ["charge.succeeded"]
        resource.save()
        request_mock.assert_requested(
            "post", "/v1/webhook_endpoints/%s" % TEST_RESOURCE_ID
        )

    def test_is_modifiable(self, request_mock):
        resource = fintecture.WebhookEndpoint.modify(
            TEST_RESOURCE_ID,
            enabled_events=["charge.succeeded"],
            url="https://fintecture.com",
        )
        request_mock.assert_requested(
            "post", "/v1/webhook_endpoints/%s" % TEST_RESOURCE_ID
        )
        assert isinstance(resource, fintecture.WebhookEndpoint)

    def test_is_deletable(self, request_mock):
        resource = fintecture.WebhookEndpoint.retrieve(TEST_RESOURCE_ID)
        resource.delete()
        request_mock.assert_requested(
            "delete", "/v1/webhook_endpoints/%s" % TEST_RESOURCE_ID
        )
        assert resource.deleted is True

    def test_can_delete(self, request_mock):
        resource = fintecture.WebhookEndpoint.delete(TEST_RESOURCE_ID)
        request_mock.assert_requested(
            "delete", "/v1/webhook_endpoints/%s" % TEST_RESOURCE_ID
        )
        assert resource.deleted is True
