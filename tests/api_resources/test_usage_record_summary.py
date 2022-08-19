from __future__ import absolute_import, division, print_function

import fintecture


class TestUsageRecordSummary(object):
    def test_is_listable(self, request_mock):
        usage_record_summaries = (
            fintecture.SubscriptionItem.list_usage_record_summaries("si_123")
        )
        request_mock.assert_requested(
            "get", "/v1/subscription_items/si_123/usage_record_summaries"
        )
        assert isinstance(usage_record_summaries.data, list)
        assert isinstance(
            usage_record_summaries.data[0], fintecture.UsageRecordSummary
        )
