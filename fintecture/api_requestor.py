from __future__ import absolute_import, division, print_function

import calendar
import datetime
import json
import platform
import time
import uuid
import warnings

from collections import OrderedDict
from email import utils as email_utils

import fintecture

from fintecture import crypto
from fintecture import error, http_client, version, util, six
from fintecture.multipart_data_generator import MultipartDataGenerator
from fintecture.six.moves.urllib.parse import urlparse, urlencode, urlsplit, urlunsplit
from fintecture.fintecture_response import FintectureResponse
from fintecture.constants import SIGNED_HEADER_PARAMETER_LIST


def _encode_datetime(dttime):
    if dttime.tzinfo and dttime.tzinfo.utcoffset(dttime) is not None:
        utc_timestamp = calendar.timegm(dttime.utctimetuple())
    else:
        utc_timestamp = time.mktime(dttime.timetuple())

    return int(utc_timestamp)


def _encode_nested_dict(key, data, fmt="%s[%s]"):
    d = OrderedDict()
    for subkey, subvalue in six.iteritems(data):
        d[fmt % (key, subkey)] = subvalue
    return d


def _api_encode(data):
    for key, value in six.iteritems(data):
        key = util.utf8(key)
        if value is None:
            continue
        elif hasattr(value, "fintecture_id"):
            yield (key, value.fintecture_id)
        elif isinstance(value, list) or isinstance(value, tuple):
            for i, sv in enumerate(value):
                if isinstance(sv, dict):
                    subdict = _encode_nested_dict("%s[%d]" % (key, i), sv)
                    for k, v in _api_encode(subdict):
                        yield (k, v)
                else:
                    yield ("%s[%d]" % (key, i), util.utf8(sv))
        elif isinstance(value, dict):
            subdict = _encode_nested_dict(key, value)
            for subkey, subvalue in _api_encode(subdict):
                yield (subkey, subvalue)
        elif isinstance(value, datetime.datetime):
            yield (key, _encode_datetime(value))
        else:
            yield (key, util.utf8(value))


def _build_api_url(url, query):
    scheme, netloc, path, base_query, fragment = urlsplit(url)

    if base_query:
        query = "%s&%s" % (base_query, query)

    return urlunsplit((scheme, netloc, path, query, fragment))


