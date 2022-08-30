from __future__ import absolute_import, division, print_function

import fintecture


TEST_RESOURCE_ID = "acct_123"
TEST_CAPABILITY_ID = "acap_123"
TEST_EXTERNALACCOUNT_ID = "ba_123"
TEST_PERSON_ID = "person_123"


class TestAis(object):
    def test_is_listable(self, request_mock):
        resources = fintecture.Account.list()
        request_mock.assert_requested("get", "/v1/accounts")
        assert isinstance(resources.data, list)
        assert isinstance(resources.data[0], fintecture.Account)

    def test_is_retrievable(self, request_mock):
        resource = fintecture.Account.retrieve(TEST_RESOURCE_ID)
        request_mock.assert_requested(
            "get", "/v1/accounts/%s" % TEST_RESOURCE_ID
        )
        assert isinstance(resource, fintecture.Account)

    def test_is_creatable(self, request_mock):
        resource = fintecture.Account.create(country="US", type="custom")
        request_mock.assert_requested("post", "/v1/accounts")
        assert isinstance(resource, fintecture.Account)

    def test_is_saveable(self, request_mock):
        account = fintecture.Account.retrieve(TEST_RESOURCE_ID)
        account.metadata["key"] = "value"
        resource = account.save()
        request_mock.assert_requested(
            "post", "/v1/accounts/%s" % TEST_RESOURCE_ID
        )
        assert isinstance(resource, fintecture.Account)
        assert resource is account

    def test_is_saveable_with_individual(self, request_mock):
        individual = fintecture.Person.construct_from(
            {"id": "person_123", "object": "person", "first_name": "Jenny"},
            fintecture.app_id,
        )
        account = fintecture.Account.construct_from(
            {"id": "acct_123", "object": "account", "individual": individual},
            fintecture.app_id,
        )

        account.individual.first_name = "Jane"

        request_mock.stub_request(
            "post",
            "/v1/accounts/%s" % TEST_RESOURCE_ID,
            account.to_dict_recursive(),
        )
        resource = account.save()
        request_mock.assert_requested(
            "post",
            "/v1/accounts/%s" % TEST_RESOURCE_ID,
            {"individual": {"first_name": "Jane"}},
        )
        assert isinstance(resource, fintecture.Account)
        assert resource is account

    def test_is_modifiable(self, request_mock):
        resource = fintecture.Account.modify(
            TEST_RESOURCE_ID, metadata={"key": "value"}
        )
        request_mock.assert_requested(
            "post", "/v1/accounts/%s" % TEST_RESOURCE_ID
        )
        assert isinstance(resource, fintecture.Account)

    def test_is_deletable(self, request_mock):
        resource = fintecture.Account.retrieve(TEST_RESOURCE_ID)
        resource.delete()
        request_mock.assert_requested(
            "delete", "/v1/accounts/%s" % TEST_RESOURCE_ID
        )
        assert resource.deleted is True

    def test_can_delete(self, request_mock):
        resource = fintecture.Account.delete(TEST_RESOURCE_ID)
        request_mock.assert_requested(
            "delete", "/v1/accounts/%s" % TEST_RESOURCE_ID
        )
        assert resource.deleted is True

    def test_can_retrieve_no_id(self, request_mock):
        resource = fintecture.Account.retrieve()
        request_mock.assert_requested("get", "/v1/account")
        assert isinstance(resource, fintecture.Account)

    def test_can_reject(self, request_mock):
        account = fintecture.Account.retrieve(TEST_RESOURCE_ID)
        resource = account.reject(reason="fraud")
        request_mock.assert_requested(
            "post",
            "/v1/accounts/%s/reject" % TEST_RESOURCE_ID,
            {"reason": "fraud"},
        )
        assert isinstance(resource, fintecture.Account)
        assert resource is account

    def test_can_reject_classmethod(self, request_mock):
        resource = fintecture.Account.reject(TEST_RESOURCE_ID, reason="fraud")
        request_mock.assert_requested(
            "post",
            "/v1/accounts/%s/reject" % TEST_RESOURCE_ID,
            {"reason": "fraud"},
        )
        assert isinstance(resource, fintecture.Account)

    def test_is_deauthorizable(self, request_mock):
        account = fintecture.Account.retrieve(TEST_RESOURCE_ID)
        request_mock.stub_request(
            "post", "/oauth/deauthorize", {}
        )
        account.deauthorize()
        request_mock.assert_requested(
            "post",
            "/oauth/deauthorize",
            {},
        )

    def test_can_call_persons(self, request_mock):
        account = fintecture.Account.retrieve(TEST_RESOURCE_ID)
        resources = account.persons()
        request_mock.assert_requested(
            "get", "/v1/accounts/%s/persons" % TEST_RESOURCE_ID
        )
        assert isinstance(resources.data, list)
        assert isinstance(resources.data[0], fintecture.Person)


