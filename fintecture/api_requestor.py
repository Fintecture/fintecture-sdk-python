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
from fintecture import error, oauth_error, http_client, version, util, six
from fintecture.multipart_data_generator import MultipartDataGenerator
from fintecture.six.moves.urllib.parse import urlparse, urlencode, urlsplit, urlunsplit
from fintecture.fintecture_response import FintectureResponse, FintectureStreamResponse
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
        account=None,
    ):
        self.api_base = api_base or APIRequestor.api_base()

        self.app_id = app_id
        self.app_secret = app_secret
        self.private_key = private_key

        self.api_version = api_version or fintecture.api_version
        self.fintecture_account = account

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
                "Please check that available environment values is one of %r\n" % (fintecture.AVAILABLE_ENVS)
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
        rbody, rcode, rheaders, my_api_key = self.request_raw(
            method.lower(), url, params, headers, is_streaming=False
        )
        resp = self.interpret_response(rbody, rcode, rheaders)
        return resp, my_api_key

    def request_stream(self, method, url, params=None, headers=None):
        stream, rcode, rheaders, my_api_key = self.request_raw(
            method.lower(), url, params, headers, is_streaming=True
        )
        resp = self.interpret_streaming_response(stream, rcode, rheaders)
        return resp, my_api_key

    def handle_error_response(self, rbody, rcode, resp, rheaders):
        try:
            error_data = resp["errors"]
        except (KeyError, TypeError):
            raise error.APIError(
                "Invalid response object from API: %r (HTTP response code "
                "was %d)" % (rbody, rcode),
                rbody,
                rcode,
                resp,
            )

        err = None

        # OAuth errors are a JSON object where `error` is a string. In
        # contrast, in API errors, `error` is a hash with sub-keys. We use
        # this property to distinguish between OAuth and API errors.
        if isinstance(error_data, six.string_types):
            err = self.specific_oauth_error(
                rbody, rcode, resp, rheaders, error_data
            )

        if err is None:
            err = self.specific_api_error(
                rbody, rcode, resp, rheaders, error_data
            )

        raise err

    def specific_api_error(self, rbody, rcode, resp, rheaders, error_data):

        # only raise exception with the first error notified
        if isinstance(error_data, list) and len(error_data) > 0:
            error_data = error_data[0]

        util.log_info(
            "Fintecture API error received",
            error_code=error_data.get("code"),
            error_title=error_data.get("title"),
            error_message=error_data.get("message"),
        )

        # Rate limits were previously coded as 400's with code 'rate_limit'
        if rcode == 429 or (
            rcode == 400 and error_data.get("code") == "rate_limit"
        ):
            return error.RateLimitError(
                error_data.get("message"), rbody, rcode, resp, rheaders
            )
        elif rcode in [400, 404]:
            if error_data.get("type") == "idempotency_error":
                return error.IdempotencyError(
                    error_data.get("message"), rbody, rcode, resp, rheaders
                )
            else:
                return error.InvalidRequestError(
                    error_data.get("message"),
                    error_data.get("param"),
                    error_data.get("code"),
                    rbody,
                    rcode,
                    resp,
                    rheaders,
                )
        elif rcode == 401:
            return error.AuthenticationError(
                error_data.get("message"), rbody, rcode, resp, rheaders
            )
        elif rcode == 402:
            return error.CardError(
                error_data.get("message"),
                error_data.get("param"),
                error_data.get("code"),
                rbody,
                rcode,
                resp,
                rheaders,
            )
        elif rcode == 403:
            return error.PermissionError(
                error_data.get("message"), rbody, rcode, resp, rheaders
            )
        else:
            return error.APIError(
                error_data.get("message"), rbody, rcode, resp, rheaders
            )

    def specific_oauth_error(self, rbody, rcode, resp, rheaders, error_code):
        description = resp.get("error_description", error_code)

        util.log_info(
            "Fintecture OAuth error received",
            error_code=error_code,
            error_description=description,
        )

        args = [error_code, description, rbody, rcode, resp, rheaders]

        if error_code == "invalid_client":
            return oauth_error.InvalidClientError(*args)
        elif error_code == "invalid_grant":
            return oauth_error.InvalidGrantError(*args)
        elif error_code == "invalid_request":
            return oauth_error.InvalidRequestError(*args)
        elif error_code == "invalid_scope":
            return oauth_error.InvalidScopeError(*args)
        elif error_code == "unsupported_grant_type":
            return oauth_error.UnsupportedGrantTypError(*args)
        elif error_code == "unsupported_response_type":
            return oauth_error.UnsupportedResponseTypError(*args)

        return None

    def request_headers(self, app_id, method, url, access_token=None, private_key=None, body=None):
        user_agent = "Fintecture/v1 PythonBindings/%s" % (version.VERSION,)
        if fintecture.app_info:
            user_agent += " " + self.format_app_info(fintecture.app_info)

        # ua = {
        #     "bindings_version": version.VERSION,
        #     "lang": "python",
        #     "publisher": "fintecture",
        #     "httplib": self._client.name,
        # }
        # for attr, func in [
        #     ["lang_version", platform.python_version],
        #     ["platform", platform.platform],
        #     ["uname", lambda: " ".join(platform.uname())],
        # ]:
        #     try:
        #         val = func()
        #     except Exception:
        #         val = "(disabled)"
        #     ua[attr] = val
        # if fintecture.app_info:
        #     ua["application"] = fintecture.app_info

        headers = {
            # "X-Fintecture-Client-User-Agent": json.dumps(ua),
            "User-Agent": user_agent,
            "Accept": "application/json",
        }

        # if self.fintecture_account:
        #     headers["Fintecture-Account"] = self.fintecture_account

        if method == "post":
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            headers.setdefault("Idempotency-Key", str(uuid.uuid4()))

        if self.api_version is not None:
            headers["Fintecture-Version"] = self.api_version

        if app_id:
            headers['app_id'] = app_id

        if access_token:
            headers['Authorization'] = "Bearer {}".format(fintecture.access_token)

        if private_key:
            payload = ''
            if type(body) == 'str':
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
        is_streaming=False,
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
                post_data = json.dumps(params)
            else:
                post_data = encoded_params
        else:
            raise error.APIConnectionError(
                "Unrecognized HTTP method %r.  This may indicate a bug in the "
                "Fintecture bindings.  Please contact contact@fintecture.com for "
                "assistance." % (method,)
            )

        headers = self.request_headers(my_app_id, method, abs_url, fintecture.access_token, my_private_key, post_data)
        if supplied_headers is not None:
            for key, value in six.iteritems(supplied_headers):
                headers[key] = value

        util.log_info("Request to Fintecture api", method=method, path=abs_url)
        util.log_debug(
            "Post details",
            post_data=encoded_params,
            api_version=self.api_version,
        )

        if is_streaming:
            (
                rcontent,
                rcode,
                rheaders,
            ) = self._client.request_stream_with_retries(
                method, abs_url, headers, post_data
            )
        else:
            rcontent, rcode, rheaders = self._client.request_with_retries(
                method, abs_url, headers, post_data
            )

        util.log_info("Fintecture API response", path=abs_url, response_code=rcode)
        util.log_debug("API response body", body=rcontent)

        if "Request-Id" in rheaders:
            request_id = rheaders["Request-Id"]
            util.log_debug(
                "Dashboard link for request",
                link=util.dashboard_link(request_id),
            )

        return rcontent, rcode, rheaders, my_app_id

    def _should_handle_code_as_error(self, rcode):
        return not 200 <= rcode < 300

    def interpret_response(self, rbody, rcode, rheaders):
        try:
            if hasattr(rbody, "decode"):
                rbody = rbody.decode("utf-8")
            resp = FintectureResponse(rbody, rcode, rheaders)
        except Exception as e:
            raise error.APIError(
                "Invalid response body from API: %s "
                "(HTTP response code was %d)" % (rbody, rcode),
                rbody,
                rcode,
                rheaders,
            )
        if self._should_handle_code_as_error(rcode):
            self.handle_error_response(rbody, rcode, resp.data, rheaders)
        return resp

    def interpret_streaming_response(self, stream, rcode, rheaders):
        # Streaming response are handled with minimal processing for the success
        # case (ie. we don't want to read the content). When an error is
        # received, we need to read from the stream and parse the received JSON,
        # treating it like a standard JSON response.
        if self._should_handle_code_as_error(rcode):
            if hasattr(stream, "getvalue"):
                json_content = stream.getvalue()
            elif hasattr(stream, "read"):
                json_content = stream.read()
            else:
                raise NotImplementedError(
                    "HTTP client %s does not return an IOBase object which "
                    "can be consumed when streaming a response."
                )

            return self.interpret_response(json_content, rcode, rheaders)
        else:
            return FintectureStreamResponse(stream, rcode, rheaders)