class APIRequestor(object):

    def __init__(
        self,
        app_id=None,
        app_secret=None,
        private_key=None,
        client=None,
        api_base=None,
        api_version=None,
    ):
        self.api_base = api_base or APIRequestor.api_base()

        self.app_id = app_id
        self.app_secret = app_secret
        self.private_key = private_key

        self.api_version = api_version or fintecture.api_version

        self._default_proxy = None

        from fintecture import verify_ssl_certs as verify
        from fintecture import proxy

        if client:
            self._client = client
        elif fintecture.default_http_client:
            self._client = fintecture.default_http_client
            if proxy != self._default_proxy:
                warnings.warn(
                    "fintecture.proxy was updated after sending a "
                    "request - this is a no-op. To use a different proxy, "
                    "set fintecture.default_http_client to a new client "
                    "configured with the proxy."
                )
        else:
            # If the fintecture.default_http_client has not been set by the user
            # yet, we'll set it here. This way, we aren't creating a new
            # HttpClient for every request.
            fintecture.default_http_client = http_client.new_default_http_client(
                verify_ssl_certs=verify, proxy=proxy
            )
            self._client = fintecture.default_http_client
            self._default_proxy = proxy

    @classmethod
    def api_base(cls):
        from fintecture import production_api_base, sandbox_api_base, env

        if env not in fintecture.AVAILABLE_ENVS:
            raise ValueError(
                "Defined environment value is invalid. "
                "Please check that specified environment value is one of %r\n" % fintecture.AVAILABLE_ENVS
            )
        if env == fintecture.ENVIRONMENT_SANDBOX:
            return sandbox_api_base
        elif env == fintecture.ENVIRONMENT_PRODUCTION:
            return production_api_base

        return sandbox_api_base

    @classmethod
    def format_app_info(cls, info):
        str = info["name"]
        if info["version"]:
            str += "/%s" % (info["version"],)
        if info["url"]:
            str += " (%s)" % (info["url"],)
        return str

    def request(self, method, url, params=None, headers=None):
        rbody, rcode, rheaders, url, my_app_id = self.request_raw(
            method.lower(), url, params, headers
        )
        resp = self.interpret_response(url, rbody, rcode, rheaders)
        return resp, my_app_id

    def handle_error_response(self, url, rbody, rcode, resp, rheaders):
        try:
            errors = resp['errors']
        except (KeyError, TypeError):
            raise error.APIError(
                message="Invalid response object from API: %r "
                        "(HTTP response code was %d)" % (rbody, rcode),
                url=url,
                http_body=rbody,
                http_status=rcode,
                headers=rheaders,
                json_body=resp,
            )

        err = self.specific_api_error(
            url, rbody, rcode, resp, rheaders, errors
        )

        if err is not None:
            raise err

        raise error.APIError(
            message="Invalid response object from API: %r "
                    "(HTTP response code was %d)" % (rbody, rcode),
            url=url,
            http_body=rbody,
            http_status=rcode,
            headers=rheaders,
            json_body=resp,
        )

    def specific_api_error(self, url, rbody, rcode, resp, rheaders, error_data):

        status = resp['status']
        code = resp['code']

        util.log_info(
            "Fintecture API error received",
            code=code,
            status=status,
            errors=error_data,
        )

        args = [url, rbody, rcode, resp, rheaders, code]

        if rcode == 400 and code == 'bad_request':
            bad_errors = [
                {
                    'bad_request': 'Invalid parameters or malformed syntax.',
                    'customer_unknown': 'Invalid customer_id. '
                                        'Use a valid customer_id or authenticate to a bank to continue.',
                    'account_unknown': 'Invalid account_id. '
                                       'You must specify an account_id as defined by the /accounts API.',
                    'session_id_invalid_or_expired': 'The session ID used is either expired or invalid.',
                    'invalid_field': 'The value or format of field [field] is incorrect',
                    'mandatory_field_missing': 'The mandatory field is missing: [field] has not been defined.',
                    'invalid_debited_account': 'Invalid debited_account_id. '
                                               'The debited_account_type is set to internal, '
                                               'please use an id provider by the accounts API.',
                }
            ]
            message = "Some general information about the error could be one of [%r]. " \
                      "More details in specific errors." % bad_errors
            args.insert(0, message)
            return error.BadRequestError(*args)

        elif rcode == 401 and code == 'unauthorized':
            authorization_errors = [
                {
                    'invalid_token': 'The token is either invalid or expired.',
                    'invalid_scopes': 'Your app does not have the necessary scopes to access this API.',
                    'invalid_code': 'The authorization code is either wrong or expired.',
                    'invalid_app_id': 'Invalid app_id.',
                    'invalid_app_url': 'Invalid app redirect URL.',
                }
            ]
            message = "Some general information about the error could be one of [%r]. " \
                      "More details in specific errors." % authorization_errors
            args.insert(0, message)
            return error.AuthorizationError(*args)

        elif rcode == 403:
            args.insert(0, 'Some resource could not be accessed.')
            return error.PermissionError(*args)

        elif rcode == 404 and code == 'not_found':
            message = 'The requested resource could not be found. ' \
                      'The requested resource either does not exist or is temporarily down'
            args.insert(0, message)
            return error.NotFoundError(*args)

        elif rcode == 429 and code == 'too_many_requests':
            message = 'The user has sent too many requests in a given amount of time.'
            args.insert(0, message)
            return error.TooManyRequestsError(*args)

        elif rcode == 500 and code == 'internal_server_error':
            message = 'An internal error has occurred. If the error persists, please contact our support.'
            args.insert(0, message)
            return error.InternalServerError(*args)

        elif rcode == 503 and code == 'service_unavailable':
            message = 'The provider is currently unavailable. Please try again later.'
            args.insert(0, message)
            return error.ServiceUnavailableError(*args)

        else:
            args.insert(0, 'An unknown error occur. Please, see error details.')
            return error.APIError(*args)

    def request_headers(self, app_id, method, url, access_token=None, private_key=None, body=None,
                        supplied_headers=None):

        api_version = self.api_version or 'v1'
        user_agent = "Fintecture/%s PythonBindings/%s" % (api_version, version.VERSION,)
        if fintecture.app_info:
            user_agent += " " + self.format_app_info(fintecture.app_info)

        headers = {
            "User-Agent": user_agent,
            "Accept": "application/json",
        }

        if method == "post":
            if supplied_headers is None:
                headers["Content-Type"] = "application/x-www-form-urlencoded"
            elif supplied_headers.get('Content-Type', False):
                headers["Content-Type"] = supplied_headers.get('Content-Type')

        if self.api_version is not None:
            headers["Fintecture-Version"] = self.api_version

        if app_id:
            headers['app_id'] = app_id

        if access_token:
            headers['Authorization'] = "Bearer {}".format(fintecture.access_token)

        if private_key:
            payload = ''
            if isinstance(body, str):
                payload = body
            elif isinstance(body, dict):
                payload = json.dumps(body, separators=(',', ':'))

            parsed_url = urlparse(url)
            path = parsed_url.path
            query = parsed_url.query

            if payload and len(payload) > 0:
                headers['Digest'] = 'SHA-256=' + crypto.hash_base64(payload)

            headers['Date'] = email_utils.format_datetime(datetime.datetime.utcnow())
            headers['X-Date'] = headers['Date']
            headers['X-Request-ID'] = crypto.generate_uuidv4()
            headers['(request-target)'] = method + ' ' + path + ('?' + query if query else '')
            headers['Signature'] = crypto.create_signature_header(
                headers, app_id, private_key, SIGNED_HEADER_PARAMETER_LIST)
            del headers['(request-target)']

        return headers

    def request_raw(
        self,
        method,
        url,
        params=None,
        supplied_headers=None,
    ):
        """
        Mechanism for issuing an API call
        """

        if self.app_id:
            my_app_id = self.app_id
        else:
            from fintecture import app_id
            my_app_id = app_id

        if my_app_id is None:
            raise error.AuthenticationError(
                "No app_id and/or app_secret provided. (HINT: set your app_id and app_secret using "
                '"fintecture.app_id = <APP-ID>" and "fintecture.app_secret = <APP-SECRET>"). '
                "You can find your application values in your Fintecture developer console at "
                "https://console.fintecture.com/developers, after registering your account as a platform. "
                "See https://docs.fintecture.com/ for details, or email contact@fintecture.com "
                "if you have any questions."
            )

        if self.app_secret:
            my_app_secret = self.app_secret
        else:
            from fintecture import app_secret
            my_app_secret = app_secret

        if self.private_key:
            my_private_key = self.private_key
        else:
            from fintecture import private_key
            my_private_key = private_key

        abs_url = "%s%s" % (self.api_base, url)

        encoded_params = urlencode(list(_api_encode(params or {})))

        # Don't use strict form encoding by changing the square bracket control
        # characters back to their literals. This is fine by the server, and
        # makes these parameter strings easier to read.
        encoded_params = encoded_params.replace("%5B", "[").replace("%5D", "]")

        if method == "get" or method == "delete":
            if params:
                abs_url = _build_api_url(abs_url, encoded_params)
            post_data = None
        elif method == "post" or method == "patch":
            if (
                supplied_headers is not None
                and supplied_headers.get("Content-Type")
                == "multipart/form-data"
            ):
                generator = MultipartDataGenerator()
                generator.add_params(params or {})
                post_data = generator.get_post_data()
                supplied_headers[
                    "Content-Type"
                ] = "multipart/form-data; boundary=%s" % (generator.boundary,)
            elif (
                supplied_headers is not None
                and supplied_headers.get("Content-Type")
                == "application/json"
            ):
                post_data = json.dumps(params, separators=(',', ':'))
            else:
                post_data = encoded_params
        else:
            raise error.APIConnectionError(
                "Unrecognized HTTP method %r. This may indicate a bug in the "
                "Fintecture bindings. Please contact contact@fintecture.com for "
                "assistance." % (method,)
            )

        headers = self.request_headers(my_app_id, method, abs_url, fintecture.access_token, my_private_key, post_data)
        if supplied_headers is not None:
            for key, value in six.iteritems(supplied_headers):
                headers[key] = value

        util.log_info("Request to Fintecture API", method=method, path=abs_url)
        util.log_debug(
            "Post details",
            headers=headers,
            post_data=encoded_params,
        )

        rcontent, rcode, rheaders = self._client.request_with_retries(
            method, abs_url, headers, post_data
        )

        util.log_info("Fintecture API response", path=abs_url, response_code=rcode)
        util.log_debug(
            "API response details",
            headers=rheaders,
            body=rcontent,
        )

        return rcontent, rcode, rheaders, url, my_app_id

    def _should_handle_code_as_error(self, rcode):
        return not 200 <= rcode < 300

    def interpret_response(self, url, rbody, rcode, rheaders):
        try:
            if hasattr(rbody, "decode"):
                rbody = rbody.decode("utf-8")
            resp = FintectureResponse(url, rbody, rcode, rheaders)
        except Exception as e:
            raise error.APIError(
                message="Invalid response body from API: %s "
                "(HTTP response code was %d)" % (rbody, rcode),
                url=url,
                http_body=rbody,
                http_status=rcode,
                headers=rheaders,
            )

        if self._should_handle_code_as_error(rcode):
            self.handle_error_response(url, rbody, rcode, resp.data, rheaders)

        return resp