class TestAccountCapabilities(object):
    def test_is_listable(self, request_mock):
        resources = fintecture.Account.list_capabilities(TEST_RESOURCE_ID)
        request_mock.assert_requested(
            "get", "/v1/accounts/%s/capabilities" % TEST_RESOURCE_ID
        )
        assert isinstance(resources.data, list)
        assert isinstance(resources.data[0], fintecture.Capability)

    def test_is_modifiable(self, request_mock):
        resource = fintecture.Account.modify_capability(
            TEST_RESOURCE_ID, TEST_CAPABILITY_ID, requested=True
        )
        request_mock.assert_requested(
            "post",
            "/v1/accounts/%s/capabilities/%s"
            % (TEST_RESOURCE_ID, TEST_CAPABILITY_ID),
        )
        assert isinstance(resource, fintecture.Capability)

    def test_is_retrievable(self, request_mock):
        resource = fintecture.Account.retrieve_capability(
            TEST_RESOURCE_ID, TEST_CAPABILITY_ID
        )
        request_mock.assert_requested(
            "get",
            "/v1/accounts/%s/capabilities/%s"
            % (TEST_RESOURCE_ID, TEST_CAPABILITY_ID),
        )
        assert isinstance(resource, fintecture.Capability)


class TestAccountExternalAccounts(object):
    def test_is_listable(self, request_mock):
        resources = fintecture.Account.list_external_accounts(TEST_RESOURCE_ID)
        request_mock.assert_requested(
            "get", "/v1/accounts/%s/external_accounts" % TEST_RESOURCE_ID
        )
        assert isinstance(resources.data, list)

    def test_is_retrievable(self, request_mock):
        resource = fintecture.Account.retrieve_external_account(
            TEST_RESOURCE_ID, TEST_EXTERNALACCOUNT_ID
        )
        request_mock.assert_requested(
            "get",
            "/v1/accounts/%s/external_accounts/%s"
            % (TEST_RESOURCE_ID, TEST_EXTERNALACCOUNT_ID),
        )
        assert isinstance(resource, fintecture.BankAccount)

    def test_is_creatable(self, request_mock):
        resource = fintecture.Account.create_external_account(
            TEST_RESOURCE_ID, external_account="btok_123"
        )
        request_mock.assert_requested(
            "post", "/v1/accounts/%s/external_accounts" % TEST_RESOURCE_ID
        )
        assert isinstance(resource, fintecture.BankAccount)

    def test_is_modifiable(self, request_mock):
        resource = fintecture.Account.modify_external_account(
            TEST_RESOURCE_ID, TEST_EXTERNALACCOUNT_ID, metadata={"foo": "bar"}
        )
        request_mock.assert_requested(
            "post",
            "/v1/accounts/%s/external_accounts/%s"
            % (TEST_RESOURCE_ID, TEST_EXTERNALACCOUNT_ID),
        )
        assert isinstance(resource, fintecture.BankAccount)

    def test_is_deletable(self, request_mock):
        resource = fintecture.Account.delete_external_account(
            TEST_RESOURCE_ID, TEST_EXTERNALACCOUNT_ID
        )
        request_mock.assert_requested(
            "delete",
            "/v1/accounts/%s/external_accounts/%s"
            % (TEST_RESOURCE_ID, TEST_EXTERNALACCOUNT_ID),
        )
        assert resource.deleted is True


class TestAccountLoginLinks(object):
    def test_is_creatable(self, request_mock):
        resource = fintecture.Account.create_login_link(TEST_RESOURCE_ID)
        request_mock.assert_requested(
            "post", "/v1/accounts/%s/login_links" % TEST_RESOURCE_ID
        )
        assert isinstance(resource, fintecture.LoginLink)


class TestAccountPersons(object):
    def test_is_creatable(self, request_mock):
        resource = fintecture.Account.create_person(
            TEST_RESOURCE_ID, dob={"day": 1, "month": 1, "year": 1980}
        )
        request_mock.assert_requested(
            "post", "/v1/accounts/%s/persons" % TEST_RESOURCE_ID
        )
        assert isinstance(resource, fintecture.Person)

    def test_is_deletable(self, request_mock):
        resource = fintecture.Account.delete_person(
            TEST_RESOURCE_ID, TEST_PERSON_ID
        )
        request_mock.assert_requested(
            "delete",
            "/v1/accounts/%s/persons/%s" % (TEST_RESOURCE_ID, TEST_PERSON_ID),
        )
        assert resource.deleted is True

    def test_is_listable(self, request_mock):
        resources = fintecture.Account.list_persons(TEST_RESOURCE_ID)
        request_mock.assert_requested(
            "get", "/v1/accounts/%s/persons" % TEST_RESOURCE_ID
        )
        assert isinstance(resources.data, list)
        assert isinstance(resources.data[0], fintecture.Person)

    def test_is_modifiable(self, request_mock):
        resource = fintecture.Account.modify_person(
            TEST_RESOURCE_ID, TEST_PERSON_ID, metadata={"foo": "bar"}
        )
        request_mock.assert_requested(
            "post",
            "/v1/accounts/%s/persons/%s" % (TEST_RESOURCE_ID, TEST_PERSON_ID),
        )
        assert isinstance(resource, fintecture.Person)

    def test_is_retrievable(self, request_mock):
        resource = fintecture.Account.retrieve_person(
            TEST_RESOURCE_ID, TEST_PERSON_ID
        )
        request_mock.assert_requested(
            "get",
            "/v1/accounts/%s/persons/%s" % (TEST_RESOURCE_ID, TEST_PERSON_ID),
        )
        assert isinstance(resource, fintecture.Person)
