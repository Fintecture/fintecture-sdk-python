from __future__ import absolute_import, division, print_function

import atexit
import os
import sys
from distutils.version import StrictVersion

import pytest

import fintecture
from fintecture.six.moves.urllib.request import urlopen
from fintecture.six.moves.urllib.error import HTTPError

from tests.request_mock import RequestMock
from tests.fintecture_mock import FintectureMock

MOCK_MINIMUM_VERSION = "0.109.0"

# Starts fintecture-mock if an OpenAPI spec override is found in `openapi/`, and
# otherwise fall back to `fintecture_MOCK_PORT` or 12111.
if FintectureMock.start():
    MOCK_PORT = FintectureMock.port()
else:
    MOCK_PORT = os.environ.get("FINTECTURE_MOCK_PORT", 12111)


@atexit.register
def stop_fintecture_mock():
    FintectureMock.stop()


def pytest_configure(config):
    if not config.getoption("--nomock"):
        try:
            resp = urlopen("http://localhost:%s/" % MOCK_PORT)
            info = resp.info()
            version = info.get("FINTECTURE_LOGMock-Version")
            if version != "master" and StrictVersion(version) < StrictVersion(
                MOCK_MINIMUM_VERSION
            ):
                sys.exit(
                    "Your version of fintecture-mock (%s) is too old. The minimum "
                    "version to run this test suite is %s. Please "
                    "see its repository for upgrade instructions."
                    % (version, MOCK_MINIMUM_VERSION)
                )

        except HTTPError as e:
            info = e.info()
        except Exception:
            sys.exit(
                "Couldn't reach fintecture-mock at `localhost:%s`. Is "
                "it running? Please see README for setup instructions."
                % MOCK_PORT
            )


def pytest_addoption(parser):
    parser.addoption(
        "--nomock",
        action="store_true",
        help="only run tests that don't need fintecture-mock",
    )


def pytest_runtest_setup(item):
    if "request_mock" in item.fixturenames and item.config.getoption(
        "--nomock"
    ):
        pytest.skip(
            "run fintecture-mock locally and remove --nomock flag to run skipped tests"
        )


@pytest.fixture(autouse=True)
def setup_fintecture():
    orig_attrs = {
        "api_base": fintecture.api_base,
        "api_key": fintecture.api_key,
        "client_id": fintecture.client_id,
        "default_http_client": fintecture.default_http_client,
    }
    http_client = fintecture.http_client.new_default_http_client()
    fintecture.api_base = "http://localhost:%s" % MOCK_PORT
    fintecture.api_key = "sk_test_123"
    fintecture.client_id = "ca_123"
    fintecture.default_http_client = http_client
    yield
    http_client.close()
    fintecture.api_base = orig_attrs["api_base"]
    fintecture.api_key = orig_attrs["api_key"]
    fintecture.client_id = orig_attrs["client_id"]
    fintecture.default_http_client = orig_attrs["default_http_client"]


@pytest.fixture
def request_mock(mocker):
    return RequestMock(mocker)
