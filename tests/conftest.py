from __future__ import absolute_import, division, print_function

import atexit
import os
import sys
from distutils.version import StrictVersion

import pytest

import fintecture
from fintecture.environments import ENVIRONMENT_TEST
from fintecture.six.moves.urllib.request import urlopen
from fintecture.six.moves.urllib.error import HTTPError

from tests.request_mock import RequestMock

MOCK_MINIMUM_VERSION = "0.109.0"


def pytest_configure(config):
    pass


@pytest.fixture(autouse=True)
def setup_fintecture():
    orig_attrs = {
        "env": fintecture.env,
        "app_id": fintecture.app_id,
        "app_secret": fintecture.app_secret,
        "private_key": fintecture.private_key,
        "default_http_client": fintecture.default_http_client,
    }
    http_client = fintecture.http_client.new_default_http_client()
    fintecture.env = ENVIRONMENT_TEST
    fintecture.app_id = "test_123"
    fintecture.app_secret = "test_456"
    fintecture.private_key = "private_key_789"
    fintecture.default_http_client = http_client
    yield
    http_client.close()
    fintecture.env = orig_attrs["env"]
    fintecture.app_id = orig_attrs["app_id"]
    fintecture.app_secret = orig_attrs["app_secret"]
    fintecture.private_key = orig_attrs["private_key"]
    fintecture.default_http_client = orig_attrs["default_http_client"]


@pytest.fixture
def request_mock(mocker):
    return RequestMock(mocker)
