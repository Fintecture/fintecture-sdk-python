from __future__ import absolute_import, division, print_function

import fintecture


TEST_RESOURCE_ID = "vs_123"


class TestVerificationReport(object):
    def test_is_listable(self, request_mock):
        resources = fintecture.identity.VerificationReport.list()
        request_mock.assert_requested(
            "get", "/v1/identity/verification_reports"
        )
        assert isinstance(resources.data, list)
        assert isinstance(
            resources.data[0], fintecture.identity.VerificationReport
        )

    def test_is_retrievable(self, request_mock):
        resource = fintecture.identity.VerificationReport.retrieve(
            TEST_RESOURCE_ID
        )
        request_mock.assert_requested(
            "get", "/v1/identity/verification_reports/%s" % TEST_RESOURCE_ID
        )
        assert isinstance(resource, fintecture.identity.VerificationReport)
