from __future__ import absolute_import, division, print_function

import pytest

import fintecture


TEST_SUBSCRIPTION_ITEM_ID = "si_123"


class TestUsageRecord(object):
    def test_is_creatable(self, request_mock):
        resource = fintecture.UsageRecord.create(
            subscription_item=TEST_SUBSCRIPTION_ITEM_ID,
            quantity=5000,
            timestamp=1524182400,
            action="increment",
        )
        request_mock.assert_requested(
            "post",
            "/v1/subscription_items/%s/usage_records"
            % (TEST_SUBSCRIPTION_ITEM_ID),
        )
        assert isinstance(resource, fintecture.UsageRecord)

    def test_raises_when_creating_without_subscription_item(self):
        with pytest.raises(ValueError):
            fintecture.UsageRecord.create(
                quantity=5000, timestamp=1524182400, action="increment"
            )
